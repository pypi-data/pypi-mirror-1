#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

## Copyright 2004/2005 by LivingLogic AG, Bayreuth/Germany.
## Copyright 2004/2005 by Walter Dörwald
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
<par><module>ll.orasql</module> contains utilities for working with
<link href="http://www.computronix.com/utilities.shtml#Oracle"><app>cx_Oracle</app></link>:</par>
<ulist>
<item>It allows calling procedures with keyword arguments (via the
<pyref class="Proc"><class>Proc</class></pyref> class).</item>
<item>Query results will be put into <pyref class="Record"><class>Record</class></pyref>
objects, where database fields are accessible as object attributes.</item>
<item>The <pyref class="Cursor"><class>Cursor</class></pyref> class
provides methods for iterating through the database metadata.</item>
</ulist>
"""


import datetime

from cx_Oracle import *

from ll import misc, astyle

# ipipe support
try:
	from ll import ipipe
except ImportError:
	ipipe = None


class SQLObjectNotFoundError(Exception):
	def __init__(self, obj):
		self.obj = obj

	def __str__(self):
		return "%r not found" % self.obj


class UnknownModeError(ValueError):
	def __init__(self, mode):
		self.mode = mode

	def __str__(self):
		return "unknown mode %r" % self.mode


class UnknownSchemaError(ValueError):
	def __init__(self, schema):
		self.schema = schema

	def __str__(self):
		return "unknown schema %r" % self.schema


class ConflictError(ValueError):
	def __init__(self, definition, message):
		self.definition = definition
		self.message = message

	def __str__(self):
		return "conflict in %r: %s" % self.definition


_default = object() # marker object for unset parameters


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
	
	def __init__(self, name, encoding=None):
		"""
		Create a <class>Proc</class> object. <arg>name</arg> is the name of the
		Oracle procedure.
		"""
		self.name = name
		self._realargs = None
		self.encoding = encoding

	def __repr__(self):
		if self.encoding is None:
			return "Proc(%r)" % self.name
		else:
			return "Proc(%r, %r)" % (self.name, self.encoding)

	def _calcrealargs(self, cursor):
		if self._realargs is None:
			self._realargs = ({}, [])
			cursor.execute("select lower(argument_name) as name, lower(in_out) as in_out, lower(data_type) as datatype from user_arguments where lower(object_name)=lower(:name) order by sequence", name=self.name)
			for (i, record) in enumerate(cursor):
				data = (i, record.name, record.datatype, "in" in record.in_out, "out" in record.in_out)
				self._realargs[1].append(data)
				self._realargs[0][record.name] = data

	def __call__(self, cursor, *args, **kwargs):
		"""
		Call the procedure with arguments <arg>args</arg> and keyword arguments
		<arg>kwargs</arg>. <arg>cursor</arg> must be a <module>cx_Oracle</module>
		cursor. This will return a <pyref class="Record"><class>Record</class></pyref>
		object containing the result of the call.
		"""
		self._calcrealargs(cursor)

		# Get preinitialized parameter array
		la = len(args)
		lra = len(self._realargs[1])
		if la > lra:
			raise TypeError("too many parameters for %s: %d given, %d expected" % (self.name, la, lra))
		realargs = list(args) + [_default]*(lra-la)

		# Put keyword arguments into the parameter array
		for (key, value) in kwargs.iteritems():
			try:
				(pos, name, datatype, isin, isout) = self._realargs[0][key.lower()]
			except KeyError:
				raise TypeError("unknown parameter for %s: %s" % (self.name, key))
			else:
				if realargs[pos] is not _default:
					raise TypeError("duplicate argument for %s: %s" % (self.name, key))
			if isinstance(value, unicode) and self.encoding is not None:
				value = value.encode(self.encoding)
			realargs[pos] = value

		# Replace out parameters (and strings that are longer than the allowed
		# maximum) with variables; replace unspecified parameters with None
		for (pos, name, datatype, isin, isout) in self._realargs[1]:
			realarg = realargs[pos]
			if realarg is _default:
				realarg = None
				realargs[pos] = realarg
			if isout or (isinstance(realarg, str) and len(realarg) >= 32768):
				var = cursor.var(self._ora2cx[datatype])
				var.setvalue(0, realarg)
				realargs[pos] = var

		result = Record()
		for (i, value) in enumerate(cursor.callproc(self.name, realargs)):
			result[self._realargs[1][i][1]] = value
		return result


class LLProc(Proc):
	def __call__(self, cursor, *args, **kwargs):
		realkwargs = {}
		for (key, value) in kwargs.iteritems():
			if key == "user":
				key = "c_user"
			elif key == "out":
				key = "c_out"
			else:
				key = "p_%s" % key
			realkwargs[key] = value

		result = Record()
		for (key, value) in Proc.__call__(self, cursor, *args, **realkwargs).iteritems():
			if key == "c_user":
				key = "user"
			elif key == "c_out":
				key = "out"
			elif key.startswith("p_"):
				key = key[2:]
			else:
				raise TypeError("unknown parameter name %r in result" % key)
			result[key] = value
		return result


class Record(dict):
	"""
	A <class>Record</class> is a subclass of <class>dict</class> that is used
	for storing results of database queries. Both item and attribute access (i.e.
	<method>__getitem__</method> and <method>__getattr__</method>) are available.
	Field names are case insensitive.
	"""
	@classmethod
	def fromdata(cls, cursor, row):
		"""
		This class method can be used to create a <class>Record</class> instance
		from the database data.
		"""
		record = cls()
		for (i, field) in enumerate(row):
			record[cursor.description[i][0]] = field
		return record

	def __getitem__(self, name):
		return dict.__getitem__(self, name.lower())

	def __setitem__(self, name, value):
		dict.__setitem__(self, name.lower(), value)

	def __delitem__(self, name):
		dict.__delitem__(self, name.lower())

	def __getattr__(self, name):
		try:
			return self.__getitem__(name)
		except KeyError:
			raise AttributeError(name)

	def __setattr__(self, name, value):
		self.__setitem__(name, value)

	def __delattr__(self, name):
		try:
			self.__delitem__(name)
		except KeyError:
			raise AttributeError(name)

	def __xattrs__(self, mode):
		"""
		Return the attributes of this record. This is for interfacing with
		<pyref module="ll.ipipe"><module>ll.ipipe</module></pyref>.
		"""
		return [key.lower() for key in self.iterkeys()]

	def __xrepr__(self, mode):
		yield (-1, True)
		if mode == "header":
			yield (astyle.style_default, "%s.%s" % (self.__class__.__module__, self.__class__.__name__))
		else:
			yield (astyle.style_default, repr(self))

	def __repr__(self):
		return "%s.%s(%s)" % (self.__class__.__module__, self.__class__.__name__, ", ".join("%s=%r" % item for item in self.iteritems()))


class _AllTypes(object):
	def __init__(self, connection, class_, count):
		self.connection = connection
		self.class_ = class_
		self.type = class_.type
		self.count = count

	def __xattrs__(self, mode):
		return ("type", "count")

	def __xrepr__(self, mode):
		yield (-1, True)
		if mode == "header" or mode == "footer":
			yield (astyle.style_default, self.type + "s")
		else:
			yield (astyle.style_default, repr(self))

	def __iter__(self):
		return self.__xiter__("default")

	def __xiter__(self, mode):
		cursor = self.connection.cursor()
		cursor.execute("select object_name from user_objects where lower(object_type) = :type", type=self.type)
		return (self.class_(row.object_name, cursor=cursor) for row in cursor)


class SessionPool(SessionPool):
	"""
	<class>SessionPool</class> is a subclass of <class>cx_Oracle.SessionPool</class>.
	"""

	def __init__(self, user, password, database, min, max, increment, connectiontype=None, threaded=False):
		if connectiontype is None:
			connectiontype = Connection
		super(SessionPool, self).__init__(user, password, database, min, max, increment, connectiontype, threaded)

	def connectstring(self):
		return "%s@%s" % (self.username, self.tnsentry)

	def __repr__(self):
		return "<%s.%s object db=%r at 0x%x>" % (self.__class__.__module__, self.__class__.__name__, self.connectstring(), id(self))


class Connection(Connection):
	"""
	<class>Connection</class> is a subclass of <class>cx_Oracle.Connection</class>.
	"""
	def connectstring(self):
		return "%s@%s" % (self.username, self.tnsentry)

	def cursor(self):
		return Cursor(self)

	def __repr__(self):
		return "<%s.%s object db=%r at 0x%x>" % (self.__class__.__module__, self.__class__.__name__, self.connectstring(), id(self))

	def __xrepr__(self, mode):
		yield (-1, True)
		if mode == "header" or mode=="footer":
			yield (astyle.style_default, "oracle connection to %s" % self.connectstring())
		else:
			yield (astyle.style_default, repr(self))

	def __xiter__(self, mode):
		if mode is None:
			yield ipipe.XMode(self, "schema", "schema", "object types in this schema")
			yield ipipe.XMode(self, "objectscreateown", "objects (create order)", "all objects in this schema (in create order)")
			yield ipipe.XMode(self, "objectsdropown", "objects (drop order)", "all objects in this schema (in drop order)")
		elif mode == "objectscreateown":
			for item in self.iterobjects("create", "own"):
				yield item
		elif mode == "objectsdropown":
			for item in self.iterobjects("drop", "own"):
				yield item
		else:
			for item in self.iterschema():
				yield item

	def iterschema(self):
		cursor = self.cursor()
		cursor.execute("select object_type as type, count(*) as count from user_objects group by object_type")
		for row in cursor:
			class_ = Definition.name2type.get(row.type.lower(), None)
			if class_ is not None:
				yield _AllTypes(self, class_, row.count)

	def iterobjects(self, mode="create", schema="dep"):
		"""
		<par>Generator that yields the definition of all (or the current users)
		sequences, tables, primary keys, foreign keys, comments, unique constraints,
		indexes, views, functions, procedures, packages and types in a
		specified order.</par>
		<par><arg>mode</arg> specifies the order in which objects will be yielded:</par>
		<dlist>
		<term><lit>"create"</lit></term><item>Create order, i.e. recreating the
		objects in this order will not lead to errors.</item>
		<term><lit>"drop"</lit></term><item>Drop order, i.e. dropping the
		objects in this order will not lead to errors.</item>
		<term><lit>"flat"</lit></term><item>Unordered.</item>
		</dlist>
		<par><arg>schema</arg> specifies from which schema definitions should be
		yielded:</par>
		<dlist>
		<term><lit>"own"</lit></term><item>Only definitions belonging to the current
		user will be yielded.</item>
		<term><lit>"dep"</lit></term><item>Definitions belonging to the current
		user and those definitions these depend on will be yielded.</item>
		<term><lit>"all"</lit></term><item>All definitions from all users will be
		yielded.</item>
		</dlist>
		"""
		if mode not in ("create", "drop", "flat"):
			raise UnknownModeError(mode)

		if schema not in ("own", "dep", "all"):
			raise UnknownSchemaError(schema)

		done = set()

		cursor = self.cursor()

		def dosequences():
			# select * from all_sequences where sequence_owner=nvl(:owner, user) and sequence_name=:name
			if schema == "all":
				cursor.execute("select decode(sequence_owner, user, null, sequence_owner) as sequence_owner, sequence_name from all_sequences")
			else:
				cursor.execute("select null as sequence_owner, sequence_name from user_sequences")
			for rec in cursor.fetchall():
				for definition in SequenceDefinition(rec.sequence_name, rec.sequence_owner, cursor).iterdependent(cursor, done, mode, schema):
					yield definition

		def dotables():
			if schema == "all":
				cursor.execute("select decode(owner, user, null, owner) as owner, table_name from all_tables")
			else:
				cursor.execute("select null as owner, table_name from user_tables")
			for rec in cursor.fetchall():
				if mode == "create" or mode == "flat":
					for definition in TableDefinition(rec.table_name, rec.owner, cursor).iterdependent(cursor, done, mode, schema):
						yield definition
		
				# Primary key
				if schema == "all":
					cursor.execute("select decode(owner, user, null, owner) as owner, constraint_name from all_constraints where constraint_type='P' and owner=:owner and table_name=:name", owner=rec.owner, name=rec.table_name)
				else:
					cursor.execute("select null as owner, constraint_name from user_constraints where constraint_type='P' and table_name=:name", name=rec.table_name)
				for rec2 in cursor.fetchall():
					for definition in PKDefinition(rec2.constraint_name, rec2.owner, cursor).iterdependent(cursor, done, mode, schema):
						yield definition

				# Comments
				if schema == "all":
					cursor.execute("select column_name from all_tab_columns where owner=:owner and table_name=:name order by column_id", owner=rec.owner, name=rec.table_name)
				else:
					cursor.execute("select column_name from user_tab_columns where table_name=:name order by column_id", name=rec.table_name)
				for rec2 in cursor.fetchall():
					yield CommentDefinition("%s.%s" % (rec.table_name, rec2.column_name), rec.owner, cursor) # No dependency checks neccessary
	
				if mode == "drop":
					for definition in TableDefinition(rec.table_name, rec.owner, cursor).iterdependent(cursor, done, mode, schema):
						yield definition

		def doconstraints():
			if schema == "all":
				cursor.execute("select constraint_type, decode(owner, user, null, owner) as owner, constraint_name from all_constraints where constraint_type in ('R', 'U')")
			else:
				cursor.execute("select constraint_type, null as owner, constraint_name from user_constraints where constraint_type in ('R', 'U')")
			types = {"U": UniqueDefinition, "R": FKDefinition}
			for rec in cursor.fetchall():
				for definition in types[rec.constraint_type](rec.constraint_name, rec.owner, cursor).iterdependent(cursor, done, mode, schema):
					yield definition

		def doindexes():
			if schema == "all":
				cursor.execute("(select decode(owner, user, null, owner) as owner, index_name, table_name from all_indexes where generated='N' minus select decode(owner, user, null, owner) as owner, constraint_name as index_name, table_name from all_constraints where constraint_type in ('U', 'P')) order by table_name, index_name")
			else:
				cursor.execute("(select null as owner, index_name, table_name from user_indexes where generated='N' minus select null as owner, constraint_name as index_name, table_name from user_constraints where constraint_type in ('U', 'P')) order by table_name, index_name")
			for rec in cursor.fetchall():
				for definition in IndexDefinition(rec.index_name, rec.owner).iterdependent(cursor, done, mode, schema):
					yield definition

		def dosynonyms():
			if schema == "all":
				cursor.execute("select decode(owner, user, null, owner) as owner, synonym_name from all_synonyms")
			else:
				cursor.execute("select null as owner, synonym_name from user_synonyms")
			for rec in cursor.fetchall():
				for definition in SynonymDefinition(rec.synonym_name, rec.owner, cursor).iterdependent(cursor, done, mode, schema):
					yield definition

		def doviews():
			if schema == "all":
				cursor.execute("select decode(owner, user, null, owner) as owner, view_name from all_views")
			else:
				cursor.execute("select null as owner, view_name from user_views")
			for rec in cursor.fetchall():
				for definition in ViewDefinition(rec.view_name, rec.owner, cursor).iterdependent(cursor, done, mode, schema):
					yield definition

		def docode():
			for type in (FunctionDefinition, ProcedureDefinition, PackageDefinition, PackageBodyDefinition, TypeDefinition, TriggerDefinition, JavaSourceDefinition):
				if schema == "all":
					cursor.execute("select decode(owner, user, null, owner) as owner, object_name from all_objects where lower(object_type)=lower(:type)", type=type.type)
				else:
					cursor.execute("select null as owner, object_name from user_objects where lower(object_type)=lower(:type)", type=type.type)
				for rec in cursor.fetchall():
					for definition in type(rec.object_name, rec.owner, cursor).iterdependent(cursor, done, mode, schema):
						yield definition

		funcs = (dosequences, dotables, doconstraints, doindexes, dosynonyms, doviews, docode)
		if mode == "drop":
			funcs = reversed(funcs)

		for func in funcs:
			for definition in func():
				yield definition


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

	def __xrepr__(self, mode):
		yield (-1, True)
		if mode == "header" or mode == "footer":
			if self.statement:
				yield (astyle.style_default, self.statement)
			else:
				yield (astyle.style_default, "no statement")
		else:
			yield (astyle.style_default, repr(self))

	def __repr__(self):
		return "<%s.%s statement=%r at 0x%x>" % (self.__class__.__module__, self.__class__.__name__, self.statement, id(self))


def formatstring(value, latin1=False):
	result = []
	current = []

	if latin1:
		upper = 255
	else:
		upper = 127
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
		elif ord(c) < 32 or ord(c)>upper:
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


class MixinNormalDates(object):
	def cdate(self, cursor=None):
		cursor = self.getcursor(cursor)
		cursor.execute("select created from all_objects where lower(object_type)=:type and object_name=:name and owner=nvl(:owner, user)", type=self.__class__.type, name=self.name, owner=self.owner)
		row = cursor.fetchone()
		if row is None:
			raise SQLObjectNotFoundError(self)
		return row.created

	def udate(self, cursor=None):
		cursor = self.getcursor(cursor)
		cursor.execute("select last_ddl_time from all_objects where lower(object_type)=:type and object_name=:name and owner=nvl(:owner, user)", type=self.__class__.type, name=self.name, owner=self.owner)
		row = cursor.fetchone()
		if row is None:
			raise SQLObjectNotFoundError(self)
		return row.last_ddl_time


class MixinCodeDDL(object):
	def createddl(self, cursor=None, term=True):
		cursor = self.getcursor(cursor)
		cursor.execute("select text from all_source where lower(type)=lower(:type) and owner=nvl(:owner, user) and name=:name order by line", type=self.__class__.type, owner=self.owner, name=self.name)
		code = "\n".join((rec.text or "").rstrip() for rec in cursor) # sqlplus strips trailing spaces when executing SQL scripts, so we do that too
		code = " ".join(code.split(None, 1)) # compress "PROCEDURE          FOO"
		code = code.strip()
		if self.owner is not None:
			type = self.__class__.type
			code = code[code.lower().find(type)+len(type):].strip() # drop "procedure" etc.
			code = "create or replace %s %s.%s\n" % (type, self.owner, code)
		else:
			code = "create or replace %s\n" % code
		if term:
			code += "\n/\n"
		else:
			code += "\n"
		return code

	def dropddl(self, cursor=None, term=True):
		if self.owner is not None:
			name = "%s.%s" % (self.owner, self.name)
		else:
			name = self.name
		code = "drop %s %s" % (self.__class__.type, name)
		if term:
			code += ";\n"
		else:
			code += "\n"
		return code


class Definition(object):
	name2type = {}

	class __metaclass__(type):
		def __new__(mcl, name, bases, dict):
			typename = None
			if "type" in dict and name != "Definition":
				typename = dict["type"]
			cls = type.__new__(mcl, name, bases, dict)
			if typename is not None:
				Definition.name2type[typename] = cls
			return cls

	def __init__(self, name, owner=None, cursor=None):
		self.name = name
		self.owner = owner
		self.cursor = cursor

	def __repr__(self):
		if self.owner is not None:
			return "%s.%s(%r, %r)" % (self.__class__.__module__, self.__class__.__name__, self.name, self.owner)
		else:
			return "%s.%s(%r)" % (self.__class__.__module__, self.__class__.__name__, self.name)

	def __eq__(self, other):
		return self.__class__ is other.__class__ and self.name == other.name and self.owner == other.owner

	def __ne__(self, other):
		return not self.__eq__(other)

	def __hash__(self):
		return hash(self.__class__.__name__) ^ hash(self.name) ^ hash(self.owner)

	@misc.notimplemented
	def createddl(self, cursor=None, term=True):
		"""
		Return an &sql; statement that will recreate <self/> in the database.
		"""

	@misc.notimplemented
	def dropddl(self, cursor=None, term=True):
		"""
		Return an &sql; statement that will delete <self/> in the database.
		"""

	@misc.notimplemented
	def cdate(self, cursor=None):
		"""
		Return a <class>datetime.datetime</class> object with the creation date of
		<self/> in the database specified by <arg>cursor</arg> (or <lit>None</lit>
		if such information is not available).
		"""

	@misc.notimplemented
	def udate(self, cursor=None):
		"""
		Return a <class>datetime.datetime</class> object with the last modification
		date of <self/> in the database specified by <arg>cursor</arg>
		(or <lit>None</lit> if such information is not available).
		"""

	def iterdependent(self, cursor=None, done=None, mode="create", schema="dep"):
		cursor = self.getcursor(cursor)
		if done is None:
			done = set()
		if self not in done:
			if mode in ("create", "drop"):
				if mode == "drop":
					cursor.execute("select type, decode(owner, user, null, owner) as owner, name from all_dependencies where lower(referenced_type)=:type and referenced_name=:name and referenced_owner=nvl(:owner, user)", type=self.__class__.type, name=self.name, owner=self.owner)
				else:
					cursor.execute("select referenced_type as type, decode(referenced_owner, user, null, referenced_owner) as owner, referenced_name as name from all_dependencies where lower(type)=:type and name=:name and owner=nvl(:owner, user)", type=self.__class__.type, name=self.name, owner=self.owner)
				for rec in cursor.fetchall():
					if rec.type != "NON-EXISTENT":
						try:
							type = Definition.name2type[rec.type.lower()]
						except KeyError:
							pass # FIXME: Issue a warning?
						else:
							for definition in type(rec.name, rec.owner, self.cursor).iterdependent(cursor, done, mode, schema):
								yield definition
			elif mode != "flat":
				raise UnknownModeError(mode)
			if schema != "own" or self.owner is None:
				done.add(self)
				yield self

	def getcursor(self, cursor):
		if cursor is None:
			cursor = self.cursor.connection.cursor() # We don't want to disturb the original cursor, so we get a new one
		return cursor

	def getconnectstring(self):
		if self.cursor:
			return self.cursor.connection.connectstring()
		return None
	connectstring = property(getconnectstring)

	def __xiter__(self, mode):
		if mode is None:
			yield ipipe.XMode(self, "create", "create statement", "the SQL script to create this %s" % self.type)
			yield ipipe.XMode(self, "drop", "drop statement", "the SQL script to drop this %s" % self.type)
			yield ipipe.XMode(self, "referencedbyown", "referenced by own", "other objects (in this schema) depending on this %s" % self.type)
			yield ipipe.XMode(self, "referencedbydep", "referenced by all", "all other objects depending on this %s" % self.type)
			yield ipipe.XMode(self, "referencesown", "references own", "other objects (in this schema) on which this %s depends" % self.type)
			yield ipipe.XMode(self, "referencesdep", "references all", "all other objects on which this %s depends" % self.type)
		elif mode == "referencedbyown":
			for item in self.iterdependent(mode="drop", schema="own"):
				yield item
		elif mode == "referencedbydep":
			for item in self.iterdependent(mode="drop", schema="dep"):
				yield item
		elif mode == "referencesown":
			for item in self.iterdependent(mode="create", schema="own"):
				yield item
		elif mode == "referencesdep":
			for item in self.iterdependent(mode="create", schema="dep"):
				yield item
		elif mode == "drop":
			for item in self.dropddl().splitlines():
				yield item
		else:
			for item in self.createddl().splitlines():
				yield item

	def __xattrs__(self, mode):
		return ("type", "owner", "name")


class SequenceDefinition(MixinNormalDates, Definition):
	type = "sequence"

	def _createddl(self, cursor, term, copyvalue):
		cursor = self.getcursor(cursor)
		cursor.execute("select * from all_sequences where sequence_owner=nvl(:owner, user) and sequence_name=:name", owner=self.owner, name=self.name)
		rec = cursor.fetchone()
		if rec is None:
			raise SQLObjectNotFoundError(self)
		if self.owner is not None:
			code  = "create sequence %s.%s\n" % (rec.sequence_owner, rec.sequence_name)
		else:
			code  = "create sequence %s\n" % rec.sequence_name
		code += "\tincrement by %d\n" % rec.increment_by
		if copyvalue:
			code += "\tstart with %d\n" % (rec.last_number + rec.increment_by)
		else:
			code += "\tstart with %d\n" % rec.min_value
		code += "\tmaxvalue %s\n" % rec.max_value
		code += "\tminvalue %d\n" % rec.min_value
		code += "\t%scycle\n" % ["no", ""][rec.cycle_flag == "Y"]
		if rec.cache_size:
			code += "\tcache %d\n" % rec.cache_size
		else:
			code += "\tnocache\n"
		code += "\t%sorder" % ["no", ""][rec.order_flag == "Y"]
		if term:
			code += ";\n"
		else:
			code += "\n"
		return code

	def createddl(self, cursor=None, term=True):
		return self._createddl(cursor, term, False)

	def createddlcopy(self, cursor=None, term=True):
		return self._createddl(cursor, term, True)

	def dropddl(self, cursor=None, term=True):
		if self.owner is not None:
			code = "drop sequence %s.%s" % (self.owner, self.name)
		else:
			code = "drop sequence %s" % self.name
		if term:
			code += ";\n"
		else:
			code += "\n"
		return code

	def __xiter__(self, mode):
		if mode is None:
			yield ipipe.XMode(self, "create", "create statement", "the SQL script to create this sequence")
			yield ipipe.XMode(self, "createcopy", "create statement (exact copy)", "the SQL script to create this sequence (using the current value as the start value)")
			yield ipipe.XMode(self, "drop", "drop statement", "the SQL script to drop this sequence")
			yield ipipe.XMode(self, "referencedbyown", "referenced by own", "other objects (in this schema) depending on this sequence")
			yield ipipe.XMode(self, "referencedbydep", "referenced by all", "all other objects depending on this sequence")
			yield ipipe.XMode(self, "referencesown", "references own", "other objects (in this schema) on which this sequence depends")
			yield ipipe.XMode(self, "referencesdep", "references all", "all other objects on which this sequence depends")
		elif mode == "referencedbyown":
			for item in self.iterdependent(mode="drop", schema="own"):
				yield item
		elif mode == "referencedbydep":
			for item in self.iterdependent(mode="drop", schema="dep"):
				yield item
		elif mode == "referencesown":
			for item in self.iterdependent(mode="create", schema="own"):
				yield item
		elif mode == "referencesdep":
			for item in self.iterdependent(mode="create", schema="dep"):
				yield item
		elif mode == "drop":
			for item in self.dropddl().splitlines():
				yield item
		elif mode == "createcopy":
			for item in self.createddlcopy().splitlines():
				yield item
		else:
			for item in self.createddl().splitlines():
				yield item


def _fieldtype(rec, data_precision=None, data_scale=None, char_length=None):
	ftype = rec.data_type.lower()
	if data_precision is None:
		data_precision = rec.data_precision
	if data_scale is None:
		data_scale = rec.data_scale
	if char_length is None:
		char_length = rec.char_length

	fsize = data_precision
	fprec = data_scale
	if ftype == "number" and fprec == 0 and fsize is None:
		ftype = "integer"
	elif ftype == "number" and fprec is None and fsize is None:
		ftype = "number"
	elif ftype == "number" and fprec == 0:
		ftype = "number(%d)" % fsize
	elif ftype == "number":
		ftype = "number(%d, %d)" % (fsize, fprec)
	elif ftype == "raw":
		ftype = "raw(%d)" % rec.data_length
	else:
		if char_length != 0:
			fsize = char_length
		if fsize is not None:
			ftype += "(%d" % fsize
			if rec.char_used == "B":
				ftype += " byte"
			elif rec.char_used == "C":
				ftype += " char"
			if fprec is not None:
				ftype += ", %d" % fprec
			ftype += ")"
	return ftype


def _fielddefault(rec):
	if rec.data_default is not None and rec.data_default != "null\n":
		return rec.data_default.rstrip("\n")
	return "null"


class TableDefinition(MixinNormalDates, Definition):
	type = "table"

	def createddl(self, cursor=None, term=True):
		cursor = self.getcursor(cursor)
		cursor.execute("select * from all_tab_columns where owner=nvl(:owner, user) and table_name=:name order by column_id asc", owner=self.owner, name=self.name)
		recs = cursor.fetchall()
		if not recs:
			raise SQLObjectNotFoundError(self)
		if self.owner is not None:
			code = ["create table %s.%s\n(\n" % (self.owner, self.name)]
		else:
			code = ["create table %s\n(\n" % self.name]
		for (i, rec) in enumerate(recs):
			if i:
				code.append(",\n")
			code.append("\t%s %s" % (rec.column_name, _fieldtype(rec)))
			default = _fielddefault(rec)
			if default != "null":
				code.append(" default %s" % default)
			if rec.nullable == "N":
				code.append(" not null")
		if term:
			code.append("\n);\n")
		else:
			code.append("\n)\n")
		return "".join(code)

	def dropddl(self, cursor=None, term=True):
		if self.owner is not None:
			code = "drop table %s.%s" % (self.owner, self.name)
		else:
			code = "drop table %s" % self.name
		if term:
			code += ";\n"
		else:
			code += "\n"
		return code

	def itercolumns(self, cursor=None):
		"""
		<par>Generator that yields the definition of all columns of the
		<class>TableDefinition</class> <self/>.</par>
		"""
		cursor = self.getcursor(cursor)
		cursor.execute("select column_name from all_tab_columns where owner=nvl(:owner, user) and table_name=:name order by column_id", owner=self.owner, name=self.name)

		for rec in cursor.fetchall():
			yield ColumnDefinition("%s.%s" % (self.name, rec.column_name), self.owner, cursor)

	def iterrecords(self, cursor=None):
		cursor = self.getcursor(cursor)
		if self.owner is not None:
			query = "select * from %s.%s" % (self.owner, self.name)
		else:
			query = "select * from %s" % self.name
		cursor.execute(query)

		return iter(cursor)

	def __xiter__(self, mode):
		if mode is None:
			yield ipipe.XMode(self, "create", "create statement", "the SQL script to create this table")
			yield ipipe.XMode(self, "drop", "drop statement", "the SQL script to drop this table")
			yield ipipe.XMode(self, "columns", "columns", "the columns of this table")
			yield ipipe.XMode(self, "referencedbyown", "referenced by own", "other objects (in this schema) depending on this table")
			yield ipipe.XMode(self, "referencedbydep", "referenced by all", "all other objects depending on this table")
			yield ipipe.XMode(self, "referencesown", "references own", "other objects (in this schema) on which this table depends")
			yield ipipe.XMode(self, "referencesdep", "references all", "all other objects on which this table depends")
			yield ipipe.XMode(self, "records", "records", "records in this table")
		elif mode == "referencedbyown":
			for item in self.iterdependent(mode="drop", schema="own"):
				yield item
		elif mode == "referencedbydep":
			for item in self.iterdependent(mode="drop", schema="dep"):
				yield item
		elif mode == "referencesown":
			for item in self.iterdependent(mode="create", schema="own"):
				yield item
		elif mode == "referencesdep":
			for item in self.iterdependent(mode="create", schema="dep"):
				yield item
		elif mode == "drop":
			for item in self.dropddl().splitlines():
				yield item
		elif mode == "columns":
			for item in self.itercolumns():
				yield item
		elif mode == "records":
			for item in self.iterrecords():
				yield item
		else:
			for item in self.createddl().splitlines():
				yield item


class PKDefinition(Definition):
	type = "pk"

	def createddl(self, cursor=None, term=True):
		cursor = self.getcursor(cursor)
		cursor.execute("select decode(owner, user, null, owner) as owner, constraint_name, table_name, r_owner, r_constraint_name from all_constraints where constraint_type='P' and owner=nvl(:owner, user) and constraint_name=:name", owner=self.owner, name=self.name)
		rec2 = cursor.fetchone()
		if rec2 is None:
			raise SQLObjectNotFoundError(self)
		cursor.execute("select column_name from all_cons_columns where owner=nvl(:owner, user) and constraint_name=:name", owner=self.owner, name=self.name)
		if rec2.owner is not None:
			name = "%s.%s" % (rec2.owner, rec2.table_name)
		else:
			name = rec2.table_name
		code = "alter table %s add constraint %s primary key(%s)" % (name, self.name, ", ".join(r.column_name for r in cursor))
		if term:
			code += ";\n"
		else:
			code += "\n"
		return code

	def dropddl(self, cursor=None, term=True):
		cursor = self.getcursor(cursor)
		cursor.execute("select decode(owner, user, null, owner) as owner, table_name from all_constraints where owner=nvl(:owner, user) and constraint_name=:name", owner=self.owner, name=self.name)
		rec = cursor.fetchone()
		if rec.owner is not None:
			name = "%s.%s" % (rec.owner, rec.table_name)
		else:
			name = rec.table_name
		code = "alter table %s drop constraint %s" % (name, self.name)
		if term:
			code += ";\n"
		else:
			code += "\n"
		return code

	def cdate(self, cursor=None):
		cursor = self.getcursor(cursor)
		cursor.execute("select last_change from all_constraints where constraint_type='P' and constraint_name=:name and owner=nvl(:owner, user)", name=self.name, owner=self.owner)
		row = cursor.fetchone()
		if row is None:
			raise SQLObjectNotFoundError(self)
		return None

	def udate(self, cursor=None):
		cursor = self.getcursor(cursor)
		cursor.execute("select last_change from all_constraints where constraint_type='P' and constraint_name=:name and owner=nvl(:owner, user)", name=self.name, owner=self.owner)
		row = cursor.fetchone()
		if row is None:
			raise SQLObjectNotFoundError(self)
		return row.last_change


class CommentDefinition(Definition):
	type = "comment"

	def iterdependent(self, cursor=None, done=None, mode="create", schema="dep"):
		cursor = self.getcursor(cursor)
		if done is None:
			done = set()
		if self not in done:
			if mode == "create":
				for definition in TableDefinition(self.name.split(".")[0], self.owner, cursor).iterdependent(cursor, done, mode):
					yield definition
			done.add(self)
			yield self

	def createddl(self, cursor=None, term=True):
		cursor = self.getcursor(cursor)
		tcname = self.name.split(".")
		cursor.execute("select comments from all_col_comments where owner=nvl(:owner, user) and table_name=:tname and column_name=:cname", owner=self.owner, tname=tcname[0], cname=tcname[1])
		row = cursor.fetchone()
		if row is None:
			raise SQLObjectNotFoundError(self)

		if self.owner is not None:
			name = "%s.%s" % (self.owner, self.name)
		else:
			name = self.name
		if row.comments:
			code = "comment on column %s is %s" % (name, formatstring(row.comments, latin1=True))
		else:
			code = "comment on column %s is ''" % name
		if term:
			code += ";\n"
		else:
			code += "\n"
		return code

	def dropddl(self, cursor=None, term=True):
		# will be dropped with the table
		return ""

	def cdate(self, cursor=None):
		return None

	def udate(self, cursor=None):
		return None


class FKDefinition(Definition):
	type = "fk"

	def createddl(self, cursor=None, term=True):
		cursor = self.getcursor(cursor)
		# Add constraint_type to the query, so we don't pick up another constraint by accident
		cursor.execute("select decode(r_owner, user, null, r_owner) as r_owner, r_constraint_name, table_name from all_constraints where constraint_type='R' and owner=nvl(:owner, user) and constraint_name=:name", owner=self.owner, name=self.name)
		rec = cursor.fetchone()
		if rec is None:
			raise SQLObjectNotFoundError(self)
		cursor.execute("select column_name from all_cons_columns where owner=nvl(:owner, user) and constraint_name=:name order by position", owner=self.owner, name=self.name)
		fields1 = ", ".join(r.column_name for r in cursor)
		cursor.execute("select table_name, column_name from all_cons_columns where owner=nvl(:owner, user) and constraint_name=:name order by position", owner=rec.r_owner, name=rec.r_constraint_name)
		if rec.r_owner is not None:
			fields2 = ", ".join("%s.%s(%s)" % (rec.r_owner, r.table_name, r.column_name) for r in cursor)
		else:
			fields2 = ", ".join("%s(%s)" % (r.table_name, r.column_name) for r in cursor)
		if self.owner is not None:
			name = "%s.%s" % (self.owner, rec.table_name)
		else:
			name = rec.table_name
		code = "alter table %s add constraint %s foreign key (%s) references %s" % (name, self.name, fields1, fields2)
		if term:
			code += ";\n"
		else:
			code += "\n"
		return code

	def _ddl(self, cursor, cmd, term):
		cursor.execute("select table_name from all_constraints where owner=nvl(:owner, user) and constraint_name=:name", owner=self.owner, name=self.name)
		rec = cursor.fetchone()
		if rec is None:
			raise SQLObjectNotFoundError(self)
		if self.owner is not None:
			name = "%s.%s" % (self.owner, rec.table_name)
		else:
			name = rec.table_name
		code = "alter table %s %s constraint %s" % (name, cmd, self.name)
		if term:
			code += ";\n"
		else:
			code += "\n"
		return code

	def dropddl(self, cursor=None, term=True):
		cursor = self.getcursor(cursor)
		return self._ddl(cursor, "drop", term)

	def enableddl(self, cursor=None, term=True):
		cursor = self.getcursor(cursor)
		return self._ddl(cursor, "enable", term)

	def disableddl(self, cursor=None, term=True):
		cursor = self.getcursor(cursor)
		return self._ddl(cursor, "disable", term)

	def cdate(self, cursor=None):
		cursor = self.getcursor(cursor)
		cursor.execute("select last_change from all_constraints where constraint_type='R' and constraint_name=:name and owner=nvl(:owner, user)", name=self.name, owner=self.owner)
		row = cursor.fetchone()
		if row is None:
			raise SQLObjectNotFoundError(self)
		return None

	def udate(self, cursor=None):
		cursor = self.getcursor(cursor)
		cursor.execute("select last_change from all_constraints where constraint_type='R' and constraint_name=:name and owner=nvl(:owner, user)", name=self.name, owner=self.owner)
		row = cursor.fetchone()
		if row is None:
			raise SQLObjectNotFoundError(self)
		return row.last_change


class IndexDefinition(MixinNormalDates, Definition):
	type = "index"

	def createddl(self, cursor, term=True):
		cursor.execute("select count(*) as count from all_constraints where constraint_type in ('U', 'P') and owner=nvl(:owner, user) and constraint_name=:name", owner=self.owner, name=self.name)
		rec = cursor.fetchone() # This is a constraint, not just an index
		if rec.count:
			raise SQLObjectNotFoundError(self)
		cursor.execute("select index_name, table_name, uniqueness from all_indexes where generated='N' and table_owner=nvl(:owner, user) and index_name=:name", owner=self.owner, name=self.name)
		rec = cursor.fetchone()
		if rec is None:
			raise SQLObjectNotFoundError(self)
		if self.owner is not None:
			name = "%s.%s" % (self.owner, rec.table_name)
		else:
			name = rec.table_name
		if rec.uniqueness == "UNIQUE":
			unique = " unique"
		else:
			unique = ""
		cursor.execute("select aie.column_expression, aic.column_name from all_ind_columns aic, all_ind_expressions aie where aic.table_owner=aie.table_owner(+) and aic.index_name=aie.index_name(+) and aic.column_position=aie.column_position(+) and aic.table_owner=nvl(:owner, user) and aic.index_name=:name order by aic.column_position", owner=self.owner, name=self.name)
		code = "create%s index %s on %s (%s)" % (unique, self.name, name, ", ".join(r.column_expression or r.column_name for r in cursor))
		if term:
			code += ";\n"
		else:
			code += "\n"
		return code

	def dropddl(self, cursor, term=True):
		cursor.execute("select index_name from all_indexes where generated='N' and table_owner=nvl(:owner, user) and index_name=:name", owner=self.owner, name=self.name)
		rec = cursor.fetchone()
		if rec is None:
			raise SQLObjectNotFoundError(self)
		if self.owner is not None:
			name = "%s.%s" % (self.owner, rec.index_name)
		else:
			name = rec.index_name
		code = "drop index %s" % name
		if term:
			code += ";\n"
		else:
			code += "\n"
		return code


class UniqueDefinition(Definition):
	type = "unique"

	def createddl(self, cursor=None, term=True):
		cursor = self.getcursor(cursor)
		# Add constraint_type to the query, so we don't pick up another constraint by accident
		cursor.execute("select table_name from all_constraints where constraint_type='U' and owner=nvl(:owner, user) and constraint_name=:name", owner=self.owner, name=self.name)
		rec = cursor.fetchone()
		if rec is None:
			raise SQLObjectNotFoundError(self)
		if self.owner is not None:
			name = "%s.%s" % (self.owner, rec.table_name)
		else:
			name = rec.table_name
		cursor.execute("select column_name from all_cons_columns where owner=nvl(:owner, user) and constraint_name=:name", owner=self.owner, name=self.name)
		code = "alter table %s add constraint %s unique(%s)" % (name, self.name, ", ".join(r.column_name for r in cursor))
		if term:
			code += ";\n"
		else:
			code += "\n"
		return code

	def dropddl(self, cursor=None, term=True):
		cursor = self.getcursor(cursor)
		cursor.execute("select table_name from all_constraints where constraint_type='U' and owner=nvl(:owner, user) and constraint_name=:name", owner=self.owner, name=self.name)
		rec = cursor.fetchone()
		if rec is None:
			raise SQLObjectNotFoundError(self)
		if self.owner is not None:
			name = "%s.%s" % (self.owner, rec.table_name)
		else:
			name = rec.table_name
		code = "alter table %s drop constraint %s" % (name, self.name)
		if term:
			code += ";\n"
		else:
			code += "\n"
		return code

	def cdate(self, cursor=None):
		cursor = self.getcursor(cursor)
		cursor.execute("select last_change from all_constraints where constraint_type='U' and constraint_name=:name and owner=nvl(:owner, user)", name=self.name, owner=self.owner)
		row = cursor.fetchone()
		if row is None:
			raise SQLObjectNotFoundError(self)
		return None

	def udate(self, cursor=None):
		cursor = self.getcursor(cursor)
		cursor.execute("select last_change from all_constraints where constraint_type='U' and constraint_name=:name and owner=nvl(:owner, user)", name=self.name, owner=self.owner)
		row = cursor.fetchone()
		if row is None:
			raise SQLObjectNotFoundError(self)
		return row.last_change


class SynonymDefinition(Definition):
	type = "synonym"

	def createddl(self, cursor=None, term=True):
		cursor = self.getcursor(cursor)
		cursor.execute("select table_owner, table_name, db_link from all_synonyms where owner=nvl(:owner, user) and synonym_name=:name", owner=self.owner, name=self.name)
		rec = cursor.fetchone()
		if rec is None:
			raise SQLObjectNotFoundError(self)
		owner = self.owner
		if owner == "PUBLIC":
			public = "public "
			owner = None
		else:
			public = ""
		if owner is not None:
			name = "%s.%s" % (owner, self.name)
		else:
			name = self.name

		if rec.table_owner is not None:
			name2 = "%s.%s" % (rec.table_owner, rec.table_name)
		else:
			name2 = rec.table_name
		code = "create or replace %ssynonym %s for %s" % (public, name, name2)
		if rec.db_link is not None:
			code += "@%s" % rec.db_link
		if term:
			code += ";\n"
		else:
			code += "\n"
		return code

	def dropddl(self, cursor=None, term=True):
		owner = self.owner
		if owner == "PUBLIC":
			public = "public "
			owner = None
		else:
			public = ""
		if owner is not None:
			name = "%s.%s" % (owner, self.name)
		else:
			name = self.name
		code = "drop %ssynonym %s" % (public, name)
		if term:
			code += ";\n"
		else:
			code += "\n"
		return code

	def cdate(self, cursor=None):
		return None

	def udate(self, cursor=None):
		return None


class ViewDefinition(MixinNormalDates, Definition):
	type = "view"

	def createddl(self, cursor=None, term=True):
		cursor = self.getcursor(cursor)
		cursor.execute("select text from all_views where owner=nvl(:owner, user) and view_name=:name", owner=self.owner, name=self.name)
		rec = cursor.fetchone()
		if rec is None:
			raise SQLObjectNotFoundError(self)
		if self.owner is not None:
			name = "%s.%s" % (self.owner, self.name)
		else:
			name = self.name
		code = "\n".join(line.rstrip() for line in rec.text.strip().splitlines()) # Strip trailing whitespace
		code = "create or replace view %s as\n\t%s" % (self.name, code)
		if term:
			code += "\n/\n"
		else:
			code += "\n"
		return code

	def dropddl(self, cursor=None, term=True):
		if self.owner is not None:
			code = "drop view %s.%s" % (self.owner, self.name)
		else:
			code = "drop view %s" % self.name
		if term:
			code += ";\n"
		else:
			code += "\n"
		return code

	def iterrecords(self, cursor=None):
			cursor = self.getcursor(cursor)
			if self.owner is not None:
				query = "select * from %s.%s" % (self.owner, self.name)
			else:
				query = "select * from %s" % self.name
			cursor.execute(query)
			return iter(cursor)

	def __xiter__(self, mode):
		if mode is None:
			yield ipipe.XMode(self, "create", "create statement", "the SQL script to create this view")
			yield ipipe.XMode(self, "drop", "drop statement", "the SQL script to drop this view")
			yield ipipe.XMode(self, "referencedbyown", "referenced by own", "other objects (in this schema) depending on this view")
			yield ipipe.XMode(self, "referencedbydep", "referenced by all", "all other objects depending on this view")
			yield ipipe.XMode(self, "referencesown", "references own", "other objects (in this schema) on which this view depends")
			yield ipipe.XMode(self, "referencesdep", "references all", "all other objects on which this view depends")
			yield ipipe.XMode(self, "records", "records", "records in this view")
		elif mode == "referencedbyown":
			for item in self.iterdependent(mode="drop", schema="own"):
				yield item
		elif mode == "referencedbydep":
			for item in self.iterdependent(mode="drop", schema="dep"):
				yield item
		elif mode == "referencesown":
			for item in self.iterdependent(mode="create", schema="own"):
				yield item
		elif mode == "referencesdep":
			for item in self.iterdependent(mode="create", schema="dep"):
				yield item
		elif mode == "drop":
			for item in self.dropddl().splitlines():
				yield item
		elif mode == "records":
			for item in self.iterrecords():
				yield item
		else:
			for item in self.createddl().splitlines():
				yield item


class LibraryDefinition(Definition):
	type = "library"

	def createddl(self, cursor=None, term=True):
		cursor = self.getcursor(cursor)
		cursor.execute("select file_spec from all_libraries where owner=nvl(:owner, user) and library_name=:name", owner=self.owner, name=self.name)
		rec = cursor.fetchone()
		if rec is None:
			raise SQLObjectNotFoundError(self)
		if self.owner is not None:
			name = "%s.%s" % (self.owner, self.name)
		else:
			name = self.name
		return "create or replace library %s as %r" % (self.name, rec.file_spec)
		if term:
			code += ";\n"
		else:
			code += "\n"
		return code

	def dropddl(self, cursor=None, term=True):
		if self.owner is not None:
			code = "drop library %s.%s" % (self.owner, self.name)
		else:
			code = "drop library %s" % self.name
		if term:
			code += ";\n"
		else:
			code += "\n"
		return code


class FunctionDefinition(MixinNormalDates, MixinCodeDDL, Definition):
	type = "function"


class ProcedureDefinition(MixinNormalDates, MixinCodeDDL, Definition):
	type = "procedure"


class PackageDefinition(MixinNormalDates, MixinCodeDDL, Definition):
	type = "package"


class PackageBodyDefinition(MixinNormalDates, MixinCodeDDL, Definition):
	type = "package body"


class TypeDefinition(MixinNormalDates, MixinCodeDDL, Definition):
	type = "type"


class TriggerDefinition(MixinNormalDates, MixinCodeDDL, Definition):
	type = "trigger"


class JavaSourceDefinition(MixinNormalDates, Definition):
	type = "java source"

	def createddl(self, cursor=None, term=True):
		cursor = self.getcursor(cursor)
		cursor.execute("select text from all_source where type='JAVA SOURCE' and owner=nvl(:owner, user) and name=:name order by line", owner=self.owner, name=self.name)
		code = "\n".join((rec.text or "").rstrip() for rec in cursor)
		code = code.strip()

		if self.owner is not None:
			name = "%s.%s" % (self.owner, self.name)
		else:
			name = self.name

		code = "create or replace and compile java source named %s as\n%s\n" % (name, code)
		if term:
			code += "/\n"
		return code

	def dropddl(self, cursor=None, term=True):
		if self.owner is not None:
			name = "%s.%s" % (self.owner, self.name)
		else:
			name = self.name
		code = "drop java source %s" % name
		if term:
			code += ";\n"
		else:
			code += "\n"
		return code


class ColumnDefinition(Definition):
	type = "column"

	def addddl(self, cursor=None, term=True):
		cursor = self.getcursor(cursor)
		name = self.name.split(".")
		cursor.execute("select * from all_tab_columns where owner=nvl(:owner, user) and table_name=:table_name and column_name=:column_name", owner=self.owner, table_name=name[0], column_name=name[1])
		rec = cursor.fetchone()
		if rec is None:
			raise SQLObjectNotFoundError(self)
		if self.owner is not None:
			code = ["alter table %s.%s add %s" % (self.owner, name[0], name[1])]
		else:
			code = ["alter table %s add %s" % (name[0], name[1])]
		code.append(" %s" % _fieldtype(rec))
		default = _fielddefault(rec)
		if default != "null":
			code.append(" default %s" % default)
		if rec.nullable == "N":
			code.append(" not null")
		if term:
			code.append(";\n")
		else:
			code.append("\n")
		return "".join(code)

	def modifyddl(self, cursor, cursorold, cursornew, term=True):
		cursor = self.getcursor(cursor)
		name = self.name.split(".")
		def fetch(cursor):
			cursor.execute("select * from all_tab_columns where owner=nvl(:owner, user) and table_name=:table_name and column_name=:column_name", owner=self.owner, table_name=name[0], column_name=name[1])
			rec = cursor.fetchone()
			if rec is None:
				raise SQLObjectNotFoundError(self)
			return rec

		rec = fetch(cursor)
		recold = fetch(cursorold)
		recnew = fetch(cursornew)

		if self.owner is not None:
			code = ["alter table %s.%s modify %s" % (self.owner, name[0], name[1])]
		else:
			code = ["alter table %s modify %s" % (name[0], name[1])]
		# Has the type changed?
		if recold.data_precision != recnew.data_precision or recold.data_length != recnew.data_length or recold.data_scale != recnew.data_scale or recold.char_length != recnew.char_length or recold.data_type != recnew.data_type or recold.data_type_owner != recnew.data_type_owner:
			# Has only the size changed?
			if rec.data_type == recold.data_type == recnew.data_type and rec.data_type_owner == recold.data_type_owner == recnew.data_type_owner:
				try:
					data_precision = max(r.data_precision for r in (rec, recold, recnew) if r.data_precision is not None)
				except ValueError:
					data_precision = None
				try:
					data_scale = max(r.data_scale for r in (rec, recold, recnew) if r.data_scale is not None)
				except ValueError:
					data_scale = None
				try:
					char_length = max(r.char_length for r in (rec, recold, recnew) if r.char_length is not None)
				except ValueError:
					char_length = None
				code.append(" %s" % _fieldtype(rec, data_precision=data_precision, data_scale=data_scale, char_length=char_length))
			else: # The type has changed too
				if recnew.data_type != rec.data_type or recnew.data_type_owner != rec.data_type_owner:
					raise ConflictError(self, "data_type unmergeable")
				elif recnew.data_precision != rec.data_precision:
					raise ConflictError(self, "data_precision unmergeable")
				elif recnew.data_scale != rec.data_scale:
					raise ConflictError(self, "data_scale unmergeable")
				elif recnew.char_length != rec.char_length:
					raise ConflictError(self, "char_length unmergeable")
				code.append(" %s" % _fieldtype(recnew))

		# Has the default changed?
		default = _fielddefault(rec)
		olddefault = _fielddefault(recold)
		newdefault = _fielddefault(recnew)
		if olddefault != newdefault:
			if newdefault != default:
				raise ConflictError(self, "default value unmergable")
			code.append(" default %s" % newdefault)

		# Check nullability
		if recold.nullable != recnew.nullable:
			if recnew.nullable == "N":
				code.append(" not null")
			else:
				code.append(" null")

		if term:
			code.append(";\n")
		else:
			code.append("\n")

		return "".join(code)

	def dropddl(self, cursor=None, term=True):
		cursor = self.getcursor(cursor)
		name = self.name.split(".")
		if self.owner is not None:
			code = "alter table %s.%s drop column %s" % (self.owner, name[0], name[1])
		else:
			code = "alter table %s drop column %s" % (name[0], name[1])
		if term:
			code += ";\n"
		else:
			code += "\n"
		return code

	def cdate(self, cursor):
		cursor.execute("select created from all_objects where lower(object_type)='table' and object_name=:name and owner=nvl(:owner, user)", name=self.name.split(".")[0], owner=self.owner)
		row = cursor.fetchone()
		if row is None:
			raise SQLObjectNotFoundError(self)
		return row.created

	def udate(self, cursor):
		cursor.execute("select last_ddl_time from all_objects where lower(object_type)='table' and object_name=:name and owner=nvl(:owner, user)", name=self.name.split(".")[0], owner=self.owner)
		row = cursor.fetchone()
		if row is None:
			raise SQLObjectNotFoundError(self)
		return row.last_ddl_time

	def __xiter__(self, mode):
		return None
