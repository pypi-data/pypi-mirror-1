#!/usr/bin/env python
# encoding: utf-8
"""
test_procs.py

Created by Tara Sawyer on 2010-01-14.
Copyright (c) 2010 __MyCompanyName__. All rights reserved.
"""

import nose
import procs

def test_isRunning():
    assert procs.isRunning('init')

if __name__ == '__main__':
    nose.run()

