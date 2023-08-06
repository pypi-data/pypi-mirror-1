#!/usr/bin/env python
# encoding: utf-8
"""
test_files.py

Created by Craig Sawyer on 2010-01-14.
Copyright (c) 2010 YUHSD #70. All rights reserved.
"""

import nose
import files

def test_run():
    assert files.run('head -1 test_files.py') == (0, ['#!/usr/bin/env python'])

    
if __name__ == '__main__':
    nose.run()