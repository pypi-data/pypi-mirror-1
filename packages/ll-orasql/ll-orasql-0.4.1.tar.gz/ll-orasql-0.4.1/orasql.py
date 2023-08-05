#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

## Copyright 2004 by LivingLogic AG, Bayreuth/Germany.
## Copyright 2004 by Walter Dörwald
##
## All Rights Reserved
##
## Permission to use, copy, modify, and distribute this software and its documentation
## for any purpose and without fee is hereby granted, provided that the above copyright
## notice appears in all copies and that both that copyright notice and this permission
## notice appear in supporting documentation, and that the name of LivingLogic AG or
## the author not be used in advertising or publicity pertaining to distribution of the
## software without specific, written prior permission.
##
## LIVINGLOGIC AG AND THE AUTHOR DISCLAIM ALL WARRANTIES WITH REGARD TO THIS SOFTWARE,
## INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS, IN NO EVENT SHALL
## LIVINGLOGIC AG OR THE AUTHOR BE LIABLE FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL
## DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER
## IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR
## IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.


"""
<par>This module contains utilities for working with
<link href="http://www.computronix.com/utilities.shtml#Oracle"><app>cx_Oracle</app></link>:</par>
<ulist>
<item>It allows calling procedure with keyword arguments (via the
<pyref class="Proc"><class>Proc</class></pyref> class).</item>
<item>Query results will be put into <pyref class="Record"><class>Record</class></pyref>
objects, where database fields are accessible as object attributes.</item>
</ulist>
"""


import datetime


from cx_Oracle import *


class Proc:
	"""
	A <class>Proc</class> object is a wrapper for calling a specific Oracle
	procedure with keyword arguments.
	"""
	_ora2cx = {
		"number": NUMBER,
		"varchar2": STRING,
		"clob": CLOB,
		"blob": BLOB,
	}
	
	def __init__(self, name):
		"""
		Create a <class>Proc</class> object. <arg>name</arg> is the name of the
		Oracle procedure.
		"""
		self.name = name
		self._realargs = None

	def __repr__(self):
		return "Proc(%r)" % self.name

	def _calcrealargs(self, cursor):
		if self._realargs is None:
			self._realargs = ({}, [])
			cursor.execute("select lower(argument_name) as name, lower(in_out) as in_out, lower(data_type) as datatype from user_arguments where lower(object_name)=lower(:name) order by sequence", name=self.name)
			for (i, record) in enumerate(cursor):
				self._realargs[1].append((record.name, record.datatype, "in" in record.in_out, "out" in record.in_out))
				self._realargs[0][record.name] = (i, record.datatype, "in" in record.in_out, "out" in record.in_out)

	def __call__(self, cursor, **kwargs):
		"""
		Call the procedure with keyword arguments <arg>kwargs</arg>. <arg>cursor</arg>
		must be a <module>cx_Oracle</module> cursor. This will return a
		<pyref class="Record"><class>Record</class></pyref> object containing the result
		of the call.
		"""
		self._calcrealargs(cursor)
		realargs = [None]*len(self._realargs[1])
		for (key, value) in kwargs.iteritems():
			(pos, datatype, isin, isout) = self._realargs[0][key.lower()]
			if isinstance(value, unicode):
				value = value.encode("iso-8859-1")
			realargs[pos] = value

		# Replace out parameters (and strings that are longer than the allowed
		# maximum) with variables
		for (pos, (name, datatype, isin, isout)) in enumerate(self._realargs[1]):
			realarg = realargs[pos]
			if isout or (isinstance(realarg, str) and len(realarg) >= 32768):
				var = cursor.var(self._ora2cx[datatype])
				var.setvalue(0, realarg)
				realargs[pos] = var

		result = Record()
		for (i, value) in enumerate(cursor.callproc(self.name, realargs)):
			result[self._realargs[1][i][0]] = value
		return result


class LLProc(Proc):
	def __call__(self, cursor, **kwargs):
		args = {}
		for (key, value) in kwargs.iteritems():
			if key == "user":
				key = "c_user"
			else:
				key = "p_%s" % key
			args[key] = value

		result = Record()
		for (key, value) in Proc.__call__(self, cursor, **args).iteritems():
			if key == "c_user":
				key = "user"
			elif key.startswith("p_"):
				key = key[2:]
			else:
				raise ValueError("unknown parameter name %r in result" % key)
			result[key] = value
		return result


class Record(dict):
	"""
	A <class>Record</class> is a subclass of <class>dict</class> that is used
	for storing results of database queries. Both item and attribute access (i.e.
	<method>__getitem__</method> and <method>__getattr__</method>) are available.
	Field names are case insensitive.
	"""
	def fromdata(cls, cursor, row):
		"""
		This class method can be used to create a <class>Record</class> instance
		from the database data.
		"""
		record = cls()
		for (i, field) in enumerate(row):
			record[cursor.description[i][0]] = field
		return record
	fromdata = classmethod(fromdata)

	def __getitem__(self, name):
		return dict.__getitem__(self, name.lower())

	def __setitem__(self, name, value):
		dict.__setitem__(self, name.lower(), value)

	def __delitem__(self, name):
		dict.__delitem__(self, name.lower())

	def __getattr__(self, name):
		return self.__getitem__(name)

	def __setattr__(self, name, value):
		self.__setitem__(name, value)

	def __delattr__(self, name):
		self.__delitem__(name)

	def __repr__(self):
		return "%s.%s(%s)" % (self.__class__.__module__, self.__class__.__name__, ", ".join(["%s=%r" % item for item in self.iteritems()]))


class Connection(Connection):
	def cursor(self):
		return Cursor(self)


def connect(*args, **kwargs):
	return Connection(*args, **kwargs)


class Cursor(Cursor):
	"""
	A subclass of <module>cx_Oracle</module>s cursor class. All database results
	will be returned as <pyref class="Record"><class>Record</class> objects.
	"""
	def fetchone(self, type=Record):
		row = super(Cursor, self).fetchone()
		if row is not None:
			row = type.fromdata(self, row)
		return row

	def fetchmany(self, rows=0, type=Record):
		sup = super(Cursor, self)
		return [ type.fromdata(self, row) for row in sup.fetchmany(rows)]

	def fetchall(self, type=Record):
		sup = super(Cursor, self)
		return [ type.fromdata(self, row) for row in sup.fetchall()]

	def fetch(self, type=Record):
		while True:
			yield type.fromdata(self, self.next())

	def __iter__(self):
		return self.fetch()
