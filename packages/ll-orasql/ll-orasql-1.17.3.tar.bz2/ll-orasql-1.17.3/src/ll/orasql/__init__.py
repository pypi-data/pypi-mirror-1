#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

## Copyright 2004-2007 by LivingLogic AG, Bayreuth/Germany.
## Copyright 2004-2007 by Walter Dörwald
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
<pyref class="Procedure"><class>Procedure</class></pyref> class).</item>
<item>Query results will be put into <pyref class="Record"><class>Record</class></pyref>
objects, where database fields are accessible as object attributes.</item>
<item>The <pyref class="Connection"><class>Connection</class></pyref> class
provides methods for iterating through the database metadata.</item>
</ulist>
"""


import datetime, itertools

from cx_Oracle import *

from ll import misc

try:
	import astyle
except ImportError:
	from ll import astyle


# ipipe support
try:
	import ipipe
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
	def __init__(self, object, message):
		self.object = object
		self.message = message

	def __str__(self):
		return "conflict in %r: %s" % (self.object, self.message)


_default = object() # marker object for unset parameters


def _promotevalue(value, cursor, isblob):
	if isinstance(value, LOB) and (cursor.readlobs is True or (isinstance(cursor.readlobs, (int, long)) and value.size() <= cursor.readlobs)):
		value = value.read()
	if isinstance(value, str) and cursor.unicode and cursor.connection.encoding and not isblob:
		value = value.decode(cursor.connection.encoding)
	return value


class Record(dict):
	"""
	A <class>Record</class> is a subclass of <class>dict</class> that is used
	for storing results of database queries. Both item and attribute access (i.e.
	<method>__getitem__</method> and <method>__getattr__</method>) are available.
	Field names are case insensitive.
	"""
	def __init__(self, arg=None, **kwargs):
		dict.__init__(self)
		self.update(arg, **kwargs)

	def update(self, arg=None, **kwargs):
		if arg is not None:
			# if arg is a mapping use iteritems
			dict.update(self, ((key.lower(), value) for (key, value) in getattr(arg, "iteritems", arg)))
		dict.update(self, ((key.lower(), value) for (key, value) in kwargs.iteritems()))

	@classmethod
	def fromdata(cls, cursor, row):
		"""
		This class method can be used to create a <class>Record</class> instance
		from the database data.
		"""
		return cls((descr[0].lower(), _promotevalue(field, cursor, descr[1] is BLOB)) for (descr, field) in itertools.izip(cursor.description, row))

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

	def __xattrs__(self, mode="default"):
		# Return the attributes of this record. This is for interfacing with ipipe
		return self.iterkeys()

	def __xrepr__(self, mode):
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

	def __xattrs__(self, mode="default"):
		return ("type", "count")

	def __xrepr__(self, mode):
		if mode == "header" or mode == "footer":
			yield (astyle.style_default, self.type + "s")
		else:
			yield (astyle.style_default, repr(self))

	def __iter__(self):
		return self.class_.iterobjects(self.connection, self.schema)


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
	def __init__(self, *args, **kwargs):
		"""
		<par>Create a new connection. In addition to the parameters supported
		by <function>cx_Oracle.connect</function> the following keyword arguments
		are supported.</par>
		<dlist>
		<term><arg>readlobs</arg></term><item>If <arg>readlobs</arg> is <lit>False</lit>
		all cursor fetch return <class>LOB</class> objects as usual. If
		<arg>readlobs</arg> is an <class>int</class> (or <class>long</class>)
		<class>LOB</class>s with a maximum size of <arg>readlobs</arg>
		will be returned as strings. If <arg>readlobs</arg> is <lit>True</lit>
		all <class>LOB</class>s will be returned as strings.</item>
		<term><arg>unicode</arg></term><item>If <arg>unicode</arg> is true,
		strings (and <class>CLOB</class>s, if <arg>readlobs</arg> has the appropriate
		value) will be returned as <class>unicode</class> objects (except for
		<class>BLOB</class>s). Note that strings in the national character set
		(and <class>NCLOB</class>s) are not supported).</item>
		</dlist>
		"""
		if "readlobs" in kwargs or "unicode" in kwargs:
			kwargs = kwargs.copy()
			self.readlobs = kwargs.pop("readlobs", False)
			self.unicode = kwargs.pop("unicode", False)
		else:
			self.readlobs = False
			self.unicode = False
		super(Connection, self).__init__(*args, **kwargs)

	def connectstring(self):
		return "%s@%s" % (self.username, self.tnsentry)

	def cursor(self, readlobs=None, unicode=None):
		"""
		Return a new cursor for this connection. For the meaning
		of <arg>readlobs</arg> and <arg>unicode</arg> see
		<pyref method="__init__"><method>__init__</method></pyref>.
		"""
		return Cursor(self, readlobs=readlobs, unicode=unicode)

	def __repr__(self):
		return "<%s.%s object db=%r at 0x%x>" % (self.__class__.__module__, self.__class__.__name__, self.connectstring(), id(self))

	def __xrepr__(self, mode):
		if mode == "header" or mode=="footer":
			yield (astyle.style_default, "oracle connection to %s" % self.connectstring())
		elif mode == "cell":
			yield (style_connection, self.connectstring())
		else:
			yield (astyle.style_default, repr(self))

	def iterschema(self, schema="user"):
		"""
		<par>Generator that returns the number of different object types for this
		database.</par>
		
		<par>For the meaning of <arg>schema</arg> see
		<pyref method="iterobjects"><method>iterobjects</method></pyref>.</par>
		"""
		cursor = self.cursor()
		if schema == "all":
			cursor.execute("select object_type as type, count(*) as count from all_objects group by object_type")
		else:
			cursor.execute("select object_type as type, count(*) as count from user_objects group by object_type")
		for row in cursor.fetchall():
			class_ = Object.name2type.get(row.type.lower(), None)
			if class_ is not None:
				yield _AllTypes(self, class_, schema, row.count)
		if schema == "all":
			cursor.execute("select object_type as type, count(*) as count from all_objects group by object_type")
		else:
			cursor.execute("select object_type as type, count(*) as count from user_objects group by object_type")
		if schema == "all":
			cursor.execute("select count(*) as count from all_tab_privs")
		else:
			cursor.execute("select count(*) as count from user_tab_privs where owner=user")
		yield _AllTypes(self, Privilege, schema, cursor.fetchone().count)

	def itertables(self, schema="user"):
		"""
		<par>Generator that yields all table definitions in the current users schema
		(or all users schemas).</par>
		<par><arg>schema</arg> specifies from which tables should be
		yielded:</par>
		<dlist>
		<term><lit>"user"</lit></term><item>Only tables belonging to the current
		user (and those objects these depend on) will be yielded.</item>
		<term><lit>"all"</lit></term><item>All tables from all users will be
		yielded.</item>
		</dlist>
		<par>Tables that are materialized view will be skipped in both casess.</par>
		"""
		if schema not in ("user", "all"):
			raise UnknownSchemaError(schema)

		cursor = self.cursor()

		if schema == "all":
			cursor.execute("select decode(owner, user, null, owner) as owner, table_name from all_tables minus select decode(owner, user, null, owner) as owner, mview_name as table_name from all_mviews")
		else:
			cursor.execute("select null as owner, table_name from user_tables minus select null as owner, mview_name as table_name from user_mviews")
		for rec in cursor.fetchall():
			yield Table(rec.table_name, rec.owner, self)

	def iterfks(self, schema="user"):
		"""
		<par>Generator that yields all foreign key constraints in the current users schema
		(or all users schemas).</par>
		<par><arg>schema</arg> specifies from which tables should be
		yielded:</par>
		<dlist>
		<term><lit>"user"</lit></term><item>Only tables belonging to the current
		user (and those objects these depend on) will be yielded.</item>
		<term><lit>"all"</lit></term><item>All tables from all users will be
		yielded.</item>
		</dlist>
		"""
		if schema not in ("user", "all"):
			raise UnknownSchemaError(schema)

		cursor = self.cursor()

		if schema == "all":
			cursor.execute("select decode(owner, user, null, owner) as owner, constraint_name from all_constraints where constraint_type='R' order by owner, table_name, constraint_name")
		else:
			cursor.execute("select null as owner, constraint_name from user_constraints where constraint_type='R' order by table_name, constraint_name")
		for rec in cursor.fetchall():
			yield ForeignKey(rec.constraint_name, rec.owner, self)

	def iterobjects(self, mode="create", schema="user"):
		"""
		<par>Generator that yields the sequences, tables, primary keys,
		foreign keys, comments, unique constraints, indexes, views, functions,
		procedures, packages and types in the current users schema (or all users
		schemas) in a specified order.</par>
		<par><arg>mode</arg> specifies the order in which objects will be yielded:</par>
		<dlist>
		<term><lit>"create"</lit></term><item>Create order, i.e. recreating the
		objects in this order will not lead to errors.</item>
		<term><lit>"drop"</lit></term><item>Drop order, i.e. dropping the
		objects in this order will not lead to errors.</item>
		<term><lit>"flat"</lit></term><item>Unordered.</item>
		</dlist>
		<par><arg>schema</arg> specifies from which schema objects should be
		yielded:</par>
		<dlist>
		<term><lit>"user"</lit></term><item>Only objects belonging to the current
		user (and those objects these depend on) will be yielded.</item>
		<term><lit>"all"</lit></term><item>All objects from all users will be
		yielded.</item>
		</dlist>
		"""
		if mode not in ("create", "drop", "flat"):
			raise UnknownModeError(mode)

		if schema not in ("user", "all"):
			raise UnknownSchemaError(schema)

		done = set()

		cursor = self.cursor()

		def do(obj):
			if mode == "create":
				for subobj in obj.iterreferencesall(self, done):
					yield subobj
			elif mode == "drop":
				for subobj in obj.iterreferencedbyall(self, done):
					yield subobj
			else:
				if obj not in done:
					done.add(obj)
					yield obj

		def dosequences():
			# select * from all_sequences where sequence_owner=nvl(:owner, user) and sequence_name=:name
			if schema == "all":
				cursor.execute("select decode(sequence_owner, user, null, sequence_owner) as sequence_owner, sequence_name from all_sequences")
			else:
				cursor.execute("select null as sequence_owner, sequence_name from user_sequences")
			for rec in cursor.fetchall():
				for obj in do(Sequence(rec.sequence_name, rec.sequence_owner, self)):
					yield obj

		def dotables():
			if schema == "all":
				cursor.execute("select decode(owner, user, null, owner) as owner, table_name from all_tables")
			else:
				cursor.execute("select null as owner, table_name from user_tables")
			for rec in cursor.fetchall():
				obj = Table(rec.table_name, rec.owner, self)
				if mode == "create" or mode == "flat":
					for subobj in do(obj):
						yield subobj
	
				if not obj.ismview(self):
					# Primary key
					if schema == "all":
						cursor.execute("select decode(owner, user, null, owner) as owner, constraint_name from all_constraints where constraint_type='P' and owner=:owner and table_name=:name", owner=rec.owner, name=rec.table_name)
					else:
						cursor.execute("select null as owner, constraint_name from user_constraints where constraint_type='P' and table_name=:name", name=rec.table_name)
					for rec2 in cursor.fetchall():
						for subobj in do(PrimaryKey(rec2.constraint_name, rec2.owner, self)):
							yield subobj
	
					# Comments
					if schema == "all":
						cursor.execute("select column_name from all_tab_columns where owner=:owner and table_name=:name order by column_id", owner=rec.owner, name=rec.table_name)
					else:
						cursor.execute("select column_name from user_tab_columns where table_name=:name order by column_id", name=rec.table_name)
					for rec2 in cursor.fetchall():
						# No dependency checks neccessary, but use do anyway
						for subobj in do(Comment("%s.%s" % (rec.table_name, rec2.column_name), rec.owner, self)):
							yield subobj

				if mode == "drop":
					for subobj in do(obj):
						yield subobj

		def doconstraints():
			if schema == "all":
				cursor.execute("select constraint_type, decode(owner, user, null, owner) as owner, constraint_name from all_constraints where constraint_type in ('R', 'U') order by owner, table_name, constraint_type, constraint_name")
			else:
				cursor.execute("select constraint_type, null as owner, constraint_name from user_constraints where constraint_type in ('R', 'U') order by table_name, constraint_type, constraint_name")
			types = {"U": UniqueConstraint, "R": ForeignKey}
			for rec in cursor.fetchall():
				for subobj in do(types[rec.constraint_type](rec.constraint_name, rec.owner, self)):
					yield subobj

		def doindexes():
			if schema == "all":
				cursor.execute("select decode(owner, user, null, owner) as owner, index_name from all_indexes where index_type in ('NORMAL', 'FUNCTION-BASED NORMAL') order by owner, table_name, index_name")
			else:
				cursor.execute("select null as owner, index_name from user_indexes where index_type in ('NORMAL', 'FUNCTION-BASED NORMAL') order by table_name, index_name")
			for rec in cursor.fetchall():
				for subobj in do(Index(rec.index_name, rec.owner, self)):
					yield subobj

		def dosynonyms():
			if schema == "all":
				cursor.execute("select decode(owner, user, null, owner) as owner, synonym_name from all_synonyms")
			else:
				cursor.execute("select null as owner, synonym_name from user_synonyms")
			for rec in cursor.fetchall():
				for subobj in do(Synonym(rec.synonym_name, rec.owner, self)):
					yield subobj

		def doviews():
			if schema == "all":
				cursor.execute("select decode(owner, user, null, owner) as owner, view_name from all_views")
			else:
				cursor.execute("select null as owner, view_name from user_views")
			for rec in cursor.fetchall():
				for subobj in do(View(rec.view_name, rec.owner, self)):
					yield subobj

		def domviews():
			if schema == "all":
				cursor.execute("select decode(owner, user, null, owner) as owner, mview_name from all_mviews")
			else:
				cursor.execute("select null as owner, mview_name from user_mviews")
			for rec in cursor.fetchall():
				for subobj in do(MaterializedView(rec.mview_name, rec.owner, self)):
					yield subobj

		def docode():
			for type in (Function, Procedure, Package, PackageBody, Type, Trigger, JavaSource):
				if schema == "all":
					cursor.execute("select decode(owner, user, null, owner) as owner, object_name from all_objects where lower(object_type)=lower(:type)", type=type.type)
				else:
					cursor.execute("select null as owner, object_name from user_objects where lower(object_type)=lower(:type)", type=type.type)
				for rec in cursor.fetchall():
					for subobj in do(type(rec.object_name, rec.owner, self)):
						yield subobj

		funcs = [dosequences, dotables, doconstraints, doindexes, dosynonyms, doviews, domviews, docode]
		if mode == "drop":
			funcs = reversed(funcs)

		for func in funcs:
			for obj in func():
				yield obj

	def iterprivileges(self, schema="user"):
		"""
		<par>Generator that yields object privileges for the current users
		(or all users) objects.</par>
		<par><arg>schema</arg> specifies which privileges should be yielded:</par>
		<dlist>
		<term><lit>"user"</lit></term><item>Only object privileges for objects
		belonging to the current user will be yielded.</item>
		<term><lit>"all"</lit></term><item>All object privileges will be yielded.</item>
		</dlist>
		"""
		return Privilege.iterobjects(self, schema)


def connect(*args, **kwargs):
	"""
	Create a connection to the database and return a
	<pyref class="Connection"><class>Connection</class></pyref> object.
	"""
	return Connection(*args, **kwargs)


class Cursor(Cursor):
	"""
	A subclass of <module>cx_Oracle</module>s cursor class. Database results
	returned from <method>fetchone</method>, <method>fetchmany</method>,
	<method>fetchall</method> and <method>fetch</method> or by iterating the
	cursor will be returned as <pyref class="Record"><class>Record</class> objects.
	"""
	def __init__(self, connection, readlobs=None, unicode=None):
		"""
		Return a new cursor for the connection <arg>connection</arg>.
		For the meaning of <arg>readlobs</arg> and <arg>unicode</arg> see
		<pyref class="Connection" method="__init__"><class>Connection</class>s constructor</pyref>.
		"""
		super(Cursor, self).__init__(connection)
		if readlobs is not None:
			self.readlobs = readlobs
		else:
			self.readlobs = connection.readlobs
		if unicode is not None:
			self.unicode = unicode
		else:
			self.unicode = connection.unicode
		
	def fetchone(self, type=Record):
		row = super(Cursor, self).fetchone()
		if row is not None:
			row = type.fromdata(self, row)
		return row

	def fetchmany(self, rows=0, type=Record):
		sup = super(Cursor, self)
		return [type.fromdata(self, row) for row in sup.fetchmany(rows)]

	def fetchall(self, type=Record):
		sup = super(Cursor, self)
		return [type.fromdata(self, row) for row in sup.fetchall()]

	def fetch(self, type=Record):
		while True:
			yield type.fromdata(self, self.next())

	def __iter__(self):
		return self.fetch()

	def __xrepr__(self, mode):
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
	"""
	Mixin class that provides methods for determining creation and modification
	dates for objects.
	"""
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
	"""
	Mixin class that provides methods returning the create and drop statements
	for various objects.
	"""
	def createddl(self, connection=None, term=True):
		(connection, cursor) = self.getcursor(connection)
		cursor.execute("select text from all_source where lower(type)=lower(:type) and owner=nvl(:owner, user) and name=:name order by line", type=self.__class__.type, owner=self.owner, name=self.name)
		code = "\n".join((rec.text or "").rstrip() for rec in cursor) # sqlplus strips trailing spaces when executing SQL scripts, so we do that too
		if not code:
			raise SQLObjectNotFoundError(self)
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


class Object(object):
	"""
	<par>The base class for all Python classes modelling schema objects in the
	database.</par>

	<par>Subclasses are:
	<pyref class="Sequence"><class>Sequence</class></pyref>,
	<pyref class="Table"><class>Table</class></pyref>,
	<pyref class="PrimaryKey"><class>PrimaryKey</class></pyref>,
	<pyref class="Comment"><class>Comment</class></pyref>,
	<pyref class="ForeignKey"><class>ForeignKey</class></pyref>,
	<pyref class="Index"><class>Index</class></pyref>,
	<pyref class="Unique"><class>Unique</class></pyref>,
	<pyref class="Synonym"><class>Synonym</class></pyref>,
	<pyref class="View"><class>View</class></pyref>,
	<pyref class="MaterializedView"><class>MaterializedView</class></pyref>,
	<pyref class="Library"><class>Library</class></pyref>,
	<pyref class="Function"><class>Function</class></pyref>,
	<pyref class="Package"><class>Package</class></pyref>,
	<pyref class="Type"><class>Type</class></pyref>,
	<pyref class="Trigger"><class>Trigger</class></pyref>,
	<pyref class="JavaSource"><class>JavaSource</class></pyref> and
	<pyref class="Column"><class>Column</class></pyref>.
	</par>
	"""
	name2type = {} # maps the Oracle type name to the Python class

	class __metaclass__(type):
		def __new__(mcl, name, bases, dict):
			typename = None
			if "type" in dict and name != "Object":
				typename = dict["type"]
			cls = type.__new__(mcl, name, bases, dict)
			if typename is not None:
				Object.name2type[typename] = cls
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

	def __str__(self):
		if self.owner is not None:
			return "%s(%s, %s)" % (self.__class__.__name__, self.name, self.owner)
		else:
			return "%s(%s)" % (self.__class__.__name__, self.name)

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
		<par>Objects directly used by <self/>.</par>

		<par>If <arg>connection</arg> is not <lit>None</lit> it will be used as
		the database connection from which to fetch data. If <arg>connection</arg> is <lit>None</lit>
		the connection from which <self/> has been extracted will be used. If
		there is not such connection, you'll get an exception.</par>
		"""
		(connection, cursor) = self.getcursor(connection)
		cursor.execute("select referenced_type, decode(referenced_owner, user, null, referenced_owner) as referenced_owner, referenced_name from all_dependencies where type=upper(:type) and name=:name and owner=nvl(:owner, user) and type != 'NON-EXISTENT'", type=self.type, name=self.name, owner=self.owner)
		for rec in cursor:
			try:
				type = Object.name2type[rec.referenced_type.lower()]
			except KeyError:
				pass # FIXME: Issue a warning?
			else:
				yield type(rec.referenced_name, rec.referenced_owner, connection)

	def iterreferencesall(self, connection=None, done=None):
		"""
		<par>All objects used by <self/> (recursively).</par>

		<par>For the meaning of <arg>connection</arg> see
		<pyref method="iterreferences"><method>iterreferences</method></pyref>.</par>

		<par><arg>done</arg> is used internally and shouldn't be passed.</par>
		"""
		if done is None:
			done = set()
		if self not in done:
			done.add(self)
			for obj in self.iterreferences(connection):
				for subobj in obj.iterreferencesall(connection, done):
					yield subobj
			yield self

	def iterreferencedby(self, connection=None):
		"""
		<par>Objects using <self/>.</par>

		<par>For the meaning of <arg>connection</arg> see
		<pyref method="iterreferences"><method>iterreferences</method></pyref>.</par>
		"""
		(connection, cursor) = self.getcursor(connection)
		cursor.execute("select type, decode(owner, user, null, owner) as owner, name from all_dependencies where referenced_type=upper(:type) and referenced_name=:name and referenced_owner=nvl(:owner, user) and type != 'NON-EXISTENT'", type=self.type, name=self.name, owner=self.owner)
		for rec in cursor:
			try:
				type = Object.name2type[rec.type.lower()]
			except KeyError:
				pass # FIXME: Issue a warning?
			else:
				yield type(rec.name, rec.owner, connection)

	def iterreferencedbyall(self, connection=None, done=None):
		"""
		<par>All objects depending on <self/> (recursively).</par>

		<par>For the meaning of <arg>connection</arg> see
		<pyref method="iterreferences"><method>iterreferences</method></pyref>.</par>

		<par><arg>done</arg> is used internally and shouldn't be passed.</par>
		"""
		if done is None:
			done = set()
		if self not in done:
			done.add(self)
			for obj in self.iterreferencedby(connection):
				for subobj in obj.iterreferencedbyall(connection, done):
					yield subobj
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
	def iterobjects(cls, connection, schema="user"):
		"""
		<par>Generator that yields all objects of this type in the database schema
		of <arg>cursor</arg>.</par>
		"""
		cursor = connection.cursor()
		if schema=="all":
			cursor.execute("select decode(owner, user, null, owner) as owner, object_name from all_objects where lower(object_type) = :type", type=cls.type)
		else:
			cursor.execute("select null as owner, object_name from user_objects where lower(object_type) = :type", type=cls.type)
		return (cls(row.object_name, row.owner, connection) for row in cursor)

	def __iter__(self):
		return iter(self.createddl().splitlines())

	def __xrepr__(self, mode):
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

	def __xattrs__(self, mode="default"):
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


