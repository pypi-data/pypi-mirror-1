#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='pyscanning',
      version='0.2.1',
      description='A scanner wrapper for sane and twain.',
      author='Sergio Campos',
      author_email='seocam@seocam.net',
      url='http://code.google.com/p/pyscanning',
      packages=find_packages(),
      package_data={'': ['*.tiff']},
      install_requires=[],
     )

