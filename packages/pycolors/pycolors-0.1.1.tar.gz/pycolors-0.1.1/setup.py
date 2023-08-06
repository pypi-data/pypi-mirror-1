#!/usr/bin/env python

import warnings
warnings.filterwarnings('ignore')

from distutils.core import setup
import colors

setup(
    name='pycolors',
    version=colors.__version__,
    license=colors.__license__,
    description=colors.__description__,
    author=colors.__author__,
    author_email=colors.__email__,
    url=colors.__url__,
    py_modules=['colors']
)
