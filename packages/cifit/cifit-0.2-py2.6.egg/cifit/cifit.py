#!/usr/bin/env python
# encoding: utf-8
"""
cifit.py

Created by Craig Sawyer on 2010-01-14.
Copyright (c) 2010 YUHSD #70. All rights reserved.
"""

import os
import sys
import logging
import files
import classes
import procs
import pkgs

logging.basicConfig(level=logging.DEBUG,filename='/var/log/cifit.log',filemode='a')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter("%(name)s:%(levelname)s %(message)s")
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

log = logging.getLogger('cifit')

def include(filename):
    return main(filename)

def main(filename=sys.argv[1]):
    filename = files.getFilename(filename)
    dirname = os.path.dirname(filename)
    os.chdir(dirname)
    pkg = pkgs.PkgBase()
    if classes.classes.has_key('DISTRIB_ID'):
        #log.debug('lsb machine:%s' % classes.classes.DISTRIB_ID)
        if classes.classes.DISTRIB_ID in ('Ubuntu','Debian'):
            pkg = pkgs.PkgAPT()
	#Export other package tools from pkgs file.
	pkg.installPythonEgg = pkgs.installPythonEgg

    globs = {
        'files':globals()['files'],
        'procs':globals()['procs'],
        'classes':globals()['classes'],
        'include':include,
		'pkg':pkg,
		'pear':pkgs.pearPKG()
    }
    classes.classes['log'] = log
    classes.classes['dirname'] = dirname
    log.info('loading:%s' % filename)
    execfile(filename,globs,classes.classes)



if __name__ == '__main__':
	main(sys.argv[1])
    #main('../etc/main.py')