class Sequence(MixinNormalDates, Object):
	"""
	Models a sequence in the database.
	"""
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

	def __xattrs__(self, mode="default"):
		for attr in super(Sequence, self).__xattrs__(mode):
			yield attr
			if attr == "-createddl()":
				yield "-createddlcopy()"


def _columntype(rec, data_precision=None, data_scale=None, char_length=None):
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


def _columndefault(rec):
	if rec.data_default is not None and rec.data_default != "null\n":
		return rec.data_default.rstrip("\n")
	return "null"


class Table(MixinNormalDates, Object):
	"""
	Models a table in the database.
	"""
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
			code.append("\t%s %s" % (rec.column_name, _columntype(rec)))
			default = _columndefault(rec)
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
		The materialized view this table belongs to (or <lit>None</lit> if it's a real table).
		"""
		(connection, cursor) = self.getcursor(connection)
		cursor.execute("select mview_name from all_mviews where owner=nvl(:owner, user) and mview_name=:name", owner=self.owner, name=self.name)
		rec = cursor.fetchone()
		if rec is not None:
			rec = MaterializedView(self.name, self.owner, connection)
		return rec

	def ismview(self, connection=None):
		"""
		Is this table a materialized view?
		"""
		return self.mview(connection) is not None

	@classmethod
	def iterobjects(cls, connection, schema="user"):
		cursor = connection.cursor()
		if schema == "all":
			cursor.execute("select decode(owner, user, null, owner) as owner, table_name from all_tables")
		else:
			cursor.execute("select null as owner, table_name from user_tables")
		return (cls(row.table_name, row.owner, connection=connection) for row in cursor)

	def itercolumns(self, connection=None):
		"""
		<par>Generator that yields all column objects of the <class>Table</class> <self/>.</par>
		"""
		(connection, cursor) = self.getcursor(connection)
		cursor.execute("select column_name from all_tab_columns where owner=nvl(:owner, user) and table_name=:name order by column_id", owner=self.owner, name=self.name)

		for rec in cursor.fetchall():
			yield Column("%s.%s" % (self.name, rec.column_name), self.owner, connection)

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
		Generator that yields all <pyref class="Comment">column comments</pyref> of the table <self/>.
		"""
		(connection, cursor) = self.getcursor(connection)
		cursor.execute("select column_name from all_tab_columns where owner=nvl(:owner, user) and table_name=:name order by column_id", owner=self.owner, name=self.name)
		for rec in cursor.fetchall():
			yield Comment("%s.%s" % (self.name, rec.column_name), self.owner, connection)

	def iterconstraints(self, connection=None):
		"""
		Generator that yields all <pyref class="Constraint">constraints</pyref> for this table.
		"""
		(connection, cursor) = self.getcursor(connection)
		# Primary and unique key(s)
		cursor.execute("select decode(owner, user, null, owner) as owner, constraint_type, constraint_name from all_constraints where constraint_type in ('P', 'U', 'R') and owner=nvl(:owner, user) and table_name=:name", owner=self.owner, name=self.name)
		types = {"P": PrimaryKey, "U": UniqueConstraint, "R": ForeignKey}
		for rec in cursor:
			yield types[rec.constraint_type](rec.constraint_name, rec.owner, connection)

	def iterreferences(self, connection=None):
		connection = self.getconnection(connection)
		# A table doesn't depend on anything ...
		if self.ismview(connection):
			# ... unless it was created by a materialized view, in which case it depends on the view
			yield MaterializedView(self.name, self.owner, connection)

	def iterreferencedby(self, connection=None):
		if not self.ismview(connection):
			for obj in self.itercomments(connection):
				yield obj
			for obj in self.iterconstraints(connection):
				yield obj
		for obj in super(Table, self).iterreferencedby(connection):
			# skip the materialized view
			if not isinstance(obj, MaterializedView) or obj.name != self.name or obj.owner != self.owner:
				yield obj

	def __xattrs__(self, mode="default"):
		for attr in super(Table, self).__xattrs__(mode):
			yield attr
		if mode=="detail":
			yield "-itercolumns()"
			yield "-iterrecords()"
			yield "-itercomments()"
			yield "-iterconstraints()"
			yield "mview()"


class Constraint(Object):
	"""
	Base class of all constraints (primary key constraints, foreign key constraints
	and unique constraints).
	"""


class PrimaryKey(Constraint):
	"""
	Models a primary key constraint in the database.
	"""
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
			yield ForeignKey(rec.constraint_name, rec.owner, connection)

		cursor.execute("select decode(owner, user, null, owner) as owner, index_name from all_indexes where owner=nvl(:owner, user) and index_name=:name", owner=self.owner, name=self.name)
		rec = cursor.fetchone() # Ist there an index for this constraint?
		if rec is not None:
			yield Index(rec.index_name, rec.owner, connection)

	def iterreferences(self, connection=None):
		(connection, cursor) = self.getcursor(connection)
		cursor.execute("select decode(owner, user, null, owner) as owner, table_name from all_constraints where constraint_type='P' and owner=nvl(:owner, user) and constraint_name=:name", owner=self.owner, name=self.name)
		for rec in cursor.fetchall():
			yield Table(rec.table_name, rec.owner, connection)

	def table(self, connection=None):
		"""
		Return the <pyref class="Table"><class>Table</class></pyref> <self/> belongs to.
		"""
		(connection, cursor) = self.getcursor(connection)
		cursor.execute("select table_name from all_constraints where constraint_type='P' and owner=nvl(:owner, user) and constraint_name=:name", owner=self.owner, name=self.name)
		rec = cursor.fetchone()
		return Table(rec.table_name, self.owner, connection)

	def __xattrs__(self, mode="default"):
		for attr in super(PrimaryKey, self).__xattrs__(mode):
			yield attr
		if mode == "detail":
			yield "table()"


class Comment(Object):
	"""
	Models a column comment in the database.
	"""
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
		yield Table(self.name.split(".")[0], self.owner, connection)

	def iterreferencedby(self, connection=None):
		if False:
			yield None


class ForeignKey(Constraint):
	"""
	Models a foreign key constraint in the database.
	"""
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
		Return the <pyref class="Table"><class>Table</class></pyref> <self/> belongs to.
		"""
		(connection, cursor) = self.getcursor(connection)
		cursor.execute("select table_name from all_constraints where constraint_type='R' and owner=nvl(:owner, user) and constraint_name=:name", owner=self.owner, name=self.name)
		rec = cursor.fetchone()
		return Table(rec.table_name, self.owner, connection)

	def pk(self, connection=None):
		"""
		Return the <pyref class="PrimaryKey">primary key</pyref> referenced by <self/>.
		"""
		(connection, cursor) = self.getcursor(connection)
		cursor.execute("select decode(r_owner, user, null, r_owner) as r_owner, r_constraint_name from all_constraints where constraint_type='R' and owner=nvl(:owner, user) and constraint_name=:name", owner=self.owner, name=self.name)
		rec = cursor.fetchone()
		return PrimaryKey(rec.r_constraint_name, rec.r_owner, connection)

	def isenabled(self, connection=None):
		"""
		Return whether this constraint is enabled.
		"""
		(connection, cursor) = self.getcursor(connection)
		cursor.execute("select status from all_constraints where constraint_type='R' and owner=nvl(:owner, user) and constraint_name=:name", owner=self.owner, name=self.name)
		rec = cursor.fetchone()
		return rec.status == "ENABLED"

	def __xattrs__(self, mode="default"):
		for attr in super(ForeignKey, self).__xattrs__(mode):
			yield attr
		if mode == "detail":
			yield "table()"
			yield "pk()"


class Index(MixinNormalDates, Object):
	"""
	Models an index in the database.
	"""
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
		If this index is generated by a constraint, return the constraint otherwise return <lit>None</lit>.
		"""
		(connection, cursor) = self.getcursor(connection)
		cursor.execute("select constraint_type from all_constraints where owner=nvl(:owner, user) and constraint_name=:name and constraint_type in ('U', 'P')", owner=self.owner, name=self.name)
		rec = cursor.fetchone()
		if rec is not None:
			rec = {"U": UniqueConstraint, "P": PrimaryKey}[rec.constraint_type](self.name, self.owner, connection)
		return rec

	def isconstraint(self, connection=None):
		"""
		Is this index generated by a constraint?
		"""
		return self.constraint(connection) is not None

	def iterreferences(self, connection=None):
		constraint = self.constraint(connection)
		# if self is generated by a constraint, self depends on it
		if constraint is not None:
			yield constraint
		else:
			for obj in super(Index, self).iterreferences(connection):
				yield obj

	def table(self, connection=None):
		"""
		Return the <pyref class="Table"><class>Table</class></pyref> <self/> belongs to.
		"""
		(connection, cursor) = self.getcursor(connection)
		cursor.execute("select table_name from all_indexes where table_owner=nvl(:owner, user) and index_name=:name", owner=self.owner, name=self.name)
		rec = cursor.fetchone()
		return Table(rec.table_name, self.owner, connection)

	def __xattrs__(self, mode="default"):
		for attr in super(Index, self).__xattrs__(mode):
			yield attr
		if mode == "detail":
			yield "constraint()"
			yield "table()"


class UniqueConstraint(Constraint):
	"""
	Models a unique constraint in the database.
	"""
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
			yield ForeignKey(rec.constraint_name, rec.owner, connection)

		cursor.execute("select decode(owner, user, null, owner) as owner, index_name from all_indexes where owner=nvl(:owner, user) and index_name=:name", owner=self.owner, name=self.name)
		rec = cursor.fetchone() # Ist there an index for this constraint?
		if rec is not None:
			yield Index(rec.index_name, rec.owner, connection)

	def iterreferences(self, connection=None):
		(connection, cursor) = self.getcursor(connection)
		cursor.execute("select decode(owner, user, null, owner) as owner, table_name from all_constraints where constraint_type='U' and owner=nvl(:owner, user) and constraint_name=:name", owner=self.owner, name=self.name)
		for rec in cursor.fetchall():
			yield Table(rec.table_name, rec.owner, connection)

	def table(self, connection=None):
		"""
		Return the <pyref class="Table"><class>Table</class></pyref> <self/> belongs to.
		"""
		(connection, cursor) = self.getcursor(connection)
		cursor.execute("select table_name from all_constraints where constraint_type='U' and owner=nvl(:owner, user) and constraint_name=:name", owner=self.owner, name=self.name)
		rec = cursor.fetchone()
		return Table(rec.table_name, self.owner, connection)

	def __xattrs__(self, mode="default"):
		for attr in super(UniqueConstraint, self).__xattrs__(mode):
			yield attr
		if mode == "detail":
			yield "table()"


class Synonym(Object):
	"""
	Models a synonym in the database.
	"""
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


class View(MixinNormalDates, Object):
	"""
	Models a view in the database.
	"""
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


class MaterializedView(View):
	"""
	Models a meterialized view in the database.
	"""
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
		for obj in super(MaterializedView, self).iterreferences(connection):
			if not isinstance(obj, Table) or obj.name != self.name or obj.owner != self.owner:
				yield obj

	def iterreferencedby(self, connection=None):
		connection = self.getconnection(connection)
		yield Table(self.name, self.owner, connection)


class Library(Object):
	"""
	Models a library in the database.
	"""
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


class Argument(object):
	"""
	<class>Argument</class> objects hold information about the arguments
	of a stored procedure.
	"""
	def __init__(self, name, position, datatype, isin, isout):
		self.name = name
		self.position = position
		self.datatype = datatype
		self.isin = isin
		self.isout = isout

	def __repr__(self):
		return "<%s.%s name=%r position=%r at 0x%x>" % (self.__class__.__module__, self.__class__.__name__, self.name, self.position, id(self))

	def __xattrs__(self, mode="default"):
		return ("name", "position", "datatype", "isin", "isout")


class Callable(MixinNormalDates, MixinCodeDDL, Object):
	"""
	Models a callable object in the database, i.e. functions and procedures.
	"""

	_ora2cx = {
		"date": DATETIME,
		"number": NUMBER,
		"varchar2": STRING,
		"clob": CLOB,
		"blob": BLOB,
	}
	
	def __init__(self, name, owner=None, connection=None):
		Object.__init__(self, name, owner, connection)
		self._argsbypos = None
		self._argsbyname = None
		self._returnvalue = None

	def _calcargs(self, cursor):
		if self._argsbypos is None:
			cursor.execute("select object_id from all_objects where owner=nvl(:owner, user) and lower(object_name)=lower(:name) and object_type=:type", owner=self.owner, name=self.name, type=self.type.upper())
			if cursor.fetchone() is None:
				raise SQLObjectNotFoundError(self)
			self._argsbypos = []
			self._argsbyname = {}
			cursor.execute("select lower(argument_name) as name, lower(in_out) as in_out, lower(data_type) as datatype from all_arguments where owner=nvl(:owner, user) and lower(object_name)=lower(:name) and data_level=0 order by sequence", owner=self.owner, name=self.name)
			i = 0 # argument position (skip return value)
			for record in cursor:
				arginfo = Argument(record.name, i, record.datatype, "in" in record.in_out, "out" in record.in_out)
				if record.name is None: # this is the return value
					self._returnvalue = arginfo
				else:
					self._argsbypos.append(arginfo)
					self._argsbyname[arginfo.name] = arginfo
					i += 1

	def _getparamarray(self, cursor, *args, **kwargs):
		# Get preinitialized parameter array
		la = len(args)
		lra = len(self._argsbypos)
		if la > lra:
			raise TypeError("too many parameters for %r: %d given, %d expected" % (la, lra))
		realargs = list(args) + [_default]*(lra-la)

		# Put keyword arguments into the parameter array
		for (key, value) in kwargs.iteritems():
			try:
				arginfo = self._argsbyname[key.lower()]
			except KeyError:
				raise TypeError("unknown parameter for %r: %s" % (self, key))
			else:
				if realargs[arginfo.position] is not _default:
					raise TypeError("duplicate argument for %r: %s" % (self, key))
			if isinstance(value, unicode) and cursor.connection.encoding is not None:
				value = value.encode(cursor.connection.encoding)
			realargs[arginfo.position] = value

		# Replace out parameters (and strings that are longer than the allowed
		# maximum) with variables; replace unspecified parameters with None
		for arginfo in self._argsbypos:
			realarg = realargs[arginfo.position]
			if realarg is _default:
				realarg = None
				realargs[arginfo.position] = realarg
			if arginfo.isout or arginfo.datatype == "blob" or (isinstance(realarg, basestring) and len(realarg) >= 32000):
				try:
					type = self._ora2cx[arginfo.datatype]
				except KeyError:
					raise TypeError("can't handle out parameter %s of type %s in %r" % (arginfo.name, arginfo.datatype, self))
				var = cursor.var(type)
				var.setvalue(0, realarg)
				realargs[arginfo.position] = var
		return realargs

	def iterarguments(self, connection=None):
		"""
		<par>Generator that yields all <pyref class="ArgumentInfo">arguments</pyref> of the function/procedure <self/>.</par>
		"""
		(connection, cursor) = self.getcursor(connection)
		self._calcargs(cursor)
		for arginfo in self._argsbypos:
			yield arginfo

	def __xattrs__(self, mode="default"):
		for attr in Object.__xattrs__(self, mode):
			yield attr
		if mode == "detail":
			yield "-iterarguments()"


class Procedure(Callable):
	"""
	Models a procedure in the database. A <class>Procedure</class> object can be
	used as a wrapper for calling the procedure with keyword arguments.
	"""

	type = "procedure"

	def __call__(self, cursor, *args, **kwargs):
		"""
		Call the procedure with arguments <arg>args</arg> and keyword arguments
		<arg>kwargs</arg>. <arg>cursor</arg> must be a <module>cx_Oracle</module>
		or <module>ll.orasql</module> cursor. This will return a
		<pyref class="Record"><class>Record</class></pyref> object containing
		the result of the call (i.e. this record will contain all in and out
		parameters).
		"""
		self._calcargs(cursor)

		# Get preinitialized parameter array
		realargs = self._getparamarray(cursor, *args, **kwargs)

		if self.owner is None:
			name = self.name
		else:
			name = "%s.%s" % (self.owner, self.name)

		return Record((self._argsbypos[i].name, _promotevalue(value, cursor, self._argsbypos[i].datatype == "blob")) for (i, value) in enumerate(cursor.callproc(name, realargs)))


class Function(Callable):
	"""
	Models a function in the database. A <class>Function</class> object can be
	used as a wrapper for calling the function with keyword arguments.
	"""
	type = "function"

	def __call__(self, cursor, *args, **kwargs):
		"""
		Call the function with arguments <arg>args</arg> and keyword arguments
		<arg>kwargs</arg>. <arg>cursor</arg> must be a <module>cx_Oracle</module>
		or <module>ll.orasql</module> cursor. This will return a tuple containing
		the result and a <pyref class="Record"><class>Record</class></pyref> object
		containing the modified parameters (i.e. this record will contain all in
		and out parameters).
		"""
		self._calcargs(cursor)

		# Get preinitialized parameter array
		realargs = self._getparamarray(cursor, *args, **kwargs)

		if self.owner is None:
			name = self.name
		else:
			name = "%s.%s" % (self.owner, self.name)

		returnvalue = _promotevalue(cursor.callfunc(name, self._ora2cx[self._returnvalue.datatype], realargs), cursor, self._returnvalue.datatype == "blob")
		result = Record()
		for (i, value) in enumerate(realargs):
			arginfo = self._argsbypos[i]
			if arginfo.isout:
				value = value.getvalue(0)
			result[arginfo.name] = _promotevalue(value, cursor, arginfo.datatype == "blob")
		return (returnvalue, result)


class Package(MixinNormalDates, MixinCodeDDL, Object):
	"""
	Models a package in the database.
	"""
	type = "package"


class PackageBody(MixinNormalDates, MixinCodeDDL, Object):
	"""
	Models a package body in the database.
	"""
	type = "package body"


class Type(MixinNormalDates, MixinCodeDDL, Object):
	"""
	Models a type definition in the database.
	"""
	type = "type"


class Trigger(MixinNormalDates, MixinCodeDDL, Object):
	"""
	Models a trigger in the database.
	"""
	type = "trigger"


class JavaSource(MixinNormalDates, Object):
	"""
	Models Java source code in the database.
	"""
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


class Privilege(object):
	"""
	Models a database object privilege (i.e. a grant).
	"""
	type = "privilege" # required by iterschema()

	def __init__(self, privilege, name, grantor, grantee, owner=None, connection=None):
		self.privilege = privilege
		self.name = name
		self.grantor = grantor
		self.grantee = grantee
		self.owner = owner
		self.connection = connection

	def __repr__(self):
		if self.owner is not None:
			return "%s.%s(%r, %r, %r, %r)" % (self.__class__.__module__, self.__class__.__name__, self.privilege, self.name, self.grantee, self.owner)
		else:
			return "%s.%s(%r, %r, %r)" % (self.__class__.__module__, self.__class__.__name__, self.privilege, self.name, self.grantee)

	def __str__(self):
		if self.owner is not None:
			return "%s(%r, %r, %r, %r)" % (self.__class__.__name__, self.privilege, self.name, self.grantee, self.owner)
		else:
			return "%s(%r, %r, %r)" % (self.__class__.__name__, self.privilege, self.name, self.grantee)

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
	def iterobjects(self, connection, schema="user"):
		"""
		<par>Generator that yields object privileges for the current users
		(or all users) objects.</par>
		<par><arg>schema</arg> specifies which privileges should be yielded:</par>
		<dlist>
		<term><lit>"user"</lit></term><item>Only object privileges for objects
		belonging to the current user will be yielded.</item>
		<term><lit>"all"</lit></term><item>All object privileges will be yielded.</item>
		</dlist>
		"""
		if schema not in ("user", "all"):
			raise UnknownSchemaError(schema)

		cursor = connection.cursor()

		if schema == "all":
			cursor.execute("select decode(table_schema, user, null, table_schema) as owner, privilege, table_name as object, decode(grantor, user, null, grantor) as grantor, grantee from all_tab_privs order by table_schema, table_name, privilege")
		else:
			cursor.execute("select null as owner, privilege, table_name as object, decode(grantor, user, null, grantor) as grantor, grantee from user_tab_privs where owner=user order by table_name, privilege")
		return (Privilege(rec.privilege, rec.object, rec.grantor, rec.grantee, rec.owner, cursor.connection) for rec in cursor)

	def grantddl(self, connection=None, term=True, mapgrantee=True):
		"""
		&sql; to grant this privilege. If <arg>mapgrantee</arg> is a list
		or a dictionary and <lit><self/>.grantee</lit> is not in this list
		(or dictionary) no command will returned. If it's a dictionary and
		<lit><self/>.grantee</lit> is in it, the privilege will be granted
		to the user specified as the value instead of the original one. If
		<lit>mapgrantee</lit> is <lit>True</lit> (the default) the privilege
		will be granted to the original grantee.
		"""
		(connection, cursor) = self.getcursor(connection)
		if mapgrantee is True:
			grantee = self.grantee
		elif isinstance(mapgrantee, (list, tuple)):
			if self.grantee.lower() in map(str.lower, mapgrantee):
				grantee = self.grantee
			else:
				grantee = None
		else:
			mapgrantee = dict((key.lower(), value) for (key, value) in mapgrantee.iteritems())
			grantee = mapgrantee.get(self.grantee.lower(), None)
		if grantee is None:
			return ""
		code = "grant %s on %s to %s" % (self.privilege, self.name, grantee)
		if term:
			code += ";\n"
		return code

	def __xattrs__(self, mode="default"):
		yield ipipe.AttributeDescriptor("privilege", "the type of the privilege")
		yield ipipe.AttributeDescriptor("name", "the name of the object for which this privilege grants access")
		yield ipipe.AttributeDescriptor("owner", "the owner of the object")
		yield ipipe.AttributeDescriptor("grantor", "who granted this privilege?")
		yield ipipe.AttributeDescriptor("grantee", "to whom has this privilege been granted?")
		yield ipipe.AttributeDescriptor("connection")
		if mode == "detail":
			yield ipipe.IterMethodDescriptor("grantddl", "the SQL statement to issue this privilege")


class Column(Object):
	"""
	Models a single column of a table in the database. This is used to output
	<lit>ALTER TABLE ...</lit> statements for adding, dropping and modifying
	columns.
	"""
	type = "column"

	def _getcolumnrecord(self, cursor):
		name = self.name.split(".")
		cursor.execute("select * from all_tab_columns where owner=nvl(:owner, user) and table_name=:table_name and column_name=:column_name", owner=self.owner, table_name=name[0], column_name=name[1])
		rec = cursor.fetchone()
		if rec is None:
			raise SQLObjectNotFoundError(self)
		return rec

	def addddl(self, connection=None, term=True):
		(connection, cursor) = self.getcursor(connection)
		rec = self._getcolumnrecord(cursor)
		name = self.name.split(".")
		code = ["alter table %s add %s" % (getname(name[0], self.owner), getname(name[1], None))]
		code.append(" %s" % _columntype(rec))
		default = _columndefault(rec)
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

		rec = self._getcolumnrecord(cursor)
		recold = self._getcolumnrecord(cursorold)
		recnew = self._getcolumnrecord(cursornew)

		name = self.name.split(".")

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
				code.append(" %s" % _columntype(rec, data_precision=data_precision, data_scale=data_scale, char_length=char_length))
			else: # The type has changed too
				if recnew.data_type != rec.data_type or recnew.data_type_owner != rec.data_type_owner:
					raise ConflictError(self, "data_type unmergeable")
				elif recnew.data_precision != rec.data_precision:
					raise ConflictError(self, "data_precision unmergeable")
				elif recnew.data_scale != rec.data_scale:
					raise ConflictError(self, "data_scale unmergeable")
				elif recnew.char_length != rec.char_length:
					raise ConflictError(self, "char_length unmergeable")
				code.append(" %s" % _columntype(recnew))

		# Has the default changed?
		default = _columndefault(rec)
		olddefault = _columndefault(recold)
		newdefault = _columndefault(recnew)
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
		# The column creation date is the table creation date
		(connection, cursor) = self.getcursor(connection)
		cursor.execute("select created from all_objects where lower(object_type)='table' and object_name=:name and owner=nvl(:owner, user)", name=self.name.split(".")[0], owner=self.owner)
		row = cursor.fetchone()
		if row is None:
			raise SQLObjectNotFoundError(self)
		return row.created

	def udate(self, connection=None):
		# The column modification date is the table modification date
		(connection, cursor) = self.getcursor(connection)
		cursor.execute("select last_ddl_time from all_objects where lower(object_type)='table' and object_name=:name and owner=nvl(:owner, user)", name=self.name.split(".")[0], owner=self.owner)
		row = cursor.fetchone()
		if row is None:
			raise SQLObjectNotFoundError(self)
		return row.last_ddl_time

	def iterreferences(self, connection=None):
		connection = self.getconnection(connection)
		name = self.name.split(".")
		yield Table(name[0], self.owner, connection)

	def iterreferencedby(self, connection=None):
		if False:
			yield None

	def datatype(self, connection=None):
		"""
		The &sql; type of this column.
		"""
		(connection, cursor) = self.getcursor(connection)
		rec = self._getcolumnrecord(cursor)
		return _columntype(rec)

	def default(self, connection=None):
		"""
		The &sql; default value for this column.
		"""
		(connection, cursor) = self.getcursor(connection)
		rec = self._getcolumnrecord(cursor)
		return _columndefault(rec)

	def nullable(self, connection=None):
		"""
		Is this column nullable?
		"""
		(connection, cursor) = self.getcursor(connection)
		rec = self._getcolumnrecord(cursor)
		return rec.nullable == "Y"

	def comment(self, connection=None):
		"""
		The comment for this column.
		"""
		name = self.name.split(".")
		(connection, cursor) = self.getcursor(connection)
		cursor.execute("select comments from all_col_comments where owner=nvl(:owner, user) and table_name=:table_name and column_name=:column_name", owner=self.owner, table_name=name[0], column_name=name[1])
		rec = cursor.fetchone()
		if rec is None:
			raise SQLObjectNotFoundError(self)
		return rec.comments or None

	def __xattrs__(self, mode="default"):
		for attr in super(Column, self).__xattrs__(mode):
			if attr == "-createddl()":
				yield "-addddl()"
			else:
				yield attr
		yield "datatype()"
		yield "default()"
		yield "nullable()"
		yield "comment()"

	def __iter__(self):
		return None
