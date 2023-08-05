#!/usr/bin/env python

try:
    from setuptools import setup, find_packages
    setuptools_extras = dict(
        packages=find_packages(),
        install_requires='4Suite-XML>=1.0rc4')

except ImportError:
    from distutils.core import setup
    setuptools_extras = {}

setup(name = "wsgixml",
      version = "0.1",
      description='WSGI middleware modules for XML processing',
      author='Uche Ogbuji',
      author_email='uche@ogbuji.net',
      url='http://uche.ogbuji.net/tech/4suite/wsgixml',
      **setuptools_extras)


