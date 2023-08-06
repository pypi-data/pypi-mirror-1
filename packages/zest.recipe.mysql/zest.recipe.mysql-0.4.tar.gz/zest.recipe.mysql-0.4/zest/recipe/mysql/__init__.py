# -*- coding: utf-8 -*-
"""Recipe mysql"""
import logging
import os
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

        location=options["location"]=os.path.join(
                buildout["buildout"]["parts-directory"], self.name)
        self.options["source-location"]=os.path.join(location, "source")
        self.options["mysqldb-location"]=os.path.join(location, "mysql-python")
        self.options["binary-location"]=os.path.join(location, "install")
        self.options["daemon"]=os.path.join(options["binary-location"],
                                       "mysqld_safe")
        self.options["leopard-patch"]=self.options.get("leopard-patch", 'no')

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
        if self.options["leopard-patch"] == 'yes':
            self.patchForOSXLeopard()
        self.compileMySQLPython()

        return []

    def update(self):
        """Updater"""
        pass

    def download(self):
        download_dir=self.buildout['buildout']['download-directory']
        for path in (self.options["source-location"], self.options["mysqldb-location"]):
            if os.path.exists(path):
                shutil.rmtree(path)
        self.logger.info("Downloading MySQL and mysql-python tarball.")
        if not os.path.isdir(download_dir):
            os.mkdir(download_dir)
        for url, location in ((self.mysql_url, self.options["source-location"]),
                              (self.mysql_python_url, self.options["mysqldb-location"])):
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

        # Disable Threadsafe
        site_cfg_filename = os.path.join(self.options["mysqldb-location"],
                                         'site.cfg')
        site_cfg_source = open(site_cfg_filename, 'r').read()
        site_cfg_source = site_cfg_source.replace('threadsafe = True',
                                                  'threadsafe = False')
        open(site_cfg_filename, 'w').write(site_cfg_source)

    def compileMySQL(self):
        os.chdir(self.options["source-location"])
        self.logger.info("Compiling MySQL")
        assert subprocess.call(["./configure", "--prefix=" + \
                               self.options["binary-location"]]) == 0
        assert subprocess.call(["make", "install"]) == 0

    def compileMySQLPython(self):
        #First make sure MySQLdb finds our freshly install mysql code
        site_cfg_filename = os.path.join(self.options["mysqldb-location"],
                                         'site.cfg')
        site_cfg_source = open(site_cfg_filename, 'r').read()
        myconfig = 'mysql_config = ' + self.options["binary-location"] + \
                   '/bin/mysql_config'
        site_cfg_source = site_cfg_source.replace(
                              '#mysql_config = /usr/local/bin/mysql_config',
                              myconfig)
        open(site_cfg_filename, 'w').write(site_cfg_source)
        # Now we can build and install
        os.chdir(self.options["mysqldb-location"])
        self.logger.info("Compiling MySQLdb")
        assert subprocess.call(["python", "setup.py", "build"]) == 0
        assert subprocess.call(["sudo", "python", "setup.py", "install"]) == 0

    def addScriptWrappers(self):
        bintarget=self.buildout["buildout"]["bin-directory"]

        dir=os.path.join(self.options["binary-location"], "bin")
        for file in os.listdir(dir):
            self.logger.info("Adding script wrapper for %s" % file)
            target=os.path.join(bintarget, file)
            f=open(target, "wt")
            print >>f, "#!/bin/sh"
            print >>f, 'exec %s "$@"' % os.path.join(dir, file)
            f.close()
            os.chmod(target, 0755)
        # exec mysql_admin_database


class DatabaseRecipe:
    """docstring for DatabaseRecipe"""

    def __init__(self, buildout, name, options):
        self.name=name
        self.options=options
        self.buildout=buildout
        self.logger=logging.getLogger(self.name)

    def install(self):
        pass

    def update(self):
        pass
