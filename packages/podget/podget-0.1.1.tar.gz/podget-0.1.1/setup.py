#!/usr/bin/env python

import warnings
warnings.filterwarnings('ignore')

from distutils.core import setup
import podget

setup(
    name='podget',
    version=podget.__version__,
    license=podget.__license__,
    description=podget.__description__,
    author=podget.__author__,
    author_email=podget.__email__,
    url=podget.__url__,
    py_modules=['podget'],
    scripts=['podget']
)
