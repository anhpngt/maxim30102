#!/usr/bin/env python3
# encoding: utf-8
from distutils.core import setup, Extension

maxim_module = Extension('maxim', sources = ['maxim.c'])

setup(name='maxim',
      version='0.0.0',
      description='Maxim Algorithms',
      ext_modules=[maxim_module])