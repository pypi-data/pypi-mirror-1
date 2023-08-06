#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import setuptools

NAME = 'repoze.what.plugins.redis'
URL = 'http://bitbucket.org/ares/repozewhatpluginsredis/'
INSTALL_REQUIRES = ['repoze.what >= 1.0.8']  # redis

# ====
PACKAGE_DIR = 'lib'
PACKAGES = setuptools.find_packages(PACKAGE_DIR)

# Gets documentation on Readme file.
_readme = open('README', 'r')
_readme.readline()  # Skips the first line.
_package = PACKAGES[-1].replace('.', os.path.sep)  # The package path.
_docstring = os.path.join(PACKAGE_DIR, _package, '__init__.py')

README = _readme.read()
DESCRIPTION = open(_docstring).readline().rstrip().strip('"').rstrip('.')
VERSION = open(os.path.join('doc', 'VERSION')).readline().rstrip()
# ====

setuptools.setup(
      package_dir={'': PACKAGE_DIR},
      packages=PACKAGES,
      namespace_packages = ['repoze', 'repoze.what', 'repoze.what.plugins'],

      install_requires=INSTALL_REQUIRES,
      tests_require=['nose', 'coverage'] + INSTALL_REQUIRES,

      include_package_data=True,
      test_suite='nose.collector',
      zip_safe=False,

      # Metadata for upload to PyPI.
      name=NAME,
      version=VERSION,
      author='Jonas Melian',
      author_email='devel@jonasmelian.com',
      description=DESCRIPTION,
      long_description=README,
      url=URL,
      keywords=('web application server wsgi authorization redis repoze'),
      license='Apache License, Version 2.0',
      classifiers=[
            'Development Status :: 4 - Beta',
            #'Development Status :: 5 - Production/Stable',
            'Environment :: Web Environment',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: Apache Software License',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Topic :: Database',
            'Topic :: Internet :: WWW/HTTP :: WSGI',
            'Topic :: Security',
      ],
      platforms=['any']
)
