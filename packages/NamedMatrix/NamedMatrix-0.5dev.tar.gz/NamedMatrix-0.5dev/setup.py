#!/usr/bin/env python
# encoding: utf-8
"""
setup.py

Created by Nicholas Tatonetti on 2009-12-16.
Copyright (c) 2009 Stanford University. All rights reserved.
"""

from ez_setup import use_setuptools
use_setuptools()
from setuptools import find_packages, Extension
from numpy.distutils.core import setup

maxdot = Extension('maxdot', sources=['namedmatrix/maxdotmodule.c'])

setup(name="NamedMatrix",
    version="0.5dev",
    description="NamedMatrix, a numpy matrix wrapper class.",
    long_description="""
    NamedMatrix
    A numpy matrix wrapper class.
    """,
    author="Nicholas P. Tatonetti & Guy Haskin Fernald",
    author_email="nick.tatonetti@stanford.edu & guyhf@stanford.edu",
    packages=find_packages(exclude='tests'),
    url="http://www-helix.stanford.edu",
    install_requires=['numpy>1.0.0'],
    ext_modules = [maxdot])

