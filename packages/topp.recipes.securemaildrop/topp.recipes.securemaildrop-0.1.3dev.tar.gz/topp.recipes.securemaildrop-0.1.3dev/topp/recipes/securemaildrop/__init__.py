## -*- coding: utf-8 -*-

# based on infrae.maildrophost, (c) Infrae 2007

import os, shutil, tempfile, urllib2, urlparse
import zc.buildout, zc.recipe.egg
import setuptools

class Recipe:

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options
        self.location = os.path.join(
            self.buildout['buildout']['parts-directory'], self.name)
        self.product_location = os.path.join(self.location, 'SecureMaildropHost')
        self.urls = options['urls']
        self.egg = zc.recipe.egg.Egg(buildout, options['recipe'], options)
        self.mail_dir = self.options.get('mail-dir',
                                         os.path.sep.join(('var', 'maildrop',)))
        self.mail_dir = os.path.join(self.buildout['buildout']['directory'],
                                     self.mail_dir)

    def install(self):
        """
        Download and install the MaildropHost and SecureMaildropHost
        Zope products
        """
        download_dir = self.buildout['buildout']['download-directory']

        if not os.path.isdir(download_dir):
            os.mkdir(download_dir)

        if not os.path.isdir(self.location):
            os.mkdir(self.location)
            
        tmp = tempfile.mkdtemp('buildout-'+self.name)
        try:
            for url in self.urls.split():
                _, _, urlpath, _, _, _ = urlparse.urlparse(url)
                fname = os.path.join(download_dir, urlpath.split('/')[-1])
                if not os.path.exists(fname):
                    f = open(fname, 'wb')
                    try:
                        f.write(urllib2.urlopen(self.url).read())
                    except:
                        os.remove(fname)
                        raise zc.buildout.UserError(
                            "Failed to download URL %s: %s" % (url, str(e)))
                    f.close()

                setuptools.archive_util.unpack_archive(fname, tmp)
                files = os.listdir(tmp)
                shutil.move(os.path.join(tmp, files[0]), self.product_location)
        finally:
            shutil.rmtree(tmp)


        return self.update()

    def _build_config(self):
        """
        Create the config file for the maildrop server ;
        Create directory used by the maildrop server.
        """
        
        if not os.path.exists(self.mail_dir):
            os.makedirs(self.mail_dir)

        config_option = dict(smtp_host=self.options.get('smtp_host', 'localhost'),
                             smtp_port=self.options.get('smtp_port', '25'),
                             maildrop_dir=self.mail_dir,
                             executable=self.buildout['buildout']['executable'])

        config_filename = os.path.join(self.product_location, 'config.py')
        config = open(config_filename, 'wb')
        config.write(maildrop_config_template % config_option)

                                       


    def _build_script(self):
        """
        Create the startup script in the bin directory.
        """

        requirements, ws = self.egg.working_set(['topp.recipes.securemaildrop'])

        config = dict(base=self.product_location,
                      pidfile=os.path.join(self.mail_dir, 'maildrop.pid'))

        zc.buildout.easy_install.scripts(
            [(self.name, 'topp.recipes.securemaildrop.ctl', 'main')],
            ws, self.options['executable'], self.options['bin-directory'],
            arguments=('%r, sys.argv[1:]' % config)
            )


    def update(self):
        """
        Update the maildrophost server
        """

        try:
            self._build_config()
            self._build_script()
        except:
            shutil.rmtree(self.location)
            raise

        return self.location





maildrop_config_template="""
PYTHON="%(executable)s"
MAILDROP_HOME="%(maildrop_dir)s"
MAILDROP_VAR="%(maildrop_dir)s"

SMTP_HOST="%(smtp_host)s"
SMTP_PORT=%(smtp_port)s

MAILDROP_INTERVAL=120
DEBUG=0
DEBUG_RECEIVER=""

MAILDROP_BATCH=0
MAILDROP_TLS=0

MAILDROP_LOGIN=""
MAILDROP_PASSWORD=""

WAIT_INTERVAL=0.0
ADD_MESSAGEID=0
"""
