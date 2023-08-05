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
<item><pyref function="iterdrop"><function>iterdrop</function></pyref> and
<pyref function="itercreate"><function>itercreate</function></pyref> can
be used to clear or recreate a schema.</item>
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
		"date": DATETIME,
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


def formatstring(value):
	result = []
	current = []

	# Helper function: move the content of current to result
	def shipcurrent(force=False):
		if current and (force or (len(current) > 2000)):
			if result:
				result.append(" || ")
			result.append("'%s'" % "".join(current))

	for c in value:
		if c == "'":
			current.append("''")
			shipcurrent()
		elif ord(c) < 32 or ord(c)>127:
			shipcurrent(True)
			current = []
			if result:
				result.append(" || ")
			result.append("chr(%d)" % ord(c))
		else:
			current.append(c)
			shipcurrent()
	shipcurrent(True)
	return "".join(result)


def iterdrop(cursor, fks="disable"):
	"""
	<par>Return an iterator that gives DDL statements that will completely clear the given
	schema, i.e. all functions, procedures, constraints, tables, views and sequences will be dropped.</par>
	<par>The items yielded are tuples consisting of the type of the object, the name of the
	object and the PL/SQL command to be used to drop the object.</par>
	<par><arg>fks</arg> specifies own foreign keys referencing this schema will be treated:</par>
	<dlist>
	<term>"keep"</term><item>Don't drop or disable these constraints (This <em>will</em> generate errors);</item>
	<term>"disable"</term><item>Disable these constraints;</item>
	<term>"drop"</term><item>Drop these constraints.</item>
	</dlist>
	"""
	# Find out who we are
	cursor.execute("select user from dual")
	user = cursor.fetchone().user

	# drop all procedures and functions
	cursor.execute("select distinct type, name from user_source")
	for rec in cursor:
		if rec.type=="PROCEDURE":
			yield ("procedure", rec.name, "drop procedure %s;" % rec.name)
		elif rec.type=="FUNCTION":
			yield ("function", rec.name, "drop function %s;" % rec.name)

	# drop all constraints (in the order 'C', 'U', 'R', 'P')
	for (type, desc) in [("C", "check"), ("U", "unique"), ("R", "fk"), ("P", "pk")]:
		cursor.execute("select owner, constraint_name, table_name, r_owner, r_constraint_name from all_constraints where constraint_type='%s'" % type)
		for rec in cursor:
			if rec.owner==user:
				yield (desc, rec.constraint_name, "alter table %s drop constraint %s;" % (rec.table_name, rec.constraint_name))
			elif rec.r_owner==user:
				name = "%s.%s" % (rec.owner, rec.constraint_name)
				if fks=="disable":
					yield (desc, name, "alter table %s.%s disable constraint %s;" % (rec.owner, rec.table_name, rec.constraint_name))
				elif fks=="drop":
					yield (desc, name, "alter table %s.%s drop constraint %s;" % (rec.owner, rec.table_name, rec.constraint_name))

	# drop all views
	cursor.execute("select view_name from user_views")
	for rec in cursor:
		yield ("view", rec.view_name, "drop view %s;" % rec.view_name)

	# drop all sequences
	cursor.execute("select sequence_name from user_sequences")
	for rec in cursor:
		yield ("sequence", rec.sequence_name, "drop sequence %s;" % rec.sequence_name)

	# drop all triggers
	cursor.execute("select trigger_name from user_triggers")
	for rec in cursor:
		yield ("trigger", rec.trigger_name, "drop trigger %s;" % rec.trigger_name)

	# finally drop all tables
	cursor.execute("select table_name from user_tables where nested = 'NO'")
	for rec in cursor:
		yield ("table", rec.table_name, "drop table %s;" % rec.table_name)


