#!/usr/bin/env python
# encoding: utf-8
"""
pkgs.py

Created by Craig Sawyer on 2010-01-16.
Copyright (c) 2010 YUHSD #70. All rights reserved.
"""

import sys
import re
import os
from files import run
from classes import classes, Storage
import logging

log = logging.getLogger('cifit.files')

from setuptools.command import easy_install


def installPythonEgg(package):
	"""handle installing python egg"""
	try:
		exec("import %s" % package)
	except ImportError:
		try:
			ret = easy_install.main(["-U",package])
			log.info('installPythonEgg returning:%s' % ret)
		except:
			log.critical('problem installing pythonEgg:%s' % package)
			import traceback
			msg = traceback.format_exc()
			log.critical("%s" % (msg))
			return msg



class PkgBase(object):
	def __init__(self):
		self.pkgs = {}
		self.getPackages = self.Unimplemented
		self.installPackage = self.Unimplemented
		self.removePackage = self.Unimplemented
		self.isInstalled = self.Unimplemented

	def Unimplemented(self,*args):
		log.error('Not Implemented')
		return

	def isInstalled(self,name):
		if not self.pkgs:
			self.getPackages()
		namere = re.compile(name,re.IGNORECASE)
		for k,v in self.pkgs.items():
			match = re.search(namere,k)
			if match:
				return k
		return False

class PkgAPT(PkgBase):
	def __init__(self):
		self.pkgs = {}

	def getPackages(self):
		'''get list of packages'''
		ret,out = run('/usr/bin/dpkg -l')
		name_regex = re.compile(r"ii\s+([\S*]*)\s+(\S*)")
		#version_regex = re.compile(r"\s+([0-9a-zA-Z\.\+\:~-]*)")
		for line in out:
			match = re.search(name_regex,line)
			if match:
				name = match.group(1)
				version = match.group(2)
				#log.info("name:version %s:%s" % (name,version))
				self.pkgs[name] = version
			#match = re.search(version_regex,line)
			#if match:
			#	log.info("version: %s" % match.group())
		return self.pkgs

	def installPackage(self,pkgname):
		"""install a package, if it's already installed, return None."""
		if self.isInstalled(pkgname):
			log.debug("%s already installed" % pkgname)
			return None
		else:
			run("DEBIAN_FRONTED=noninteractive /usr/bin/apt-get --yes install %s" % (pkgname))
			return True

	def removePackage(self,pkgname):
		run("DEBIAN_FRONTEND=noninteractive /usr/bin/apt-get --yes remove %s" % (pkgname))

	def updatePackages(self):
		run("DEBIAN_FRONTEND=noninteractive /usr/bin/apt-get update")

	def upgradePackages(self):
		run("DEBIAN_FRONTEND=noninteractive /usr/bin/apt-get upgrade")

class pearPKG(PkgBase):
	"""Manage PEAR (php packages)"""
	def __init__(self):
		self.pkgs = {}

	def getPackages(self):
		ret,out = run('pear list')
		pkg_re = r"^(\w*)\s+(\S*)"
		pkg_re = re.compile(pkg_re,re.IGNORECASE)
		for line in out:
			match = re.search(pkg_re,line)
			if match:
				name = match.group(1)
				version = match.group(2)
				log.info("name:version %s:%s" % (name,version))
				self.pkgs[name] = version
		return self.pkgs


	def installPackage(self,package):
		"""install pear package your repsonisbility to have pear exist."""
		if self.isInstalled(package):
			return True
		ret,out = run("pear install %s" % package)
		for line in out:
			if 'install ok' in line:
				return True
			if 'install failed' in line:
				log.error('problem installing %s see log' % package)
				return False
		log.error('is pear installed and in your path?: %s' % package)
		return False

	def removePackage(self,package):
		"""remove a pear package"""
		ret,out = run("pear uninstall %s" % package)
		for line in out:
			if 'uninstall ok' in line:
				return True
		log.error('pear remove error, see log %s'  % package)
		return False

