#!/usr/bin/env python
# encoding: utf-8
"""
setup.py

Created by Tara Sawyer on 2010-01-15.
Copyright (c) 2010 __MyCompanyName__. All rights reserved.
"""


from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages
setup(
    name = "cifit",
    version = "0.2",
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
    long_description = """
    cifit is a lightweight configuration management toolkit, it patterns itself off of cfengine 
    a little bit (it has classes), borrows from bcfg2, but the language to manage your
    configurations is python.
    """
    
)


def main():
    pass


if __name__ == '__main__':
    main()

