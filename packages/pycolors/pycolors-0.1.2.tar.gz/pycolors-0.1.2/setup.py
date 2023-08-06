#!/usr/bin/env python

import warnings
warnings.filterwarnings('ignore')

from setuptools import setup
import colors

setup(
    name='pycolors',
    version=colors.__version__,
    license=colors.__license__,
    description=colors.__description__,
    long_description=colors.__doc__,
    author=colors.__author__,
    author_email=colors.__email__,
    url=colors.__url__,
    py_modules=['colors'],
    platforms='any',
    classifiers=[
        "Programming Language :: Python",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: BSD License",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],

)
