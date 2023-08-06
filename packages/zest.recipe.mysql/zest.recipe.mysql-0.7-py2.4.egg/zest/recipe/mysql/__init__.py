# -*- coding: utf-8 -*-
"""Recipe mysql"""
import logging
import os
import platform
import setuptools
import shutil
import string
import subprocess
import tempfile
import urllib2
import urlparse
import zc.buildout


class Recipe(object):
    """zc.buildout recipe"""

    def __init__(self, buildout, name, options):
        self.name = name
        self.options = options
        self.buildout = buildout
        self.logger=logging.getLogger(self.name)

        self.mysql_url = options.get("mysql-url", None)
        self.mysql_python_url = options.get("mysql-python-url", None)
        if not self.mysql_url or not self.mysql_python_url:
            self.logger.error(
                "You need to specify the URLs to download MySQL and mysql-python")
            raise zc.buildout.UserError("No download location provided")
        pythonexec = options.get('python', buildout['buildout']['python'])
        self.python = buildout[pythonexec]['executable']

        location = options["location"]=os.path.join(
                buildout["buildout"]["parts-directory"], self.name)
        self.options["source-location"] = os.path.join(location, "source")
        self.options["mysqldb-location"] = os.path.join(location, "mysql-python")
        self.options["eggs-directory"] = buildout['buildout']['eggs-directory']
        self.options["eggs"] = 'MySQL_python'
        self.options["_e"] = self.options["eggs-directory"]
        self.options["binary-location"] = os.path.join(location, "install")
        bindir = buildout["buildout"]["bin-directory"]
        self.options["daemon"] = os.path.join(bindir, "mysqld_safe")

        # Set some default options
        buildout['buildout'].setdefault('download-directory',
            os.path.join(buildout['buildout']['directory'], 'downloads'))

    def install(self):
        """Installer"""
        location=self.options["location"]
        if not os.path.exists(location):
            os.mkdir(location)
        self.download()
        self.compileMySQL()
        self.addScriptWrappers()
        if '10.5' in platform.mac_ver()[0]:
            self.patchForOSXLeopard()
        self.compileMySQLPython()
        self.update_find_links()

        return []

    def download(self):
        options = self.options
        buildout = self.buildout
        download_dir = buildout['buildout']['download-directory']
        for path in (options["source-location"], options["mysqldb-location"]):
            if os.path.exists(path):
                shutil.rmtree(path)
        self.logger.info("Downloading MySQL and mysql-python tarball.")
        if not os.path.isdir(download_dir):
            os.mkdir(download_dir)
        for url, location in ((self.mysql_url, options["source-location"]),
                              (self.mysql_python_url, options["mysqldb-location"])):
            _, _, urlpath, _, _, _ = urlparse.urlparse(url)
            tmp=tempfile.mkdtemp("buildout-"+self.name)
            try:
                fname=os.path.join(download_dir, urlpath.split("/")[-1])
                if not fname.endswith('gz'):
                    # We are downloading from a mirror like this:
                    # http://dev.mysql.com/get/Downloads/MySQL-5.0/mysql-5.0.51a.tar.gz/from/http://mysql.proserve.nl/
                    fname=os.path.join(download_dir, urlpath.split("/")[-6])
                if not os.path.exists(fname):
                    f=open(fname, "wb")
                    try:
                        f.write(urllib2.urlopen(url).read())
                    except:
                        os.remove(fname)
                        raise
                    f.close()
                setuptools.archive_util.unpack_archive(fname, tmp)
                files=os.listdir(tmp)
                shutil.move(os.path.join(tmp, files[0]), location)
            finally:
                shutil.rmtree(tmp)

    def patchForOSXLeopard(self):
        """Patch _mysql.c on OS X Leopard.

        see http://www.davidcramer.net/code/57/mysqldb-on-leopard.html
        """
        #Commenting out uint define
        mysql_c_filename = os.path.join(self.options["mysqldb-location"],
                                        '_mysql.c')
        mysql_c_source = open(mysql_c_filename, 'r').read()
        mysql_c_source = mysql_c_source.splitlines()
        mysql_c_source.remove('#ifndef uint')
        mysql_c_source.remove('#define uint unsigned int')
        mysql_c_source.remove('#endif')
        open(mysql_c_filename, 'w').write(string.join(mysql_c_source, '\n'))

    def compileMySQL(self):
        os.chdir(self.options["source-location"])
        self.logger.info("Compiling MySQL")
        vardir = os.path.join(self.buildout['buildout']['directory'],
                              'var', 'mysql')
        if not os.path.exists(vardir):
            os.makedirs(vardir)
        assert subprocess.call(["./configure",
                                "--prefix=%s" % self.options["binary-location"],
                                "--localstatedir=%s" % vardir]) == 0
        assert subprocess.call(["make", "install"]) == 0

    def compileMySQLPython(self):
        options = self.options
        buildout = self.buildout
        #First make sure MySQLdb finds our freshly install mysql code
        site_cfg_filename = os.path.join(options["mysqldb-location"],
                                         'site.cfg')
        site_cfg_source = open(site_cfg_filename, 'r').read()
        myconfig = 'mysql_config = ' + options["binary-location"] + \
                   '/bin/mysql_config'
        site_cfg_source = site_cfg_source.replace(
                              '#mysql_config = /usr/local/bin/mysql_config',
                              myconfig)
        # Disable Threadsafe
        site_cfg_source = site_cfg_source.replace('threadsafe = True',
                                                  'threadsafe = False')
        open(site_cfg_filename, 'w').write(site_cfg_source)
        # Now we can build and install
        os.chdir(options["mysqldb-location"])
        self.logger.info("Compiling MySQLdb")
        dest = options["eggs-directory"]
        if not os.path.exists(dest):
            os.makedirs(dest)
        environ = os.environ
        environ['PYTHONPATH'] = dest
        assert subprocess.call([self.python, "setup.py", "install",
                                "--install-lib=%s" % dest],
                                env = environ) == 0

    def update_find_links(self):
        dest = self.options["eggs-directory"]
        eggfiles = [f for f in os.listdir(dest) if f.endswith('.egg')]
        find_links = ''
        for eggfile in eggfiles:
            find_links += "\n%s" % (os.path.join(dest, eggfile))
        for k in self.buildout:
            self.logger.info("Adding the MySQL_python egg to 'find-links' of %s" % k)
            original = self.buildout[k].get('find-links', '')
            self.buildout[k]['find-links'] = original + find_links
        
    def addScriptWrappers(self):
        bintarget=self.buildout["buildout"]["bin-directory"]

        dir = os.path.join(self.options["binary-location"], "bin")
        for file in os.listdir(dir):
            self.logger.info("Adding script wrapper for %s" % file)
            target=os.path.join(bintarget, file)
            f=open(target, "wt")
            print >>f, "#!/bin/sh"
            if file == 'mysqld_safe':
                print >>f, 'exec %s &' % os.path.join(dir, file)
            else:
                print >>f, 'exec %s "$@"' % os.path.join(dir, file)

            f.close()
            os.chmod(target, 0755)
        # exec mysql_install_db
        self.logger.info("Creating mysql database for access tables")
        assert subprocess.call([os.path.join(bintarget, "mysql_install_db")]) == 0
        self.logger.info("Stopping mysqld_safe if any are running")
        # TODO
        self.logger.info("Starting mysqld_safe")
        pid = subprocess.Popen(self.options['daemon']).pid
        self.logger.info("Started mysqld_safe with pid %r" % pid)

    def update(self):
        """Updater"""
        self.update_find_links()


class DatabaseRecipe:
    """docstring for DatabaseRecipe"""

    def __init__(self, buildout, name, options):
        self.name = name
        self.options = options
        self.buildout = buildout
        self.logger = logging.getLogger(self.name)
        self.db2 = self.options.get('db', '')
        self.user = self.options.get('user', 'root')
        self.import_file = self.options.get('import-file', '')
        if self.db == '':
            self.logger.error(
                "You need to specify the URLs to download MySQL and mysql-python")
            raise zc.buildout.UserError("No database name provided,"
                                        " please specify a db = mydatabase")

    def install(self):
        #create the database
        bindir=self.buildout["buildout"]["bin-directory"]
        subprocess.call([bindir, 'mysql', '-u %s' % self.user, '<', 'create', 'database', self.db])

    def update(self):
        pass
