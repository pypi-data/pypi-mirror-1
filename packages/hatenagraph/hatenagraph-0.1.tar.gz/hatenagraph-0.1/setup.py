#!/opt/local/bin/python2.5
# -*- coding: utf-8 -*-

__version__ = '0.1'

#import ez_setup
#ez_setup.use_setuptools()

from setuptools import setup

setup(
  name = "hatenagraph",
  version = __version__,
  py_modules = ['hatenagraph'],
  author='Yoshiori SHOJI',
  author_email='yoshiori@google.com',
  description='A python wrapper around the Hatena Graph API',
  install_requires = ['pyYAML'],
)
