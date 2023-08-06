#!/usr/bin/env python

from distutils.core import setup

setup(name='featurelist',
      version='0.1.2',
      description='Submit and query feature requests from featurelist.org',
      author='Matthew from featurelist.org',
      author_email='support@featurelist.org',
      packages=['featurelist'],
      py_modules = ['sitecustomize'],
      url='http://featurelist.org',
     )