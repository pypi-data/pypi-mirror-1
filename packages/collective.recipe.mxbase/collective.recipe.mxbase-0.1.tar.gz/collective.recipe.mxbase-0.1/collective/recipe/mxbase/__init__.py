# Download and install mx.Base, plus it's license file

import logging
import os
import shutil
import sys
import tempfile
import urllib2
import urlparse

import setuptools.archive_util
import zc.buildout

MXBASE_URL = 'http://downloads.egenix.com/python/egenix-mx-base-3.0.0.zip'
SETUP_PY = '''from setuptools import setup, find_packages

setup(
    name = "egenix-mx-base",
    packages = find_packages('.'),
    zip_safe = False,)
'''
def system(c):
    if os.system(c):
        raise SystemError('Failed', c)

class Recipe(object):
    def __init__(self, buildout, name, options):
        self.logger = logging.getLogger(name)
        self.buildout = buildout
        self.name = name
        self.options = options
        options['location'] = os.path.join(
            buildout['buildout']['parts-directory'], self.name)
        buildout['buildout'].setdefault(
            'download-directory',
            os.path.join(buildout['buildout']['directory'], 'downloads'))

    def install(self):
        location = self.options['location']
        if not os.path.exists(location):
            os.mkdir(location)
        self._install_mxbase(location)
        self._create_setup_py(location)
        self._install_egg(location)
        return [location]

    def update(self):
        pass

    def _create_setup_py(self, location):
        fd = open(os.path.join(location, 'setup.py'), 'w')
        fd.write(SETUP_PY)
        fd.close()

    def _install_egg(self, location):
        eggDirectory = self.buildout['buildout']['eggs-directory']
        zc.buildout.easy_install.develop(location, eggDirectory)

    def _install_mxbase(self, location):
        fname = self._download(MXBASE_URL)

        tmp = tempfile.mkdtemp('buildout-' + self.name)
        dirname = os.path.splitext(os.path.basename(fname))[0]
        package = os.path.join(tmp, dirname)
        here = os.getcwd()
        try:
            self.logger.debug('Extracting mx.Base archive')
            setuptools.archive_util.unpack_archive(fname, tmp)
            os.chdir(package)
            self.logger.debug('Installing mx.BASE into %s', location)
            system('"%s" setup.py -q install'
                   ' --install-purelib="%s" --install-platlib="%s"' % (
                        sys.executable, location, location))
        finally:
            os.chdir(here)
            shutil.rmtree(tmp)

    def _download(self, url):
        download_dir = self.buildout['buildout']['download-directory']
        if not os.path.isdir(download_dir):
            os.mkdir(download_dir)
            self.options.created(download_dir)
        urlpath = urlparse.urlparse(url)[2]
        fname = os.path.join(download_dir, urlpath.split('/')[-1])
        if not os.path.exists(fname):
            self.logger.info('Downloading ' + url)
            f = open(fname, 'wb')
            try:
                f.write(urllib2.urlopen(url).read())
            except Exception, e:
                os.remove(fname)
                raise zc.buildout.UserError(
                    "Failed to download URL %s: %s" % (url, str(e)))
            f.close()
        return fname
