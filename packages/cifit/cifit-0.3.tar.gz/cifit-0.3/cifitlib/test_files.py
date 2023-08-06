#!/usr/bin/env python
# encoding: utf-8
"""
test_files.py

Created by Craig Sawyer on 2010-01-14.
Copyright (c) 2009, 2010 Craig Sawyer (csawyer@yumaed.org). All rights reserved. see LICENSE.
"""

import nose
import files

def test_run():
	f = __file__
	if f[-3:] == '.pyc':
		f = f[:-1]
	assert files.run('head -1 %s' % f) == (0, ['#!/usr/bin/env python'])

    
if __name__ == '__main__':
	nose.run()
