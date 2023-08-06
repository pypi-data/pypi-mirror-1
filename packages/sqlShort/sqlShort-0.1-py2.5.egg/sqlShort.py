#!/usr/bin/env python
# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------
#    sqlShort - A tiny wrapper for MySQLdb
#    Version 0.1 - 2009-04-28
#    $Revision: 5 $ $Date: 2009-10-17 18:42:31 +0100 (sam., 17 oct. 2009) $
#-------------------------------------------------------------------------
#
#    Copyright 2008, 2009 Etienne Gaudrain <egaudrain@gmail.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, version 3 of the License.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#-------------------------------------------------------------------------

from numpy import *
import MySQLdb

class sqlShort:
	def __init__(self, **kwarg):
		"""Creates a connection. Example:
		db = sqlShort(host="sql.server.com", user="toto", passwd="secret", db="the_toto_jokes")
		"""
		self.db = MySQLdb.connect(**kwarg)
		self.dbh = self.db.cursor()
	
	def __del__(self):
		self.db.close()
	
	def query(self, sql, Array=False, dtype='f8'):
		"""Executes a SQL query.
		In case of SELECT query, a tuple of lists is returned.
		If Array=True, the returned lists are numpy arrays (if the type is numeric).
		In that cas, the dtype of the array can be provided.
		"""
		
		try:
			self.dbh.execute(sql)
		except:
			print sql
			raise
		
		result  = self.dbh.fetchall()
		description = self.dbh.description
		
		if description==None:
			return ()
		
		#~ print description
		n = len(description)
		
		if len(result)==0:
			if Array :
				tuple([  array([],dtype=dtype) for i in range(n) ])
			else :
				 return tuple([ () for i in range(n) ])
		
		t = list()
		for i in range(n) :
			t.append([])
		for row in result :
			for i in range(n) :
				t[i].append(row[i])
		if Array :
			for i in range(n) :
				if (description[i][1] not in MySQLdb.NUMBER) and (description[i][1]!=246):
					continue
				else:
					t[i] = array(t[i], dtype=dtype)
		
		return tuple(t)
	
	def lastrowid(self):
		"""Returns the last inserted id."""
		return self.dbh.lastrowid
	
	def make_insert(self, arg):
		"""Converts a dict into an INSERT type syntax, dealing with the types.
		If a dictionnary is provided, returns: SET `key`=value, ...
		If a list of dictionnaries is given, the long INSERT syntax is used: (`key`, ...) VALUES (value, ...), (...), ...
		In that case, the list of fields is read from the keys of the first row.
		"""
		if type(arg)==type(dict()):
			fields = "SET "+", ".join(["`%s`=%s" % (k, self.str(v)) for k, v in arg.items()])
		elif type(arg)==type(list()):
			n = len(arg[0].keys())
			fields  = "("+", ".join(["`%s`" % k for k in arg[0].keys()])+")"
			fields += " VALUES "
			L = list()
			for i, r in enumerate(arg):
				if len(r.values()) != n:
					print r
					raise ValueError('On row %d, %d arguments found, %d expected.' % (i, len(r.values()), n))
				L.append("("+", ".join([self.str(v) for v in r.values()])+")")
			fields += ", ".join(L)
		else:
			raise TypeError('sqlShort.make_insert() argument should be dict or list (%s given).' % type(arg))
		
		return fields
	
	def str(self, v):
		"""Converts a Python variable into SQL string to insert it in a query."""
		if v is None:
			return "NULL"
		elif type(v)==type(str()):
			return "\""+MySQLdb.escape_string(v)+"\""
		else:
			return str(v)
		
