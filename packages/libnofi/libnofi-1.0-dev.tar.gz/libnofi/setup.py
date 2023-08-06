#!/usr/bin/python
# -*- coding: utf-8 -*-

from distutils.core import setup
import libnofi

setup(name = 'libnofi',
        version = '1.0-dev',
        description = libnofi.__description__,
        author=libnofi.__author__,
        url='http://notefinder.googlecode.com',
        py_modules=['libnofi'],
       )
