# -*- coding: utf-8 -*-
"""
collective.recipe.libsvm

Licensed under the GPL license, see LICENCE.txt for more details.

$Id: event.py 67630 2006-04-27 00:54:03Z jfroche $
"""
import os
import urllib
import logging
import shutil
import zc.buildout
import sys

DEFAULT_LIBSVM_URL = 'http://www.csie.ntu.edu.tw/~cjlin/cgi-bin/libsvm.cgi?+http://www.csie.ntu.edu.tw/~cjlin/libsvm+tar.gz'
#DEFAULT_LIBSVM_URL = 'file:///tmp/libsvm-2.86.tar.gz'

LIBSVM_SETUP_PY = """
from setuptools import setup, find_packages
import sys, os

version = '0.1'

name='svm'

setup(name=name,
      version=version,
      author="Affinitic",
      author_email="jfroche@affinitic.be",
      description="little egg with libsvm",
      license='ZPL 2.1',
      keywords = "svm",
      url='http://svn.affinitic.be',
      packages=find_packages('src'),
      include_package_data=True,
      package_dir = {'': 'src'},
      namespace_packages=[],
      install_requires=['setuptools'],
      zip_safe=False)
"""


class Recipe(object):

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options
        self.logger = logging.getLogger(self.name)
        options.setdefault('download-url', DEFAULT_LIBSVM_URL)
        options['tmp-storage'] = os.path.join(
            buildout['buildout']['directory'], 'tmp-storage')
        options['location'] = os.path.join(
            buildout['buildout']['parts-directory'],
            self.name)
        options.setdefault(
            'unpack-name',
            'libsvm-2.86')
        options.setdefault('python-headers-directory',
            '/usr/include/python2.4')

    def download(self, whereto):
        """Download tarball into temporary location.
        """
        url = self.options['download-url']
        tarball_name = os.path.basename(url)
        download_file = os.path.join(whereto, tarball_name)
        if not os.path.exists(download_file):
            self.logger.info(
                'Downloading %s to %s', url, download_file)
            urllib.urlretrieve(url, download_file)
        else:
            self.logger.info("Tarball already downloaded.")
        return download_file

    def untar(self, download_file, storage):
        """Untar tarball into temporary location.
        """
        unpack_dir = os.path.join(storage, self.options['unpack-name'])
        if os.path.exists(unpack_dir):
            self.logger.info("Unpack directory (%s) already exists... "
                             "skipping unpack." % unpack_dir)
            return
        self.logger.info("Unpacking tarball")
        os.chdir(storage)
        status = os.system('tar xzf ' + download_file)
        assert status == 0
        assert os.path.exists(unpack_dir)

    def copy(self, storage):
        location = self.options['location']
        if os.path.exists(location):
            self.logger.info('No need to re-install openoffice part')
            return False
        shutil.copytree(os.path.join(storage, 'libsvm-2.86'),
                        location)

    def install(self):
        location = self.options['location']
        if os.path.exists(location):
            return location
        storage = self.options['tmp-storage']
        if not os.path.exists(storage):
            os.mkdir(storage)
        download_file = self.download(storage)
        self.untar(download_file, storage)
        self.copy(storage)
        self.make()
        self.install_libsvm_egg()
        return location

    def make(self):
        self.logger.info("Compile svm")
        location = self.options['location']
        os.chdir(os.path.join(location, 'python'))
        if sys.platform == 'darwin':
            os.environ['LDFLAGS'] = '-framework Python -bundle'
        os.environ['PYTHON_INCLUDEDIR'] = os.path.realpath(
	    self.options['python-headers-directory'])
        status = os.system('make')
        assert status == 0

    def install_libsvm_egg(self):
        self.logger.info("Creating libsvm egg")
        location = self.options['location']
        program_dir = os.path.join(location, 'python')
        fd = open(os.path.join(program_dir, 'setup.py'), 'w')
        fd.write(LIBSVM_SETUP_PY)
        fd.close()
        egg_src_dir = os.path.join(program_dir, 'src')
        if not os.path.isdir(egg_src_dir):
            os.mkdir(egg_src_dir)
        for filename in ['svmc.so', 'svm.py']:
            if not os.path.islink(os.path.join(egg_src_dir, filename)):
                os.symlink(os.path.join(program_dir, filename),
                           os.path.join(egg_src_dir, filename))
        eggDirectory = self.buildout['buildout']['eggs-directory']
        zc.buildout.easy_install.develop(program_dir, eggDirectory)

    def update(self):
        pass
