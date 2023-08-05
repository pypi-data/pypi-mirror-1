#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

## Copyright 2004-2006 by LivingLogic AG, Bayreuth/Germany.
## Copyright 2004-2006 by Walter Dörwald
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

from ll import misc

try:
	from IPython.Extensions import astyle
except ImportError:
	from ll import astyle


# ipipe support
try:
	from IPython.Extensions import ipipe
except ImportError:
	ipipe = None


style_connection = astyle.style_url


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
	def __init__(self, connection, class_, schema, count):
		self.connection = connection
		self.class_ = class_
		self.type = class_.type
		self.schema = schema
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
		return self.class_.iterdefinitions(self.connection, self.schema)


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
		elif mode == "cell":
			yield (style_connection, self.connectstring())
		else:
			yield (astyle.style_default, repr(self))

	def __xiter__(self, mode):
		if mode is None:
			yield ipipe.XMode(self, "schema", "schema", "object types in this schema")
			yield ipipe.XMode(self, "objectscreateuser", "objects (create order)", "all objects belonging to this user (in create order)")
			yield ipipe.XMode(self, "objectsdropuser", "objects (drop order)", "all objects belonging to this user (in drop order)")
			yield ipipe.XMode(self, "objectsflatuser", "objects (unordered)", "all objects belonging to this user (unordered)")
			yield ipipe.XMode(self, "objectscreateall", "all objects (create order)", "all objects in all schemas (in create order)")
			yield ipipe.XMode(self, "objectsdropall", "all objects (drop order)", "all objects in all schemas (in drop order)")
			yield ipipe.XMode(self, "objectsflatall", "all objects (unordered)", "all objects in all schemas (unordered)")
		elif mode == "objectscreateuser":
			for item in self.iterdefinitions("create", "user"):
				yield item
		elif mode == "objectsdropuser":
			for item in self.iterdefinitions("drop", "user"):
				yield item
		elif mode == "objectsflatuser":
			for item in self.iterdefinitions("flat", "user"):
				yield item
		elif mode == "objectscreateall":
			for item in self.iterdefinitions("create", "all"):
				yield item
		elif mode == "objectsdropall":
			for item in self.iterdefinitions("drop", "all"):
				yield item
		elif mode == "objectsflatall":
			for item in self.iterdefinitions("flat", "all"):
				yield item
		else:
			for item in self.iterschema():
				yield item

	def iterschema(self, schema="user"):
		cursor = self.cursor()
		if schema == "all":
			cursor.execute("select object_type as type, count(*) as count from all_objects group by object_type")
		else:
			cursor.execute("select object_type as type, count(*) as count from user_objects group by object_type")
		for row in cursor.fetchall():
			class_ = Definition.name2type.get(row.type.lower(), None)
			if class_ is not None:
				yield _AllTypes(self, class_, schema, row.count)

	def iterdefinitions(self, mode="create", schema="user"):
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
		<term><lit>"user"</lit></term><item>Only definitions belonging to the current
		user (and those definitions these depend on) will be yielded.</item>
		<term><lit>"all"</lit></term><item>All definitions from all users will be
		yielded.</item>
		</dlist>
		"""
		if mode not in ("create", "drop", "flat"):
			raise UnknownModeError(mode)

		if schema not in ("user", "all"):
			raise UnknownSchemaError(schema)

		done = set()

		cursor = self.cursor()

		def do(definition):
			if mode == "create":
				for subdefinition in definition.iterreferencesall(self, done):
					yield subdefinition
			elif mode == "drop":
				for subdefinition in definition.iterreferencedbyall(self, done):
					yield subdefinition
			else:
				if definition not in done:
					done.add(definition)
					yield definition

		def dosequences():
			# select * from all_sequences where sequence_owner=nvl(:owner, user) and sequence_name=:name
			if schema == "all":
				cursor.execute("select decode(sequence_owner, user, null, sequence_owner) as sequence_owner, sequence_name from all_sequences")
			else:
				cursor.execute("select null as sequence_owner, sequence_name from user_sequences")
			for rec in cursor.fetchall():
				for definition in do(SequenceDefinition(rec.sequence_name, rec.sequence_owner, self)):
					yield definition

		def dotables():
			if schema == "all":
				cursor.execute("select decode(owner, user, null, owner) as owner, table_name from all_tables")
			else:
				cursor.execute("select null as owner, table_name from user_tables")
			for rec in cursor.fetchall():
				tabledefinition = TableDefinition(rec.table_name, rec.owner, self)
				if mode == "create" or mode == "flat":
					for definition in do(tabledefinition):
						yield definition
	
				if not tabledefinition.ismview(self):
					# Primary key
					if schema == "all":
						cursor.execute("select decode(owner, user, null, owner) as owner, constraint_name from all_constraints where constraint_type='P' and owner=:owner and table_name=:name", owner=rec.owner, name=rec.table_name)
					else:
						cursor.execute("select null as owner, constraint_name from user_constraints where constraint_type='P' and table_name=:name", name=rec.table_name)
					for rec2 in cursor.fetchall():
						for definition in do(PKDefinition(rec2.constraint_name, rec2.owner, self)):
							yield definition
	
					# Comments
					if schema == "all":
						cursor.execute("select column_name from all_tab_columns where owner=:owner and table_name=:name order by column_id", owner=rec.owner, name=rec.table_name)
					else:
						cursor.execute("select column_name from user_tab_columns where table_name=:name order by column_id", name=rec.table_name)
					for rec2 in cursor.fetchall():
						# No dependency checks neccessary, but use do anyway
						for definition in do(CommentDefinition("%s.%s" % (rec.table_name, rec2.column_name), rec.owner, self)):
							yield definition

				if mode == "drop":
					for definition in do(tabledefinition):
						yield definition

		def doconstraints():
			if schema == "all":
				cursor.execute("select constraint_type, decode(owner, user, null, owner) as owner, constraint_name from all_constraints where constraint_type in ('R', 'U') order by owner, table_name, constraint_type, constraint_name")
			else:
				cursor.execute("select constraint_type, null as owner, constraint_name from user_constraints where constraint_type in ('R', 'U') order by table_name, constraint_type, constraint_name")
			types = {"U": UniqueDefinition, "R": FKDefinition}
			for rec in cursor.fetchall():
				for definition in do(types[rec.constraint_type](rec.constraint_name, rec.owner, self)):
					yield definition

		def doindexes():
			if schema == "all":
				cursor.execute("select decode(owner, user, null, owner) as owner, index_name from all_indexes where index_type in ('NORMAL', 'FUNCTION-BASED NORMAL') order by owner, table_name, index_name")
			else:
				cursor.execute("select null as owner, index_name from user_indexes where index_type in ('NORMAL', 'FUNCTION-BASED NORMAL') order by table_name, index_name")
			for rec in cursor.fetchall():
				for definition in do(IndexDefinition(rec.index_name, rec.owner, self)):
					yield definition

		def dosynonyms():
			if schema == "all":
				cursor.execute("select decode(owner, user, null, owner) as owner, synonym_name from all_synonyms")
			else:
				cursor.execute("select null as owner, synonym_name from user_synonyms")
			for rec in cursor.fetchall():
				for definition in do(SynonymDefinition(rec.synonym_name, rec.owner, self)):
					yield definition

		def doviews():
			if schema == "all":
				cursor.execute("select decode(owner, user, null, owner) as owner, view_name from all_views")
			else:
				cursor.execute("select null as owner, view_name from user_views")
			for rec in cursor.fetchall():
				for definition in do(ViewDefinition(rec.view_name, rec.owner, self)):
					yield definition

		def domviews():
			if schema == "all":
				cursor.execute("select decode(owner, user, null, owner) as owner, mview_name from all_mviews")
			else:
				cursor.execute("select null as owner, mview_name from user_mviews")
			for rec in cursor.fetchall():
				for definition in do(MaterializedViewDefinition(rec.mview_name, rec.owner, self)):
					yield definition

		def docode():
			for type in (FunctionDefinition, ProcedureDefinition, PackageDefinition, PackageBodyDefinition, TypeDefinition, TriggerDefinition, JavaSourceDefinition):
				if schema == "all":
					cursor.execute("select decode(owner, user, null, owner) as owner, object_name from all_objects where lower(object_type)=lower(:type)", type=type.type)
				else:
					cursor.execute("select null as owner, object_name from user_objects where lower(object_type)=lower(:type)", type=type.type)
				for rec in cursor.fetchall():
					for definition in do(type(rec.object_name, rec.owner, self)):
						yield definition

		funcs = (dosequences, dotables, doconstraints, doindexes, dosynonyms, doviews, domviews, docode)
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
	def cdate(self, connection=None):
		(connection, cursor) = self.getcursor(connection)
		cursor.execute("select created from all_objects where lower(object_type)=:type and object_name=:name and owner=nvl(:owner, user)", type=self.__class__.type, name=self.name, owner=self.owner)
		row = cursor.fetchone()
		if row is None:
			raise SQLObjectNotFoundError(self)
		return row.created

	def udate(self, connection=None):
		(connection, cursor) = self.getcursor(connection)
		cursor.execute("select last_ddl_time from all_objects where lower(object_type)=:type and object_name=:name and owner=nvl(:owner, user)", type=self.__class__.type, name=self.name, owner=self.owner)
		row = cursor.fetchone()
		if row is None:
			raise SQLObjectNotFoundError(self)
		return row.last_ddl_time


class MixinCodeDDL(object):
	def createddl(self, connection=None, term=True):
		(connection, cursor) = self.getcursor(connection)
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

	def dropddl(self, connection=None, term=True):
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


def getname(name, owner):
	parts = []
	if owner is not None:
		if owner != owner.upper():
			parts.append('"%s"' % owner)
		else:
			parts.append(owner)
	for part in name.split("."):
		if part != part.upper():
			parts.append('"%s"' % part)
		else:
			parts.append(part)
	return ".".join(parts)


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

	def __init__(self, name, owner=None, connection=None):
		self.name = name
		self.owner = owner
		self.connection = connection

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

	def getname(self):
		return getname(self.name, self.owner)

	@misc.notimplemented
	def createddl(self, connection=None, term=True):
		"""
		&sql; to create this object.
		"""

	@misc.notimplemented
	def dropddl(self, connection=None, term=True):
		"""
		&sql; to drop this object
		"""

	@misc.notimplemented
	def cdate(self, connection=None):
		"""
		Return a <class>datetime.datetime</class> object with the creation date of
		<self/> in the database specified by <arg>connection</arg> (or <lit>None</lit>
		if such information is not available).
		"""

	@misc.notimplemented
	def udate(self, connection=None):
		"""
		Return a <class>datetime.datetime</class> object with the last modification
		date of <self/> in the database specified by <arg>connection</arg>
		(or <lit>None</lit> if such information is not available).
		"""

	def iterreferences(self, connection=None):
		"""
		<par>Definitions directly used by <self/>.</par>

		<par>If <arg>connection</arg> is not <lit>None</lit> it will be used as
		the database connection from which to fetch data. If <arg>connection</arg> is <lit>None</lit>
		the connection from which <self/> has been extracted will be used. If
		there is not such connection, you'll get an exception.</par>
		"""
		(connection, cursor) = self.getcursor(connection)
		cursor.execute("select referenced_type, decode(referenced_owner, user, null, referenced_owner) as referenced_owner, referenced_name from all_dependencies where type=upper(:type) and name=:name and owner=nvl(:owner, user) and type != 'NON-EXISTENT'", type=self.type, name=self.name, owner=self.owner)
		for rec in cursor:
			try:
				type = Definition.name2type[rec.referenced_type.lower()]
			except KeyError:
				pass # FIXME: Issue a warning?
			else:
				yield type(rec.referenced_name, rec.referenced_owner, connection)

	def iterreferencesall(self, connection=None, done=None):
		"""
		<par>All definitions used by <self/> (recursively).</par>

		<par>For the meaning of <arg>connection</arg> see
		<pyref method="iterreferences"><method>iterreferences</method></pyref>.</par>

		<par><arg>done</arg> is used internally and shouldn't be passed.</par>
		"""
		if done is None:
			done = set()
		if self not in done:
			done.add(self)
			for definition in self.iterreferences(connection):
				for subdefinition in definition.iterreferencesall(connection, done):
					yield subdefinition
			yield self

	def iterreferencedby(self, connection=None):
		"""
		<par>Definitions using <self/>.</par>

		<par>For the meaning of <arg>connection</arg> see
		<pyref method="iterreferences"><method>iterreferences</method></pyref>.</par>
		"""
		(connection, cursor) = self.getcursor(connection)
		cursor.execute("select type, decode(owner, user, null, owner) as owner, name from all_dependencies where referenced_type=upper(:type) and referenced_name=:name and referenced_owner=nvl(:owner, user) and type != 'NON-EXISTENT'", type=self.type, name=self.name, owner=self.owner)
		for rec in cursor:
			try:
				type = Definition.name2type[rec.type.lower()]
			except KeyError:
				pass # FIXME: Issue a warning?
			else:
				yield type(rec.name, rec.owner, connection)

	def iterreferencedbyall(self, connection=None, done=None):
		"""
		<par>All definitions depending on <self/> (recursively).</par>

		<par>For the meaning of <arg>connection</arg> see
		<pyref method="iterreferences"><method>iterreferences</method></pyref>.</par>

		<par><arg>done</arg> is used internally and shouldn't be passed.</par>
		"""
		if done is None:
			done = set()
		if self not in done:
			done.add(self)
			for definition in self.iterreferencedby(connection):
				for subdefinition in definition.iterreferencedbyall(connection, done):
					yield subdefinition
			yield self

	def getconnection(self, connection):
		if connection is None:
			connection = self.connection
		if connection is None:
			raise TypeError("no connection available")
		return connection

	def getcursor(self, connection):
		connection = self.getconnection(connection)
		return (connection, connection.cursor())

	def getconnectstring(self):
		if self.connection:
			return self.connection.connectstring()
		return None
	connectstring = property(getconnectstring)

	@classmethod
	def iterdefinitions(cls, connection, schema="user"):
		"""
		<par>Generator that yields the definition of all objects of this class in the database
		schema of <arg>cursor</arg>.</par>
		"""
		cursor = connection.cursor()
		if schema=="all":
			cursor.execute("select decode(owner, user, null, owner) as owner, object_name from all_objects where lower(object_type) = :type", type=cls.type)
		else:
			cursor.execute("select null as owner, object_name from user_objects where lower(object_type) = :type", type=cls.type)
		return (cls(row.object_name, row.owner, connection) for row in cursor)

	def __xiter__(self, mode):
		if mode is None:
			yield ipipe.XMode(self, "create", "create statement", "the SQL script to create this %s" % self.type)
			yield ipipe.XMode(self, "drop", "drop statement", "the SQL script to drop this %s" % self.type)
			yield ipipe.XMode(self, "referencedby", "referenced by", "other objects depending on this %s" % self.type)
			yield ipipe.XMode(self, "references", "references", "other objects on which this %s depends" % self.type)
			yield ipipe.XMode(self, "referencedbyall", "referenced by all", "all other objects depending on this %s" % self.type)
			yield ipipe.XMode(self, "referencesall", "references all", "all other objects on which this %s depends" % self.type)
		elif mode == "referencedby":
			for item in self.iterreferencedby():
				yield item
		elif mode == "references":
			for item in self.iterreferences():
				yield item
		elif mode == "referencedbyall":
			for item in self.iterreferencedbyall():
				yield item
		elif mode == "referencesall":
			for item in self.iterreferencesall():
				yield item
		elif mode == "drop":
			for item in self.dropddl().splitlines():
				yield item
		else:
			for item in self.createddl().splitlines():
				yield item

	def __xrepr__(self, mode):
		yield (-1, True)
		if mode == "cell":
			yield (astyle.style_type_type, self.__class__.__name__)
			yield (astyle.style_default, "(")
			yield (astyle.style_default, self.name)
			if self.owner is not None:
				yield (astyle.style_default, ",")
				yield (astyle.style_default, self.owner)
			yield (astyle.style_default, ")")
		else:
			yield (astyle.style_default, repr(self))

	if hasattr(ipipe, "XDescriptor"):
		def __xattrs__(self, mode):
			yield "type"
			yield "name"
			yield "owner"
			yield "connection"
		
			if mode == "detail":
				yield "cdate()"
				yield "udate()"
				yield "-createddl()"
				yield "-dropddl()"
				yield "-iterreferences()"
				yield "-iterreferencedby()"
				yield "-iterreferencesall()"
				yield "-iterreferencedbyall()"
	else:
		def __xattrs__(self, mode):
			if mode == "detail":
				return ("type", "name", "owner", "connection", "cdate()", "udate()")
			else:
				return ("type", "name", "owner", "connection")


class SequenceDefinition(MixinNormalDates, Definition):
	type = "sequence"

	def _createddl(self, connection, term, copyvalue):
		(connection, cursor) = self.getcursor(connection)
		cursor.execute("select * from all_sequences where sequence_owner=nvl(:owner, user) and sequence_name=:name", owner=self.owner, name=self.name)
		rec = cursor.fetchone()
		if rec is None:
			raise SQLObjectNotFoundError(self)
		code  = "create sequence %s\n" % self.getname()
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

	def createddl(self, connection=None, term=True):
		return self._createddl(connection, term, False)

	def createddlcopy(self, connection=None, term=True):
		"""
		&sql; to create an identical copy of this sequence.
		"""
		return self._createddl(connection, term, True)

	def dropddl(self, connection=None, term=True):
		code = "drop sequence %s" % self.getname()
		if term:
			code += ";\n"
		else:
			code += "\n"
		return code

	def iterreferences(self, connection=None, schema="all"):
		# Shortcut: a sequence doesn't depend on anything
		if False:
			yield None

	def __xiter__(self, mode):
		if mode is None:
			yield ipipe.XMode(self, "create", "create statement", "the SQL script to create this sequence")
			yield ipipe.XMode(self, "createcopy", "create statement (exact copy)", "the SQL script to create this sequence (using the current value as the start value)")
			yield ipipe.XMode(self, "drop", "drop statement", "the SQL script to drop this sequence")
			yield ipipe.XMode(self, "referencedby", "referenced by", "other objects depending on this %s" % self.type)
			yield ipipe.XMode(self, "references", "references", "other objects on which this %s depends" % self.type)
			yield ipipe.XMode(self, "referencedbyall", "referenced by all", "all other objects depending on this %s" % self.type)
			yield ipipe.XMode(self, "referencesall", "references all", "all other objects on which this %s depends" % self.type)
		elif mode == "referencedby":
			for item in self.iterreferencedby():
				yield item
		elif mode == "references":
			for item in self.iterreferences():
				yield item
		elif mode == "referencedbyall":
			for item in self.iterreferencedbyall():
				yield item
		elif mode == "referencesall":
			for item in self.iterreferencesall():
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

	def __xattrs__(self, mode):
		for attr in super(SequenceDefinition, self).__xattrs__(mode):
			yield attr
			if attr == "-createddl()":
				yield "-createddlcopy()"


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

	def createddl(self, connection=None, term=True):
		(connection, cursor) = self.getcursor(connection)
		if self.ismview(connection):
			return ""
		cursor.execute("select * from all_tab_columns where owner=nvl(:owner, user) and table_name=:name order by column_id asc", owner=self.owner, name=self.name)
		recs = cursor.fetchall()
		if not recs:
			raise SQLObjectNotFoundError(self)
		code = ["create table %s\n(\n" % self.getname()]
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

	def dropddl(self, connection=None, term=True):
		if self.ismview(connection):
			return ""
		code = "drop table %s" % self.getname()
		if term:
			code += ";\n"
		else:
			code += "\n"
		return code

	def mview(self, connection=None):
		"""
		The materialized view this table belongs to (or <lit>None</lit>).
		"""
		(connection, cursor) = self.getcursor(connection)
		cursor.execute("select mview_name from all_mviews where owner=nvl(:owner, user) and mview_name=:name", owner=self.owner, name=self.name)
		rec = cursor.fetchone()
		if rec is not None:
			rec = MaterializedViewDefinition(self.name, self.owner, connection)
		return rec

	def ismview(self, connection=None):
		"""
		Is this table a materialized view?
		"""
		return self.mview(connection) is not None

	@classmethod
	def iterdefinitions(cls, connection, schema="user"):
		(connection, cursor) = self.getcursor(connection)
		if schema == "all":
			cursor.execute("select decode(owner, user, null, owner) as owner, table_name from all_tables")
		else:
			cursor.execute("select null as owner, table_name from user_tables")
		return (cls(row.table_name, row.owner, connection=connection) for row in cursor)

	def itercolumns(self, connection=None):
		"""
		<par>Generator that yields the definition of all columns of the
		<class>TableDefinition</class> <self/>.</par>
		"""
		(connection, cursor) = self.getcursor(connection)
		cursor.execute("select column_name from all_tab_columns where owner=nvl(:owner, user) and table_name=:name order by column_id", owner=self.owner, name=self.name)

		for rec in cursor.fetchall():
			yield ColumnDefinition("%s.%s" % (self.name, rec.column_name), self.owner, connection)

	def iterrecords(self, connection=None):
		"""
		<par>Generator that yields all records of the table <self/>.</par>
		"""
		(connection, cursor) = self.getcursor(connection)
		query = "select * from %s" % self.getname()
		cursor.execute(query)
		return iter(cursor)

	def itercomments(self, connection=None):
		"""
		<par>Generator that yields all <pyref class="CommentDefinition">column comments</pyref> of the table <self/>.</par>
		"""
		(connection, cursor) = self.getcursor(connection)
		cursor.execute("select column_name from all_tab_columns where owner=nvl(:owner, user) and table_name=:name order by column_id", owner=self.owner, name=self.name)
		for rec in cursor.fetchall():
			yield CommentDefinition("%s.%s" % (self.name, rec.column_name), self.owner, connection)

	def iterconstraints(self, connection=None):
		"""
		Constraints for this table.
		"""
		(connection, cursor) = self.getcursor(connection)
		# Primary and unique key(s)
		cursor.execute("select decode(owner, user, null, owner) as owner, constraint_type, constraint_name from all_constraints where constraint_type in ('P', 'U', 'R') and owner=nvl(:owner, user) and table_name=:name", owner=self.owner, name=self.name)
		types = {"P": PKDefinition, "U": UniqueDefinition, "R": FKDefinition}
		for rec in cursor:
			yield types[rec.constraint_type](rec.constraint_name, rec.owner, connection)

	def iterreferences(self, connection=None):
		connection = self.getconnection(connection)
		# A table doesn't depend on anything ...
		if self.ismview(connection):
			# ... unless it was created by a materialized view, in which case it depends on this view
			yield MaterializedViewDefinition(self.name, self.owner, connection)

	def iterreferencedby(self, connection=None):
		if not self.ismview(connection):
			for definition in self.itercomments(connection):
				yield definition
			for definition in self.iterconstraints(connection):
				yield definition
		for definition in super(TableDefinition, self).iterreferencedby(connection):
			# skip the materialized view
			if not isinstance(definition, MaterializedViewDefinition) or definition.name != self.name or definition.owner != self.owner:
				yield definition

	def __xiter__(self, mode):
		if mode is None:
			yield ipipe.XMode(self, "create", "create statement", "the SQL script to create this table")
			yield ipipe.XMode(self, "drop", "drop statement", "the SQL script to drop this table")
			yield ipipe.XMode(self, "columns", "columns", "the columns of this table")
			yield ipipe.XMode(self, "constraints", "constraints", "the constraints of this table")
			yield ipipe.XMode(self, "records", "records", "records in this table")
			yield ipipe.XMode(self, "referencedby", "referenced by", "other objects depending on this %s" % self.type)
			yield ipipe.XMode(self, "references", "references", "other objects on which this %s depends" % self.type)
			yield ipipe.XMode(self, "referencedbyall", "referenced by all", "all other objects depending on this %s" % self.type)
			yield ipipe.XMode(self, "referencesall", "references all", "all other objects on which this %s depends" % self.type)
		elif mode == "referencedby":
			for item in self.iterreferencedby():
				yield item
		elif mode == "references":
			for item in self.iterreferences():
				yield item
		elif mode == "referencedbyall":
			for item in self.iterreferencedbyall():
				yield item
		elif mode == "referencesall":
			for item in self.iterreferencesall():
				yield item
		elif mode == "drop":
			for item in self.dropddl().splitlines():
				yield item
		elif mode == "columns":
			for item in self.itercolumns():
				yield item
		elif mode == "constraints":
			for item in self.iterconstraints():
				yield item
		elif mode == "records":
			for item in self.iterrecords():
				yield item
		else:
			for item in self.createddl().splitlines():
				yield item

	if hasattr(ipipe, "XDescriptor"):
		def __xattrs__(self, mode):
			for attr in super(TableDefinition, self).__xattrs__(mode):
				yield attr
			if mode=="detail":
				yield "-itercolumns()"
				yield "-iterrecords()"
				yield "-itercomments()"
				yield "-iterconstraints()"
				yield "mview()"
	else:
		def __xattrs__(self, mode):
			for attr in super(TableDefinition, self).__xattrs__(mode):
				yield attr
			if mode=="detail":
				yield "mview()"


class ConstraintDefinition(Definition):
	pass


class PKDefinition(ConstraintDefinition):
	type = "pk"

	def createddl(self, connection=None, term=True):
		(connection, cursor) = self.getcursor(connection)
		cursor.execute("select decode(owner, user, null, owner) as owner, constraint_name, table_name, r_owner, r_constraint_name from all_constraints where constraint_type='P' and owner=nvl(:owner, user) and constraint_name=:name", owner=self.owner, name=self.name)
		rec2 = cursor.fetchone()
		if rec2 is None:
			raise SQLObjectNotFoundError(self)
		cursor.execute("select column_name from all_cons_columns where owner=nvl(:owner, user) and constraint_name=:name", owner=self.owner, name=self.name)
		tablename = getname(rec2.table_name, rec2.owner)
		pkname = getname(self.name, None)
		code = "alter table %s add constraint %s primary key(%s)" % (tablename, pkname, ", ".join(r.column_name for r in cursor))
		if term:
			code += ";\n"
		else:
			code += "\n"
		return code

	def dropddl(self, connection=None, term=True):
		(connection, cursor) = self.getcursor(connection)
		cursor.execute("select decode(owner, user, null, owner) as owner, table_name from all_constraints where owner=nvl(:owner, user) and constraint_name=:name", owner=self.owner, name=self.name)
		rec = cursor.fetchone()
		tablename = getname(rec.table_name, rec.owner)
		pkname = getname(self.name, None)
		code = "alter table %s drop constraint %s" % (tablename, pkname)
		if term:
			code += ";\n"
		else:
			code += "\n"
		return code

	def cdate(self, connection=None):
		(connection, cursor) = self.getcursor(connection)
		cursor.execute("select last_change from all_constraints where constraint_type='P' and constraint_name=:name and owner=nvl(:owner, user)", name=self.name, owner=self.owner)
		row = cursor.fetchone()
		if row is None:
			raise SQLObjectNotFoundError(self)
		return None

	def udate(self, connection=None):
		(connection, cursor) = self.getcursor(connection)
		cursor.execute("select last_change from all_constraints where constraint_type='P' and constraint_name=:name and owner=nvl(:owner, user)", name=self.name, owner=self.owner)
		row = cursor.fetchone()
		if row is None:
			raise SQLObjectNotFoundError(self)
		return row.last_change

	def iterreferencedby(self, connection=None):
		(connection, cursor) = self.getcursor(connection)
		cursor.execute("select decode(owner, user, null, owner) as owner, constraint_name from all_constraints where constraint_type='R' and r_owner=nvl(:owner, user) and r_constraint_name=:name", owner=self.owner, name=self.name)
		for rec in cursor.fetchall():
			yield FKDefinition(rec.constraint_name, rec.owner, connection)

		cursor.execute("select decode(owner, user, null, owner) as owner, index_name from all_indexes where owner=nvl(:owner, user) and index_name=:name", owner=self.owner, name=self.name)
		rec = cursor.fetchone() # Ist there an index for this constraint?
		if rec is not None:
			yield IndexDefinition(rec.index_name, rec.owner, connection)

	def iterreferences(self, connection=None):
		(connection, cursor) = self.getcursor(connection)
		cursor.execute("select decode(owner, user, null, owner) as owner, table_name from all_constraints where constraint_type='P' and owner=nvl(:owner, user) and constraint_name=:name", owner=self.owner, name=self.name)
		for rec in cursor.fetchall():
			yield TableDefinition(rec.table_name, rec.owner, connection)

	def table(self, connection=None):
		"""
		Return the <pyref class="TableDefinition"><class>TableDefinition</class> <self/> belongs too.
		"""
		(connection, cursor) = self.getcursor(connection)
		cursor.execute("select table_name from all_constraints where constraint_type='P' and owner=nvl(:owner, user) and constraint_name=:name", owner=self.owner, name=self.name)
		rec = cursor.fetchone()
		return TableDefinition(rec.table_name, self.owner, connection)

	def __xattrs__(self, mode):
		for attr in super(PKDefinition, self).__xattrs__(mode):
			yield attr
		if mode == "detail":
			yield "table()"


class CommentDefinition(Definition):
	type = "comment"

	def createddl(self, connection=None, term=True):
		(connection, cursor) = self.getcursor(connection)
		tcname = self.name.split(".")
		cursor.execute("select comments from all_col_comments where owner=nvl(:owner, user) and table_name=:tname and column_name=:cname", owner=self.owner, tname=tcname[0], cname=tcname[1])
		row = cursor.fetchone()
		if row is None:
			raise SQLObjectNotFoundError(self)

		name = self.getname()
		if row.comments:
			code = "comment on column %s is %s" % (name, formatstring(row.comments, latin1=True))
		else:
			code = "comment on column %s is ''" % name
		if term:
			code += ";\n"
		else:
			code += "\n"
		return code

	def dropddl(self, connection=None, term=True):
		# will be dropped with the table
		return ""

	def cdate(self, connection=None):
		return None

	def udate(self, connection=None):
		return None

	def iterreferences(self, connection=None):
		connection = self.getconnection(connection)
		yield TableDefinition(self.name.split(".")[0], self.owner, connection)

	def iterreferencedby(self, connection=None):
		if False:
			yield None


class FKDefinition(ConstraintDefinition):
	type = "fk"

	def createddl(self, connection=None, term=True):
		(connection, cursor) = self.getcursor(connection)
		# Add constraint_type to the query, so we don't pick up another constraint by accident
		cursor.execute("select decode(r_owner, user, null, r_owner) as r_owner, r_constraint_name, table_name from all_constraints where constraint_type='R' and owner=nvl(:owner, user) and constraint_name=:name", owner=self.owner, name=self.name)
		rec = cursor.fetchone()
		if rec is None:
			raise SQLObjectNotFoundError(self)
		cursor.execute("select column_name from all_cons_columns where owner=nvl(:owner, user) and constraint_name=:name order by position", owner=self.owner, name=self.name)
		fields1 = ", ".join(r.column_name for r in cursor)
		cursor.execute("select table_name, column_name from all_cons_columns where owner=nvl(:owner, user) and constraint_name=:name order by position", owner=rec.r_owner, name=rec.r_constraint_name)
		fields2 = ", ".join("%s(%s)" % (getname(r.table_name, rec.r_owner), r.column_name) for r in cursor)
		tablename = getname(rec.table_name, self.owner)
		fkname = getname(self.name, None)
		code = "alter table %s add constraint %s foreign key (%s) references %s" % (tablename, fkname, fields1, fields2)
		if term:
			code += ";\n"
		else:
			code += "\n"
		return code

	def _ddl(self, connection, cmd, term):
		(connection, cursor) = self.getcursor(connection)
		cursor.execute("select table_name from all_constraints where owner=nvl(:owner, user) and constraint_name=:name", owner=self.owner, name=self.name)
		rec = cursor.fetchone()
		if rec is None:
			raise SQLObjectNotFoundError(self)
		tablename = getname(rec.table_name, self.owner)
		fkname = getname(self.name, None)
		code = "alter table %s %s constraint %s" % (tablename, cmd, fkname)
		if term:
			code += ";\n"
		else:
			code += "\n"
		return code

	def dropddl(self, connection=None, term=True):
		return self._ddl(connection, "drop", term)

	def enableddl(self, connection=None, term=True):
		return self._ddl(connection, "enable", term)

	def disableddl(self, connection=None, term=True):
		return self._ddl(connection, "disable", term)

	def cdate(self, connection=None):
		(connection, cursor) = self.getcursor(connection)
		cursor.execute("select last_change from all_constraints where constraint_type='R' and constraint_name=:name and owner=nvl(:owner, user)", name=self.name, owner=self.owner)
		row = cursor.fetchone()
		if row is None:
			raise SQLObjectNotFoundError(self)
		return None

	def udate(self, connection=None):
		(connection, cursor) = self.getcursor(connection)
		cursor.execute("select last_change from all_constraints where constraint_type='R' and constraint_name=:name and owner=nvl(:owner, user)", name=self.name, owner=self.owner)
		row = cursor.fetchone()
		if row is None:
			raise SQLObjectNotFoundError(self)
		return row.last_change

	def iterreferencedby(self, connection=None):
		# Shortcut: Nobody references a foreign key
		if False:
			yield None

	def iterreferences(self, connection=None):
		yield self.table(connection)
		yield self.pk(connection)

	def table(self, connection=None):
		"""
		Return the <pyref class="TableDefinition"><class>TableDefinition</class> <self/> belongs too.
		"""
		(connection, cursor) = self.getcursor(connection)
		cursor.execute("select table_name from all_constraints where constraint_type='R' and owner=nvl(:owner, user) and constraint_name=:name", owner=self.owner, name=self.name)
		rec = cursor.fetchone()
		return TableDefinition(rec.table_name, self.owner, connection)

	def pk(self, connection=None):
		(connection, cursor) = self.getcursor(connection)
		cursor.execute("select decode(r_owner, user, null, r_owner) as r_owner, r_constraint_name from all_constraints where constraint_type='R' and owner=nvl(:owner, user) and constraint_name=:name", owner=self.owner, name=self.name)
		rec = cursor.fetchone()
		return PKDefinition(rec.r_constraint_name, rec.r_owner, connection)

	def __xattrs__(self, mode):
		for attr in super(FKDefinition, self).__xattrs__(mode):
			yield attr
		if mode == "detail":
			yield "table()"
			yield "pk()"


class IndexDefinition(MixinNormalDates, Definition):
	type = "index"

	def createddl(self, connection=None, term=True):
		(connection, cursor) = self.getcursor(connection)
		if self.isconstraint(connection):
			return ""
		cursor.execute("select index_name, table_name, uniqueness from all_indexes where table_owner=nvl(:owner, user) and index_name=:name", owner=self.owner, name=self.name)
		rec = cursor.fetchone()
		if rec is None:
			raise SQLObjectNotFoundError(self)
		tablename = getname(rec.table_name, self.owner)
		indexname = self.getname()
		if rec.uniqueness == "UNIQUE":
			unique = " unique"
		else:
			unique = ""
		cursor.execute("select aie.column_expression, aic.column_name from all_ind_columns aic, all_ind_expressions aie where aic.table_owner=aie.table_owner(+) and aic.index_name=aie.index_name(+) and aic.column_position=aie.column_position(+) and aic.table_owner=nvl(:owner, user) and aic.index_name=:name order by aic.column_position", owner=self.owner, name=self.name)
		code = "create%s index %s on %s (%s)" % (unique, indexname, tablename, ", ".join(r.column_expression or r.column_name for r in cursor))
		if term:
			code += ";\n"
		else:
			code += "\n"
		return code

	def dropddl(self, connection=None, term=True):
		if self.isconstraint(connection):
			return ""
		code = "drop index %s" % getname(self.name, self.owner)
		if term:
			code += ";\n"
		else:
			code += "\n"
		return code

	def constraint(self, connection=None):
		"""
		If this index is generated by a constraint, return it's definition otherwise return <lit>None</lit>.
		"""
		(connection, cursor) = self.getcursor(connection)
		cursor.execute("select constraint_type from all_constraints where owner=nvl(:owner, user) and constraint_name=:name", owner=self.owner, name=self.name)
		rec = cursor.fetchone()
		if rec is not None:
			rec = {"U": UniqueDefinition, "P": PKDefinition}[rec.constraint_type](self.name, self.owner, connection)
		return rec

	def isconstraint(self, connection=None):
		"""
		Is this index generated by a constraint?"
		"""
		return self.constraint(connection) is not None

	def iterreferences(self, connection=None):
		constraint = self.constraint(connection)
		# if self is generated by a constraint, self depends on it
		if constraint is not None:
			yield constraint
		else:
			for definition in super(IndexDefinition, self).iterreferences(connection):
				yield definition

	def __xattrs__(self, mode):
		for attr in super(IndexDefinition, self).__xattrs__(mode):
			yield attr
		if mode == "detail":
			yield "constraint()"

	def table(self, connection=None):
		"""
		Return the <pyref class="TableDefinition"><class>TableDefinition</class> <self/> belongs too.
		"""
		(connection, cursor) = self.getcursor(connection)
		cursor.execute("select table_name from all_indexes where table_owner=nvl(:owner, user) and index_name=:name", owner=self.owner, name=self.name)
		rec = cursor.fetchone()
		return TableDefinition(rec.table_name, self.owner, connection)

	def __xattrs__(self, mode):
		for attr in super(UniqueDefinition, self).__xattrs__(mode):
			yield attr
		if mode == "detail":
			yield "constraint()"
			yield "table()"


class UniqueDefinition(ConstraintDefinition):
	type = "unique"

	def createddl(self, connection=None, term=True):
		(connection, cursor) = self.getcursor(connection)
		# Add constraint_type to the query, so we don't pick up another constraint by accident
		cursor.execute("select table_name from all_constraints where constraint_type='U' and owner=nvl(:owner, user) and constraint_name=:name", owner=self.owner, name=self.name)
		rec = cursor.fetchone()
		if rec is None:
			raise SQLObjectNotFoundError(self)
		tablename = getname(rec.table_name, self.owner)
		uniquename = getname(self.name, None)
		cursor.execute("select column_name from all_cons_columns where owner=nvl(:owner, user) and constraint_name=:name", owner=self.owner, name=self.name)
		code = "alter table %s add constraint %s unique(%s)" % (tablename, uniquename, ", ".join(r.column_name for r in cursor))
		if term:
			code += ";\n"
		else:
			code += "\n"
		return code

	def dropddl(self, connection=None, term=True):
		(connection, cursor) = self.getcursor(connection)
		cursor.execute("select table_name from all_constraints where constraint_type='U' and owner=nvl(:owner, user) and constraint_name=:name", owner=self.owner, name=self.name)
		rec = cursor.fetchone()
		if rec is None:
			raise SQLObjectNotFoundError(self)
		tablename = getname(rec.table_name, self.owner)
		uniquename = getname(self.name, None)
		code = "alter table %s drop constraint %s" % (tablename, uniquename)
		if term:
			code += ";\n"
		else:
			code += "\n"
		return code

	def cdate(self, connection=None):
		(connection, cursor) = self.getcursor(connection)
		cursor.execute("select last_change from all_constraints where constraint_type='U' and constraint_name=:name and owner=nvl(:owner, user)", name=self.name, owner=self.owner)
		row = cursor.fetchone()
		if row is None:
			raise SQLObjectNotFoundError(self)
		return None

	def udate(self, connection=None):
		(connection, cursor) = self.getcursor(connection)
		cursor.execute("select last_change from all_constraints where constraint_type='U' and constraint_name=:name and owner=nvl(:owner, user)", name=self.name, owner=self.owner)
		row = cursor.fetchone()
		if row is None:
			raise SQLObjectNotFoundError(self)
		return row.last_change

	def iterreferencedby(self, connection=None):
		(connection, cursor) = self.getcursor(connection)
		cursor.execute("select decode(owner, user, null, owner) as owner, constraint_name from all_constraints where constraint_type='R' and r_owner=nvl(:owner, user) and r_constraint_name=:name", owner=self.owner, name=self.name)
		for rec in cursor:
			yield FKDefinition(rec.constraint_name, rec.owner, connection)

		cursor.execute("select decode(owner, user, null, owner) as owner, index_name from all_indexes where owner=nvl(:owner, user) and index_name=:name", owner=self.owner, name=self.name)
		rec = cursor.fetchone() # Ist there an index for this constraint?
		if rec is not None:
			yield IndexDefinition(rec.index_name, rec.owner, connection)

	def iterreferences(self, connection=None):
		(connection, cursor) = self.getcursor(connection)
		cursor.execute("select decode(owner, user, null, owner) as owner, table_name from all_constraints where constraint_type='U' and owner=nvl(:owner, user) and constraint_name=:name", owner=self.owner, name=self.name)
		for rec in cursor.fetchall():
			yield TableDefinition(rec.table_name, rec.owner, connection)

	def table(self, connection=None):
		"""
		Return the <pyref class="TableDefinition"><class>TableDefinition</class> <self/> belongs too.
		"""
		(connection, cursor) = self.getcursor(connection)
		cursor.execute("select table_name from all_constraints where constraint_type='U' and owner=nvl(:owner, user) and constraint_name=:name", owner=self.owner, name=self.name)
		rec = cursor.fetchone()
		return TableDefinition(rec.table_name, self.owner, connection)

	def __xattrs__(self, mode):
		for attr in super(UniqueDefinition, self).__xattrs__(mode):
			yield attr
		if mode == "detail":
			yield "table()"


class SynonymDefinition(Definition):
	type = "synonym"

	def createddl(self, connection=None, term=True):
		(connection, cursor) = self.getcursor(connection)
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
		name = getname(self.name, owner)
		name2 = getname(rec.table_name, rec.table_owner)
		code = "create or replace %ssynonym %s for %s" % (public, name, name2)
		if rec.db_link is not None:
			code += "@%s" % rec.db_link
		if term:
			code += ";\n"
		else:
			code += "\n"
		return code

	def dropddl(self, connection=None, term=True):
		owner = self.owner
		if owner == "PUBLIC":
			public = "public "
			owner = None
		else:
			public = ""
		name = getname(self.name, owner)
		code = "drop %ssynonym %s" % (public, name)
		if term:
			code += ";\n"
		else:
			code += "\n"
		return code

	def cdate(self, connection=None):
		return None

	def udate(self, connection=None):
		return None

	def iterreferences(self, connection=None, schema="all"):
		# Shortcut: a synonym doesn't depend on anything
		if False:
			yield None


class ViewDefinition(MixinNormalDates, Definition):
	type = "view"

	def createddl(self, connection=None, term=True):
		(connection, cursor) = self.getcursor(connection)
		cursor.execute("select text from all_views where owner=nvl(:owner, user) and view_name=:name", owner=self.owner, name=self.name)
		rec = cursor.fetchone()
		if rec is None:
			raise SQLObjectNotFoundError(self)
		code = "\n".join(line.rstrip() for line in rec.text.strip().splitlines()) # Strip trailing whitespace
		code = "create or replace view %s as\n\t%s" % (self.getname(), code)
		if term:
			code += "\n/\n"
		else:
			code += "\n"
		return code

	def dropddl(self, connection=None, term=True):
		code = "drop view %s" % self.getname()
		if term:
			code += ";\n"
		else:
			code += "\n"
		return code

	def iterrecords(self, connection=None):
		(connection, cursor) = self.getcursor(connection)
		query = "select * from %s" % self.getname()
		cursor.execute(query)
		return iter(cursor)

	def __xiter__(self, mode):
		if mode is None:
			yield ipipe.XMode(self, "create", "create statement", "the SQL script to create this view")
			yield ipipe.XMode(self, "drop", "drop statement", "the SQL script to drop this view")
			yield ipipe.XMode(self, "records", "records", "records in this view")
			yield ipipe.XMode(self, "referencedby", "referenced by", "other objects depending on this %s" % self.type)
			yield ipipe.XMode(self, "references", "references", "other objects on which this %s depends" % self.type)
			yield ipipe.XMode(self, "referencedbyall", "referenced by all", "all other objects depending on this %s" % self.type)
			yield ipipe.XMode(self, "referencesall", "references all", "all other objects on which this %s depends" % self.type)
		elif mode == "referencedby":
			for item in self.iterreferencedby():
				yield item
		elif mode == "references":
			for item in self.iterreferences():
				yield item
		elif mode == "referencedbyall":
			for item in self.iterreferencedbyall():
				yield item
		elif mode == "referencesall":
			for item in self.iterreferencesall():
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


class MaterializedViewDefinition(ViewDefinition):
	type = "materialized view"

	def createddl(self, connection=None, term=True):
		(connection, cursor) = self.getcursor(connection)
		cursor.execute("select * from all_mviews where owner=nvl(:owner, user) and mview_name=:name", owner=self.owner, name=self.name)
		rec = cursor.fetchone()
		if rec is None:
			raise SQLObjectNotFoundError(self)
		code = "\n".join(line.rstrip() for line in rec.query.strip().splitlines()) # Strip trailing whitespace
		code = "create materialized view %s\nrefresh %s on %s as\n\t%s" % (self.getname(), rec.refresh_method, rec.refresh_mode, code)
		if term:
			code += "\n/\n"
		else:
			code += "\n"
		return code

	def dropddl(self, connection=None, term=True):
		code = "drop materialized view %s" % self.getname()
		if term:
			code += ";\n"
		else:
			code += "\n"
		return code

	def iterreferences(self, connection=None):
		# skip the table
		for definition in super(MaterializedViewDefinition, self).iterreferences(connection):
			if not isinstance(definition, TableDefinition) or definition.name != self.name or definition.owner != self.owner:
				yield definition

	def iterreferencedby(self, connection=None):
		connection = self.getconnection(connection)
		yield TableDefinition(self.name, self.owner, connection)


class LibraryDefinition(Definition):
	type = "library"

	def createddl(self, connection=None, term=True):
		(connection, cursor) = self.getcursor(connection)
		cursor.execute("select file_spec from all_libraries where owner=nvl(:owner, user) and library_name=:name", owner=self.owner, name=self.name)
		rec = cursor.fetchone()
		if rec is None:
			raise SQLObjectNotFoundError(self)
		return "create or replace library %s as %r" % (self.getname(), rec.file_spec)
		if term:
			code += ";\n"
		else:
			code += "\n"
		return code

	def dropddl(self, connection=None, term=True):
		code = "drop library %s" % self.getname()
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

	def createddl(self, connection=None, term=True):
		(connection, cursor) = self.getcursor(connection)
		cursor.execute("select text from all_source where type='JAVA SOURCE' and owner=nvl(:owner, user) and name=:name order by line", owner=self.owner, name=self.name)
		code = "\n".join((rec.text or "").rstrip() for rec in cursor)
		code = code.strip()

		code = "create or replace and compile java source named %s as\n%s\n" % (self.getname(), code)
		if term:
			code += "/\n"
		return code

	def dropddl(self, connection=None, term=True):
		code = "drop java source %s" % self.getname()
		if term:
			code += ";\n"
		else:
			code += "\n"
		return code


class ColumnDefinition(Definition):
	type = "column"

	def addddl(self, connection=None, term=True):
		(connection, cursor) = self.getcursor(connection)
		name = self.name.split(".")
		cursor.execute("select * from all_tab_columns where owner=nvl(:owner, user) and table_name=:table_name and column_name=:column_name", owner=self.owner, table_name=name[0], column_name=name[1])
		rec = cursor.fetchone()
		if rec is None:
			raise SQLObjectNotFoundError(self)
		code = ["alter table %s add %s" % (getname(name[0], self.owner), getname(name[1], None))]
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

	def modifyddl(self, connection, cursorold, cursornew, term=True):
		(connection, cursor) = self.getcursor(connection)
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

		code = ["alter table %s modify %s" % (getname(name[0], self.owner), getname(name[1], None))]
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

	def dropddl(self, connection=None, term=True):
		(connection, cursor) = self.getcursor(connection)
		name = self.name.split(".")
		code = "alter table %s drop column %s" % (getname(name[0], self.owner), getname(name[1], None))
		if term:
			code += ";\n"
		else:
			code += "\n"
		return code

	def cdate(self, connection=None):
		(connection, cursor) = self.getcursor(connection)
		cursor.execute("select created from all_objects where lower(object_type)='table' and object_name=:name and owner=nvl(:owner, user)", name=self.name.split(".")[0], owner=self.owner)
		row = cursor.fetchone()
		if row is None:
			raise SQLObjectNotFoundError(self)
		return row.created

	def udate(self, connection=None):
		(connection, cursor) = self.getcursor(connection)
		cursor.execute("select last_ddl_time from all_objects where lower(object_type)='table' and object_name=:name and owner=nvl(:owner, user)", name=self.name.split(".")[0], owner=self.owner)
		row = cursor.fetchone()
		if row is None:
			raise SQLObjectNotFoundError(self)
		return row.last_ddl_time

	def iterreferences(self, connection=None):
		connection = self.getconnection(connection)
		name = self.name.split(".")
		yield TableDefinition(name[0], self.owner, connection)

	def iterreferencedby(self, connection=None):
		if False:
			yield None

	def __xiter__(self, mode):
		return None
