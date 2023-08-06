#!/usr/bin/env python
# encoding: utf-8
"""
network.py

Manage network connections.

Created by Craig Sawyer on 2010-01-14.
Copyright (c) 2009, 2010 Craig Sawyer (csawyer@yumaed.org). All rights reserved. see LICENSE.
"""

import logging

from cifitlib import files
from cifitlib.classes import classes

log = logging.getLogger('%s:network' % classes['hostname'])

class NetObject(object):
	def __init__(self):
		self.interface = None

class NetBase(object):
	"""base class"""
	def __init__(self):
		pass

class NetDebian(NetBase):
	def addInterface(self,netobj):
		"""add Interface to a Debian system.
		netobj should be a {}.
		keys we expect & support:
			interface:
			address
			netmask
			broadcast
			gateway
		"""
		pass
	def addVirtInterface(self,netobj):
		"""add virtual interface to a debian system.
		this is essentially the same thing as above, except interface can be left blank,
		if there is a network already setup on an interface that makes sense for this link.

		"""
		pass
	def listInterfaces(self):
		"""return a list of interfaces
		{} 
		"""
		ints = {}
		ret,out = files.run('ifconfig')
		if not ret:
			for line in out:
				if line[:1] != '\t':
					blah = line.split(':')
					i = blah[0]
					ints[i] = []
				if line.startswith('\tinet'):
					ip = line.split(' ')
					#print ip
					ip = ip[1]
					ints[i].append(ip)
		return ints

if __name__ == '__main__':
	x = NetDebian()
	print x.listInterfaces()

