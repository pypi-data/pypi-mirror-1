#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup
from mosaic import __version__ as mosaic_version
from mosaic import __author__ as mosaic_author

setup(name='Mosaic',
      version=mosaic_version,
      description='Mosaic poster composer',
      author=mosaic_author,
      author_email='gthomas@fw.hu',
      py_modules=['mosaic'])
