#!/usr/bin/env python
# encoding: utf-8
"""
setup.py

Created by Travis Jeffery on 2008-12-08.
Copyright (c) 2008 . All rights reserved.
"""

from setuptools import setup, find_packages
setup(
    name = "LocalGrowl",
    version = "0.2",
    packages = find_packages(),
    install_requires = ['docutils>=0.3'],
    author = "Travis Jeffery",
    author_email = "t.jeffery@utoronto.ca",
    description = "Python implemenation of Growl notifications.",
    license = "GPL",
    keywords = "growl python localhost local",
    url = "http://pypi.python.org/pypi/LocalGrowl",   # project home page, if any
)
