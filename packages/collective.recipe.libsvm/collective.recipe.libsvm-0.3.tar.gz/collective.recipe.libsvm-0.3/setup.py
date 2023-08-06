from setuptools import setup, find_packages
import os

name = "collective.recipe.libsvm"
version = '0.3'

setup(name=name,
      version=version,
      description="Recipe to compile libsvm with python in a buildout",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join('collective', 'recipe',
                                         'libsvm', 'README.txt')).read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python",
        "Topic :: System :: Installation/Setup",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Framework :: Buildout"],
      keywords='',
      author='Jean-Francois Roche',
      author_email='jfroche@affinitic.be',
      url='https://svn.plone.org/svn/collective/buildout/collective.recipe.libsvm',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.recipe'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'zc.buildout'],
      entry_points = {'zc.buildout': ['default = %s.recipe:Recipe' % name]},
      )
