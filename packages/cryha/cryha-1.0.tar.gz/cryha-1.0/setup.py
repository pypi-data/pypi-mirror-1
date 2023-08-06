#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import setuptools

NAME = 'cryha'
URL = 'http://bitbucket.org/ares/cryha/'
INSTALL_REQUIRES = ['python-mcrypt']  # python-mhash

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
      keywords=('security cryptography crypto symmetric hash database'),
      license='Apache License, Version 2.0',
      classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Environment :: Web Environment',
            'Environment :: Other Environment',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: Apache Software License',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Topic :: Database',
            'Topic :: Security :: Cryptography',
      ],
      platforms=['any']
)
