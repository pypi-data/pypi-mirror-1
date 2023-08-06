#!/usr/bin/env python
# encoding: utf-8
"""
setup.py

Created by Craig Sawyer on 2010-01-14.
Copyright (c) 2009, 2010 Craig Sawyer (csawyer@yumaed.org). All rights reserved. see LICENSE.
"""


from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages
setup(
    name = "cifit",
    version = "0.3",
    packages = find_packages(),
    entry_points = {
        'console_scripts': [
            'cifit = cifit:main'
        ]
    },
    author = 'Craig Sawyer',
    author_email = 'csawyer@yumaed.org',
    description = 'Lightweight configuration management toolkit which you write in python',
    license = "GPLv2",
    keywords = "config, system",
    long_description = open('README').read()
    
)


def main():
    pass


if __name__ == '__main__':
    main()