def _itercreate(cursor, type, name, cache):
	if (type, name) not in cache:
		if type in ("view", "procedure", "function", "type", "trigger"):
			cursor.execute("select referenced_type, referenced_name from user_dependencies where lower(type)=:type and name=:name and referenced_owner=user", type=type, name=name)
			for rec in cursor.fetchall():
				if rec.referenced_type != "NON-EXISTENT":
					for result in _itercreate(cursor, rec.referenced_type.lower(), rec.referenced_name, cache):
						yield result
		
		if type == "sequence":
			cursor.execute("select * from user_sequences where sequence_name=:name", name=name)
			rec = cursor.fetchone()
			code  = "create sequence %s\n" % rec.sequence_name.lower()
			code += "\tincrement by %d\n" % rec.increment_by
			code += "\tstart with %d\n" % rec.min_value
			code += "\tmaxvalue %s\n" % rec.max_value
			code += "\tminvalue %d\n" % rec.min_value
			code += "\t%scycle\n" % ["no", ""][rec.cycle_flag=='Y']
			code += "\tcache %d\n" % rec.cache_size
			code += "\t%sorder;\n" % ["no", ""][rec.order_flag=='Y']
		elif type == "table":
			code = ["create table %s\n(\n" % name]
			cursor.execute("select * from user_tab_columns where table_name=:name order by column_id asc", name=name)
			for rec in cursor:
				fsize = rec.data_precision
				flen = rec.data_length
				fprec = rec.data_scale
				ftype = rec.data_type.lower()
				code.append("\t%s %s" % (rec.column_name.lower(), ftype))
				if rec.char_length:
					fsize = rec.char_length
				if fsize is not None:
					code.append("(%d" % fsize)
					if fprec is not None:
						code.append(", %d" % fprec)
					code.append(")")
				if rec.data_default is not None:
					code.append(" default %s" % rec.data_default)
				if rec.nullable == 'N':
					code.append(" not null")
				code.append(",\n")
			del code[-1]
			code.append("\n);\n")
			code = "".join(code)
		elif type == "pk":
			cursor.execute("select constraint_name, table_name, r_owner, r_constraint_name from user_constraints where constraint_type='P' and constraint_name=:name", name=name)
			table_name = cursor.fetchone().table_name
			cursor.execute("select column_name from user_cons_columns where constraint_name=:name", name=name)
			code = "alter table %s add constraint %s primary key(%s);\n" % (table_name, name, ", ".join(r.column_name.lower() for r in cursor))
		elif type == "comments":
			cursor.execute("select column_name, comments from user_col_comments where table_name=:name and comments is not null", name=name)
			code = "\n".join("comment on column %s.%s is %s;" % (name, r.column_name, formatstring(r.comments)) for r in cursor) + "\n"
		elif type == "fk":
			cursor.execute("select table_name from user_constraints uc where uc.constraint_name=:name", name=name)
			table_name = cursor.fetchone().table_name
			cursor.execute("select column_name from user_cons_columns where constraint_name=:name order by position", name=name)
			recs1 = cursor.fetchall()
			cursor.execute("select r_constraint_name from user_constraints where constraint_name=:name", name=name)
			r_constraint_name = cursor.fetchone().r_constraint_name
			cursor.execute("select table_name, column_name from user_cons_columns where constraint_name=:name order by position", name=r_constraint_name)
			recs2 = cursor.fetchall()
			code = "alter table %s add constraint %s foreign key (%s) references %s;\n" % (table_name, name, ", ".join(r.column_name for r in recs1), ", ".join("%s(%s)" % (r.table_name, r.column_name) for r in recs2))
		elif type == "unique":
			cursor.execute("select table_name, r_owner, r_constraint_name from user_constraints where constraint_type='U' and constraint_name=:name", name=name)
			table_name = cursor.fetchone().table_name
			cursor.execute("select column_name from user_cons_columns where constraint_name=:name", name=name)
			code = "alter table %s add constraint %s unique(%s);\n" % (table_name, name, ", ".join(r.column_name for r in cursor))
		elif type == "view":
			cursor.execute("select text from user_views where view_name=:name", name=name)
			text = cursor.fetchone().text
			code = "create or replace view %s as\n\t%s;\n/\n" % (name, text.strip())
		elif type in ("function", "procedure", "package", "type"):
			cursor.execute("select text from user_source where lower(type)=:type and name=:name order by line", type=type, name=name)
			code = "".join(rec.text for rec in cursor)
			code = "create or replace %s\n/\n" % code.strip()
		else:
			raise ValueError("unknown type %r" % type)
		cache[(type, name)] = code
		yield (type, name, code)


def itercreate(cursor):
	"""
	<par>Return an iterator that yields DDL statements which will recreate the schema.</par>
	<par>Items yielded are tuples containing the type of the object, the name of the object
	and the PL/SQL code used to recreate the object.</par>
	"""
	cache = {}

	# Sequences
	cursor.execute("select sequence_name from user_sequences")
	for rec in cursor.fetchall():
		for result in _itercreate(cursor, "sequence", rec.sequence_name, cache):
			yield result

	# Tables
	cursor.execute("select table_name from user_tables")
	for rec in cursor.fetchall():
		for result in _itercreate(cursor, "table", rec.table_name, cache):
			yield result

		# Primary key
		cursor.execute("select constraint_name from user_constraints where constraint_type='P' and table_name=:name", name=rec.table_name)
		for rec2 in cursor.fetchall():
			for result in _itercreate(cursor, "pk", rec2.constraint_name, cache):
				yield result

		for result in _itercreate(cursor, "comments", rec.table_name, cache):
			yield result

	# Foreign keys
	cursor.execute("select * from user_constraints where constraint_type='R'")
	for rec in cursor.fetchall():
		for result in _itercreate(cursor, "fk", rec.constraint_name, cache):
			yield result

	# Unique constraints
	cursor.execute("select constraint_name from user_constraints where constraint_type='U'")
	for rec in cursor.fetchall():
		for result in _itercreate(cursor, "unique", rec.constraint_name, cache):
			yield result

	# Views
	cursor.execute("select view_name from user_views")
	for rec in cursor.fetchall():
		for result in _itercreate(cursor, "view", rec.view_name, cache):
			yield result

	# Functions, procedures, packages, types
	for type in ["function", "procedure", "package", "type"]:
		cursor.execute("select object_name from user_objects where lower(object_type)=:type", type=type)
		for rec in cursor.fetchall():
			for result in _itercreate(cursor, type, rec.object_name, cache):
				yield result
