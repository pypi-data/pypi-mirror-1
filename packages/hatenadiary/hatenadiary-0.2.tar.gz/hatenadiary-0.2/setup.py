#!/usr/bin/env python
# -*- coding: utf-8 -*-

__version__ = '0.2'

#import ez_setup
#ez_setup.use_setuptools()

from setuptools import setup

setup(
    name = "hatenadiary",
    version = __version__,
    py_modules = ['hatenadiary'],
    author='Yoshiori SHOJI',
    author_email='yoshiori@google.com',
    description='A python wrapper around the Hatena Diary AtomPub',
)
