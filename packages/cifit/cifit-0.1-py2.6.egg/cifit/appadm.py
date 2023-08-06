"""
	Manage different applications.
	We don't use python.mysql here, because we want this to work before that.
	it's not for running queries!
"""
from files import run
import logging
log = logging.getLogger('cifit.mysql')


class MysqlADM(object):
	def __init__(self,rootpw=None):
		"""initialize object"""
		self.rootpw = None
	def runAdmin(self,arg):
		"""run mysqladmin util with cmd as ''"""
		cmd = "mysqladmin %s " % (arg)
		if self.rootpw:
			cmd += "-p %s" % (self.rootpw)
		ret, out = run(cmd)
		if ret:
			log.error('problem with mysqladmin:%s' % arg)
		else:
			return out

	def query(self,query):
		"""given a SQL , execute and return results as []"""
		cmd = "echo \"%s;\" | mysql -s mysql" % (query)
		if self.rootpw:
			cmd += "-p %s" % (self.rootpw)
		ret,out = run(cmd)
		if not ret:
			return out
		else:
			log.error('problem executing query: %s' % query)
	def getDatabases(self):
		"""return list of databases"""
		return self.query("show databases")
	def addDatabase(self,dbname):
		"""Add database, dbname is ''"""
		out = self.runAdmin('create %s' % (dbname))
		if out:
			log.error('error:%s' % out)
	def addUserAndPerms(self,user,password,dbname):
		"""add user with all perms to DB"""
		q = "GRANT ALL PRIVILEGES ON %s.* TO %s@localhost IDENTIFIED BY '%s' " % (dbname,user,password)
		return self.query(q)






