#!/usr/bin/env python
# -*- coding: utf-8 -*-

## Copyright 2004-2008 by LivingLogic AG, Bayreuth/Germany.
## Copyright 2004-2008 by Walter Dörwald
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
:mod:`ll.orasql` contains utilities for working with cx_Oracle__:

*	It allows calling procedures with keyword arguments (via the
	:class:`Procedure` class).

*	Query results will be put into :class:`Record` objects, where database
	fields are accessible as object attributes.

*	The :class:`Connection` class provides methods for iterating through the
	database metadata.

__ http://www.computronix.com/utilities.shtml#Oracle
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


__docformat__ = "reStructuredText"


style_connection = astyle.style_url


class SQLObjectNotFoundError(Exception):
	def __init__(self, obj):
		self.obj = obj

	def __str__(self):
		return "%r not found" % self.obj


class SQLNoSuchObjectError(Exception):
	def __init__(self, name, owner):
		self.name = name
		self.owner = owner

	def __str__(self):
		if self.owner is None:
			return "no object named %r" % (self.name, )
		else:
			return "no object named %r for owner %r" % (self.name, self.owner)


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


class Args(dict):
	"""
	An :class:`Args` object is a subclass of :class:`dict` that is used for
	passing arguments to procedures and functions. Both item and attribute access
	(i.e. :meth:`__getitem__` and :meth:`__getattr__`) are available. Names are
	case insensitive.
	"""
	def __init__(self, arg=None, **kwargs):
		dict.__init__(self)
		self.update(arg, **kwargs)

	def update(self, arg=None, **kwargs):
		if arg is not None:
			# if arg is a mapping use iteritems
			dict.update(self, ((key.lower(), value) for (key, value) in getattr(arg, "iteritems", arg)))
		dict.update(self, ((key.lower(), value) for (key, value) in kwargs.iteritems()))

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


class RecordMaker(object):
	def __init__(self, cursor):
		self._readlobs = cursor.readlobs
		self._encoding = cursor.connection.encoding
		self._index2name = [d[0].lower() for d in cursor.description]
		self._isblob = tuple(descr[1] in (BLOB, BINARY) for descr in cursor.description)

	def _decode(self, value, isblob):
		if isinstance(value, LOB) and (self._readlobs is True or (isinstance(self._readlobs, (int, long)) and value.size() <= self._readlobs)):
			value = value.read()
		if isinstance(value, str) and not isblob:
			value = value.decode(self._encoding)
		return value

	def __call__(self, *row):
		row = tuple(self._decode(*args) for args in itertools.izip(row, self._isblob))
		return Record(self._index2name, row)


class Record(tuple):
	"""
	A :class:`Record` is a subclass of :class:`tuple` that is used for storing
	results of database fetches and procedure and function calls. Both item and
	attribute access (i.e. :meth:`__getitem__` and :meth:`__getattr__`) are
	available. Field names are case insensitive.
	"""

	def __new__(cls, names, values):
		record = tuple.__new__(cls, values)
		record._index2name = names
		record._name2index = dict(itertools.izip(names, itertools.count()))
		return record

	def __getitem__(self, arg):
		if isinstance(arg, basestring):
			arg = self._name2index[arg.lower()]
		return tuple.__getitem__(self, arg)

	def __getattr__(self, name):
		try:
			index = self._name2index[name.lower()]
		except KeyError:
			raise AttributeError("'%s' object has no attribute %r" % (self.__class__.__name__, name))
		return tuple.__getitem__(self, index)

	def __contains__(self, name):
		return name.lower() in self._name2index

	def iterkeys(self):
		"""
		Return an iterator over field names
		"""
		return iter(self._index2name)

	def keys(self):
		"""
		Return a list of field names
		"""
		return self._index2name[:]

	def items(self):
		"""
		Return a list of (field name, field value) tuples.
		"""
		return [(key, tuple.__getitem__(self, index)) for (index, key) in enumerate(self._index2name)]

	def iteritems(self):
		"""
		Return an iterator over (field name, field value) tuples.
		"""
		return ((key, tuple.__getitem__(self, index)) for (index, key) in enumerate(self._index2name))

	def __xattrs__(self, mode="default"):
		# Return the attributes of this record. This is for interfacing with ipipe
		return self.iterkeys()

	def __xrepr__(self, mode):
		if mode == "header":
			yield (astyle.style_default, "%s.%s" % (self.__class__.__module__, self.__class__.__name__))
		else:
			yield (astyle.style_default, repr(self))

	def __repr__(self):
		return "<%s.%s %s at 0x%x>" % (self.__class__.__module__, self.__class__.__name__, ", ".join("%s=%r" % item for item in self.iteritems()), id(self))


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
	:class:`SessionPool` is a subclass of :class:`cx_Oracle.SessionPool`.
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
	:class:`Connection` is a subclass of :class:`cx_Oracle.Connection`.
	"""
	def __init__(self, *args, **kwargs):
		"""
		Create a new connection. In addition to the parameters supported by
		:func:`cx_Oracle.connect` the following keyword argument is supported.

		:var:`readlobs` : bool or integer
			If :var:`readlobs` is :const:`False` all cursor fetch return
			:class:`LOB` objects as usual. If :var:`readlobs` is an :class:`int`
			(or :class:`long`) :class:`LOB`s with a maximum size of :var:`readlobs`
			will be returned as strings. If :var:`readlobs` is :const:`True`
			all :class:`LOB` values will be returned as strings.
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

	def cursor(self, readlobs=None):
		"""
		Return a new cursor for this connection. For the meaning of
		:var:`readlobs` see :meth:`__init__`.
		"""
		return Cursor(self, readlobs=readlobs)

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
		Generator that returns the number of different object types for this
		database. For the meaning of :var:`schema` see :meth:`iterobjects`.
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
			cursor.execute("select count(*) as count from all_tab_privs")
		else:
			cursor.execute("select count(*) as count from user_tab_privs where owner=user")
		yield _AllTypes(self, Privilege, schema, cursor.fetchone()[0])

	def itertables(self, schema="user"):
		"""
		Generator that yields all table definitions in the current users schema
		(or all users schemas). :var:`schema` specifies from which tables should
		be yielded:

		``"user"``
			Only tables belonging to the current user (and those objects these
			depend on) will be yielded.

		``"all"``
			All tables from all users will be yielded.

		Tables that are materialized view will be skipped in both casess.
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
		Generator that yields all foreign key constraints in the current users
		schema (or all users schemas). :var:`schema` specifies from which tables
		should be yielded:

		``"user"``
			Only tables belonging to the current user (and those objects these
			depend on) will be yielded.

		``"all"``
			All tables from all users will be yielded.
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
		Generator that yields the sequences, tables, primary keys, foreign keys,
		comments, unique constraints, indexes, views, functions, procedures,
		packages and types in the current users schema (or all users schemas)
		in a specified order.

		:var:`mode` specifies the order in which objects will be yielded:

		``"create"``
			Create order, i.e. recreating the objects in this order will not lead
			to errors.

		``"drop"``
			Drop order, i.e. dropping the objects in this order will not lead to
			errors.

		``"flat"``
			Unordered.

		:var:`schema` specifies from which schema objects should be yielded:

		``"user"``
			Only objects belonging to the current user (and those objects these
			depend on) will be yielded.

		``"all"``
			All objects from all users will be yielded.
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

	def _getobject(self, name, owner=None):
		cursor = self.cursor()
		cursor.execute("select object_name, decode(owner, user, null, owner) as owner, object_type from all_objects where object_name = :object_name and owner = nvl(:owner, user)", object_name=name, owner=owner)
		rec = cursor.fetchone()
		if rec is not None:
			type = rec.object_type.lower()
			try:
				cls = Object.name2type[type]
			except KeyError:
				raise TypeError("type %s not supported" % type)
			else:
				return cls(rec.object_name, rec.owner, self)
		raise SQLNoSuchObjectError(name, owner)

	def getobject(self, name, owner=None):
		"""
		Return the object named :var:`name` from the schema. If :var:`owner` is
		:const:`None` the current schema is queried, else the specified one is
		used. :var:`name` and :var:`owner` are treated case insensitively.
		"""
		cursor = self.cursor()
		for query in (
			"select object_name, decode(owner, user, null, owner) as owner, object_type from all_objects where object_name = :object_name and owner = nvl(:owner, user)",
			"select object_name, decode(owner, user, null, owner) as owner, object_type from all_objects where object_name = :object_name and lower(owner) = lower(nvl(:owner, user))",
			"select object_name, decode(owner, user, null, owner) as owner, object_type from all_objects where lower(object_name) = lower(:object_name) and owner = nvl(:owner, user)",
			"select object_name, decode(owner, user, null, owner) as owner, object_type from all_objects where lower(object_name) = lower(:object_name) and lower(owner) = lower(nvl(:owner, user))",
		):
			cursor.execute(query, object_name=name, owner=owner)
			rec = cursor.fetchone()
			if rec is not None:
				type = rec.object_type.lower()
				try:
					cls = Object.name2type[type]
				except KeyError:
					raise TypeError("type %s not supported" % type)
				else:
					return cls(rec.object_name, rec.owner, self)
		raise SQLNoSuchObjectError(name, owner)

	def iterprivileges(self, schema="user"):
		"""
		Generator that yields object privileges for the current users (or all
		users) objects. :var:`schema` specifies which privileges should be
		yielded:

		``"user"``
			Only object privileges for objects belonging to the current user will
			be yielded.

		``"all"``
			All object privileges will be yielded.
		"""
		return Privilege.iterobjects(self, schema)


def connect(*args, **kwargs):
	"""
	Create a connection to the database and return a :class:`Connection` object.
	"""
	return Connection(*args, **kwargs)


class Cursor(Cursor):
	"""
	A subclass of the cursor class in :mod:`cx_Oracle`. The "execute" methods
	support a unicode statement and unicode parameters (they will be encoded in
	the client encoding before being passed to the database). The "fetch" methods
	will return records as :class:`Record` objects and string values and
	``CLOB`` values, if the cursors :attr:`readlobs` attribute has the
	appropriate value) will be returned as :class:`unicode` objects (except for
	``BLOB`` values). (Note that strings in the national character set
	(and ``NCLOB`` values) are not supported).
	"""
	def __init__(self, connection, readlobs=None):
		"""
		Return a new cursor for the connection :var:`connection`. For the meaning
		of :var:`readlobs` see :meth:`Connection.__init__`.
		"""
		super(Cursor, self).__init__(connection)
		self.readlobs = (readlobs if readlobs is not None else connection.readlobs)

	def _decode(self, value, isblob):
		if isinstance(value, LOB) and (self.readlobs is True or (isinstance(self.readlobs, (int, long)) and value.size() <= self.readlobs)):
			value = value.read()
		if isinstance(value, str) and not isblob:
			value = value.decode(self.connection.encoding)
		return value

	def _encode(self, value):
		# Helper method that encodes :var:`value` using the client encoding (if :var:`value` is :class:`unicode`)
		if isinstance(value, unicode):
			return value.encode(self.connection.encoding)
		return value

	def execute(self, statement, parameters=None, **kwargs):
		kwargs = dict((self._encode(key), self._encode(value)) for (key, value) in kwargs.iteritems())
		if parameters is not None:
			if isinstance(parameters, dict):
				parameters = dict((self._encode(key), self._encode(value)) for (key, value) in parameters.iteritems())
			else:
				parameters = map(self._encode, parameters)
			result = super(Cursor, self).execute(self._encode(statement), parameters, **kwargs)
		else:
			result = super(Cursor, self).execute(self._encode(statement), **kwargs)
		if self.description is not None:
			self.rowfactory = RecordMaker(self)
		return result

	def executemany(self, statement, parameters):
		def _encode(value):
			if isinstance(value, dict):
				return dict((self._encode(key), self._encode(value)) for (key, value) in value.iteritems())
			else:
				return map(self._encode, value)
		result = super(Cursor, self).executemany(self._encode(statement), map(_encode, parameters))
		if self.description is not None:
			self.rowfactory = RecordMaker(self)
		return result

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


def getfullname(name, owner):
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
	The base class for all Python classes modelling schema objects in the
	database.

	Subclasses are: :class:`Sequence`, :class:`Table`, :class:`PrimaryKey`,
	:class:`Comment`, :class:`ForeignKey`, :class:`Index`, :class:`Unique`,
	:class:`Synonym`, :class:`View`, :class:`MaterializedView`, :class:`Library`,
	:class:`Function`, :class:`Package`, :class:`Type`, :class:`Trigger`,
	:class:`JavaSource` and :class:`Column`.
	"""
	name2type = {} # maps the Oracle type name to the Python class (populated by the metaclass)

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

	def getfullname(self):
		return getfullname(self.name, self.owner)

	@misc.notimplemented
	def createddl(self, connection=None, term=True):
		"""
		Return SQL code to create this object.
		"""

	@misc.notimplemented
	def dropddl(self, connection=None, term=True):
		"""
		Return SQL code to drop this object
		"""

	@misc.notimplemented
	def cdate(self, connection=None):
		"""
		Return a :class:`datetime.datetime` object with the creation date of
		:var:`self` in the database specified by :var:`connection` (or
		:const:`None` if such information is not available).
		"""

	@misc.notimplemented
	def udate(self, connection=None):
		"""
		Return a :class:`datetime.datetime` object with the last modification
		date of :var:`self` in the database specified by :var:`connection`
		(or :const:`None` if such information is not available).
		"""

	def iterreferences(self, connection=None):
		"""
		Objects directly used by :var:`self`.

		If :var:`connection` is not :const:`None` it will be used as the database
		connection from which to fetch data. If :var:`connection` is :const:`None`
		the connection from which :var:`self` has been extracted will be used. If
		there is not such connection, you'll get an exception.
		"""
		(connection, cursor) = self.getcursor(connection)
		cursor.execute("select referenced_type, decode(referenced_owner, user, null, referenced_owner) as referenced_owner, referenced_name from all_dependencies where type=upper(:type) and name=:name and owner=nvl(:owner, user) and type != 'NON-EXISTENT'", type=self.type, name=self.name, owner=self.owner)
		for rec in cursor.fetchall():
			try:
				type = Object.name2type[rec.referenced_type.lower()]
			except KeyError:
				pass # FIXME: Issue a warning?
			else:
				yield type(rec.referenced_name, rec.referenced_owner, connection)

	def iterreferencesall(self, connection=None, done=None):
		"""
		All objects used by :var:`self` (recursively).

		For the meaning of :var:`connection` see :meth:`iterreferences`.

		:var:`done` is used internally and shouldn't be passed.
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
		Objects using :var:`self`.

		For the meaning of :var:`connection` see :meth:`iterreferences`.
		"""
		(connection, cursor) = self.getcursor(connection)
		cursor.execute("select type, decode(owner, user, null, owner) as owner, name from all_dependencies where referenced_type=upper(:type) and referenced_name=:name and referenced_owner=nvl(:owner, user) and type != 'NON-EXISTENT'", type=self.type, name=self.name, owner=self.owner)
		for rec in cursor.fetchall():
			try:
				type = Object.name2type[rec.type.lower()]
			except KeyError:
				pass # FIXME: Issue a warning?
			else:
				yield type(rec.name, rec.owner, connection)

	def iterreferencedbyall(self, connection=None, done=None):
		"""
		All objects depending on :var:`self` (recursively).

		For the meaning of :var:`connection` see :meth:`iterreferences`.

		:var:`done` is used internally and shouldn't be passed.
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
		Generator that yields all objects of this type in the database schema
		of :var:`cursor`.
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
		code  = "create sequence %s\n" % self.getfullname()
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
		Return SQL code to create an identical copy of this sequence.
		"""
		return self._createddl(connection, term, True)

	def dropddl(self, connection=None, term=True):
		code = "drop sequence %s" % self.getfullname()
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
		code = ["create table %s\n(\n" % self.getfullname()]
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
		code = "drop table %s" % self.getfullname()
		if term:
			code += ";\n"
		else:
			code += "\n"
		return code

	def mview(self, connection=None):
		"""
		The materialized view this table belongs to (or :const:`None` if it's a
		real table).
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
		Generator that yields all column objects of the :class:`Table` :var:`self`.
		"""
		(connection, cursor) = self.getcursor(connection)
		cursor.execute("select column_name from all_tab_columns where owner=nvl(:owner, user) and table_name=:name order by column_id", owner=self.owner, name=self.name)

		for rec in cursor.fetchall():
			yield Column("%s.%s" % (self.name, rec.column_name), self.owner, connection)

	def iterrecords(self, connection=None):
		"""
		Generator that yields all records of the table :var:`self`.
		"""
		(connection, cursor) = self.getcursor(connection)
		query = "select * from %s" % self.getfullname()
		cursor.execute(query)
		return iter(cursor)

	def itercomments(self, connection=None):
		"""
		Generator that yields all column comments of the table :var:`self`.
		"""
		(connection, cursor) = self.getcursor(connection)
		cursor.execute("select column_name from all_tab_columns where owner=nvl(:owner, user) and table_name=:name order by column_id", owner=self.owner, name=self.name)
		for rec in cursor.fetchall():
			yield Comment("%s.%s" % (self.name, rec.column_name), self.owner, connection)

	def iterconstraints(self, connection=None):
		"""
		Generator that yields all constraints for this table.
		"""
		(connection, cursor) = self.getcursor(connection)
		# Primary and unique key(s)
		cursor.execute("select decode(owner, user, null, owner) as owner, constraint_type, constraint_name from all_constraints where constraint_type in ('P', 'U', 'R') and owner=nvl(:owner, user) and table_name=:name", owner=self.owner, name=self.name)
		types = {"P": PrimaryKey, "U": UniqueConstraint, "R": ForeignKey}
		for rec in cursor.fetchall():
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
	Base class of all constraints (primary key constraints, foreign key
	constraints and unique constraints).
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
		tablename = getfullname(rec2.table_name, rec2.owner)
		pkname = getfullname(self.name, None)
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
		tablename = getfullname(rec.table_name, rec.owner)
		pkname = getfullname(self.name, None)
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
		return row[0]

	def iterreferencedby(self, connection=None):
		(connection, cursor) = self.getcursor(connection)
		cursor.execute("select decode(owner, user, null, owner) as owner, constraint_name from all_constraints where constraint_type='R' and r_owner=nvl(:owner, user) and r_constraint_name=:name", owner=self.owner, name=self.name)
		for rec in cursor.fetchall():
			yield ForeignKey(rec.constraint_name, rec.owner, connection)

		cursor.execute("select decode(owner, user, null, owner) as owner, index_name from all_indexes where owner=nvl(:owner, user) and index_name=:name", owner=self.owner, name=self.name)
		rec = cursor.fetchone() # Is there an index for this constraint?
		if rec is not None:
			yield Index(rec.index_name, rec.owner, connection)

	def iterreferences(self, connection=None):
		(connection, cursor) = self.getcursor(connection)
		cursor.execute("select decode(owner, user, null, owner) as owner, table_name from all_constraints where constraint_type='P' and owner=nvl(:owner, user) and constraint_name=:name", owner=self.owner, name=self.name)
		for rec in cursor.fetchall():
			yield Table(rec.table_name, rec.owner, connection)

	def table(self, connection=None):
		"""
		Return the :class:`Table` :var:`self` belongs to.
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

		name = self.getfullname()
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
		fields2 = ", ".join("%s(%s)" % (getfullname(r.table_name, rec.r_owner), r.column_name) for r in cursor)
		tablename = getfullname(rec.table_name, self.owner)
		fkname = getfullname(self.name, None)
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
		tablename = getfullname(rec.table_name, self.owner)
		fkname = getfullname(self.name, None)
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
		return row[0]

	def iterreferencedby(self, connection=None):
		# Shortcut: Nobody references a foreign key
		if False:
			yield None

	def iterreferences(self, connection=None):
		yield self.table(connection)
		yield self.pk(connection)

	def table(self, connection=None):
		"""
		Return the :class:`Table` :var:`self` belongs to.
		"""
		(connection, cursor) = self.getcursor(connection)
		cursor.execute("select table_name from all_constraints where constraint_type='R' and owner=nvl(:owner, user) and constraint_name=:name", owner=self.owner, name=self.name)
		rec = cursor.fetchone()
		return Table(rec.table_name, self.owner, connection)

	def pk(self, connection=None):
		"""
		Return the primary key referenced by :var:`self`.
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
		return rec[0] == "ENABLED"

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
		tablename = getfullname(rec.table_name, self.owner)
		indexname = self.getfullname()
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
		code = "drop index %s" % getfullname(self.name, self.owner)
		if term:
			code += ";\n"
		else:
			code += "\n"
		return code

	def constraint(self, connection=None):
		"""
		If this index is generated by a constraint, return the constraint
		otherwise return :const:`None`.
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
		Return the :class:`Table` :var:`self` belongs to.
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
		tablename = getfullname(rec.table_name, self.owner)
		uniquename = getfullname(self.name, None)
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
		tablename = getfullname(rec.table_name, self.owner)
		uniquename = getfullname(self.name, None)
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
		return row[0]

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
		cursor.execute("select decode(owner, user, null, owner) as owner, table_name from all_constraints where constraint_type='U' and owner=nvl(:owner, user) and constraint_name=:name", owner=self.owner, name=self.name)
		for rec in cursor.fetchall():
			yield Table(rec.table_name, rec.owner, connection)

	def table(self, connection=None):
		"""
		Return the :class:`Table` :var:`self` belongs to.
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
		name = getfullname(self.name, owner)
		name2 = getfullname(rec.table_name, rec.table_owner)
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
		name = getfullname(self.name, owner)
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

	def getobject(self, connection=None):
		"""
		Get the object for which :var:`self` is a synonym.
		"""
		(connection, cursor) = self.getcursor(connection)
		cursor.execute("select table_owner, table_name, db_link from all_synonyms where owner=nvl(:owner, user) and synonym_name=:name", owner=self.owner, name=self.name)
		rec = cursor.fetchone()
		if rec is None:
			raise SQLObjectNotFoundError(self)
		return connection._getobject(rec.table_name, rec.table_owner)


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
		code = "create or replace view %s as\n\t%s" % (self.getfullname(), code)
		if term:
			code += "\n/\n"
		else:
			code += "\n"
		return code

	def dropddl(self, connection=None, term=True):
		code = "drop view %s" % self.getfullname()
		if term:
			code += ";\n"
		else:
			code += "\n"
		return code

	def iterrecords(self, connection=None):
		(connection, cursor) = self.getcursor(connection)
		query = "select * from %s" % self.getfullname()
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
		code = "create materialized view %s\nrefresh %s on %s as\n\t%s" % (self.getfullname(), rec.refresh_method, rec.refresh_mode, code)
		if term:
			code += "\n/\n"
		else:
			code += "\n"
		return code

	def dropddl(self, connection=None, term=True):
		code = "drop materialized view %s" % self.getfullname()
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
		return "create or replace library %s as %r" % (self.getfullname(), rec.file_spec)
		if term:
			code += ";\n"
		else:
			code += "\n"
		return code

	def dropddl(self, connection=None, term=True):
		code = "drop library %s" % self.getfullname()
		if term:
			code += ";\n"
		else:
			code += "\n"
		return code


class Argument(object):
	"""
	:class:`Argument` objects hold information about the arguments of a
	stored procedure.
	"""
	def __init__(self, name, position, datatype, isin, isout):
		self.name = name
		self.position = position
		self.datatype = datatype
		self.isin = isin
		self.isout = isout

	def __repr__(self):
		return "<%s.%s name=%r position=%r datatype=%r at 0x%x>" % (self.__class__.__module__, self.__class__.__name__, self.name, self.position, self.datatype, id(self))

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
	
	_py2cx = {
		datetime.datetime: DATETIME,
		int: NUMBER,
		long: NUMBER,
		float: NUMBER,
		str: STRING,
	}
	
	def __init__(self, name, owner=None, connection=None):
		Object.__init__(self, name, owner, connection)
		self._argsbypos = None
		self._argsbyname = None
		self._returnvalue = None

	def _calcargs(self, cursor):
		if self._argsbypos is None:
			cursor.execute("select object_id from all_objects where owner=nvl(:owner, user) and object_name=:name and object_type=:type", owner=self.owner, name=self.name, type=self.type.upper())
			if cursor.fetchone() is None:
				raise SQLObjectNotFoundError(self)
			self._argsbypos = []
			self._argsbyname = {}
			cursor.execute("select lower(argument_name) as name, lower(in_out) as in_out, lower(data_type) as datatype from all_arguments where owner=nvl(:owner, user) and object_name=:name and data_level=0 order by sequence", owner=self.owner, name=self.name)
			i = 0 # argument position (skip return value)
			for record in cursor:
				arginfo = Argument(record.name, i, record.datatype, "in" in record.in_out, "out" in record.in_out)
				if record.name is None: # this is the return value
					self._returnvalue = arginfo
				else:
					self._argsbypos.append(arginfo)
					self._argsbyname[arginfo.name] = arginfo
					i += 1

	def _getargs(self, cursor, *args, **kwargs):
		queryargs = {}

		if len(args) > len(self._argsbypos):
			raise TypeError("too many parameters for %r: %d given, %d expected" % (self, len(args), len(self._argsbypos)))

		# Handle positional arguments
		for (arg, arginfo) in itertools.izip(args, self._argsbypos):
			queryargs[arginfo.name] = self._wraparg(cursor, arginfo, arg)

		# Handle keyword arguments
		for (argname, arg) in kwargs.iteritems():
			argname = argname.lower()
			if argname in queryargs:
				raise TypeError("duplicate argument for %r: %s" % (self, argname))
			try:
				arginfo = self._argsbyname[argname]
			except KeyError:
				raise TypeError("unknown parameter for %r: %s" % (self, argname))
			queryargs[arginfo.name] = self._wraparg(cursor, arginfo, arg)

		# Add out parameters for anything that hasn't been specified
		for arginfo in self._argsbypos:
			if arginfo.name not in queryargs and arginfo.isout:
				queryargs[arginfo.name] = self._wraparg(cursor, arginfo, None)

		return queryargs

	def _wraparg(self, cursor, arginfo, arg):
		arg = cursor._encode(arg)
		try:
			if arg is None:
				t = self._ora2cx[arginfo.datatype]
			else:
				t = self._py2cx[type(arg)]
		except KeyError:
			raise TypeError("can't handle parameter %s of type %s in %r" % (arginfo.name, arginfo.datatype, self))
		if t is STRING and isinstance(arg, str) and len(arg) >= 4000:
			t = CLOB
		var = cursor.var(t)
		var.setvalue(0, arg)
		return var

	def _unwraparg(self, cursor, arginfo, arg):
		try:
			arg = arg.getvalue(0)
		except AttributeError:
			pass
		return cursor._decode(arg, arginfo.datatype == "blob")

	def _makerecord(self, cursor, args):
		names = []
		values = []
		for arginfo in self._argsbypos:
			name = arginfo.name
			if name in args:
				names.append(name)
				values.append(self._unwraparg(cursor, arginfo, args[name]))
		return Record(names, values)

	def iterarguments(self, connection=None):
		"""
		Generator that yields all arguments of the function/procedure :var:`self`.
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
	Models a procedure in the database. A :class:`Procedure` object can be
	used as a wrapper for calling the procedure with keyword arguments.
	"""

	type = "procedure"

	def __call__(self, cursor, *args, **kwargs):
		"""
		Call the procedure with arguments :var:`args` and keyword arguments
		:var:`kwargs`. :var:`cursor` must be a :mod:`ll.orasql` cursor. This will
		return a :class:`Record` object containing the result of the call (i.e.
		this record will contain all specified and all out parameters).
		"""
		self._calcargs(cursor)

		if self.owner is None:
			name = self.name
		else:
			name = "%s.%s" % (self.owner, self.name)

		queryargs = self._getargs(cursor, *args, **kwargs)
	
		query = "begin %s(%s); end;" % (name, ", ".join("%s=>:%s" % (name, name) for name in queryargs))

		cursor.execute(query, queryargs)

		return self._makerecord(cursor, queryargs)


class Function(Callable):
	"""
	Models a function in the database. A :class:`Function` object can be
	used as a wrapper for calling the function with keyword arguments.
	"""
	type = "function"

	def __call__(self, cursor, *args, **kwargs):
		"""
		Call the function with arguments :var:`args` and keyword arguments
		:var:`kwargs`. :var:`cursor` must be an :mod:`ll.orasql` cursor.
		This will return a tuple containing the result and a :class:`Record`
		object containing the modified parameters (i.e. this record will contain
		all specified and out parameters).
		"""
		self._calcargs(cursor)

		if self.owner is None:
			name = self.name
		else:
			name = "%s.%s" % (self.owner, self.name)

		queryargs = self._getargs(cursor, *args, **kwargs)

		returnvalue = "r"
		while returnvalue in queryargs:
			returnvalue += "_"
		queryargs[returnvalue] = self._wraparg(cursor, self._returnvalue, None)

		query = "begin :%s := %s(%s); end;" % (returnvalue, name, ", ".join("%s=>:%s" % (name, name) for name in queryargs if name != returnvalue))

		cursor.execute(query, queryargs)

		returnvalue = self._unwraparg(cursor, self._returnvalue, queryargs.pop(returnvalue))

		return (returnvalue, self._makerecord(cursor, queryargs))


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

		code = "create or replace and compile java source named %s as\n%s\n" % (self.getfullname(), code)
		if term:
			code += "/\n"
		return code

	def dropddl(self, connection=None, term=True):
		code = "drop java source %s" % self.getfullname()
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
		Generator that yields object privileges for the current users (or all
		users) objects.

		:var:`schema` specifies which privileges should be yielded:

		``"user"``
			Only object privileges for objects belonging to the current user will
			be yielded.

		``"all"``
			All object privileges will be yielded.
		"""
		if schema not in ("user", "all"):
			raise UnknownSchemaError(schema)

		cursor = connection.cursor() # can't use :meth:`getcursor` as we're in a classmethod

		if schema == "all":
			cursor.execute("select decode(table_schema, user, null, table_schema) as owner, privilege, table_name as object, decode(grantor, user, null, grantor) as grantor, grantee from all_tab_privs order by table_schema, table_name, privilege")
		else:
			cursor.execute("select null as owner, privilege, table_name as object, decode(grantor, user, null, grantor) as grantor, grantee from user_tab_privs where owner=user order by table_name, privilege")
		return (Privilege(rec.privilege, rec.object, rec.grantor, rec.grantee, rec.owner, cursor.connection) for rec in cursor)

	def grantddl(self, connection=None, term=True, mapgrantee=True):
		"""
		Return SQL code to grant this privilege. If :var:`mapgrantee` is a list
		or a dictionary and ``self.grantee`` is not in this list (or dictionary)
		no command will returned. If it's a dictionary and ``self.grantee`` is
		in it, the privilege will be granted to the user specified as the value
		instead of the original one. If :var:`mapgrantee` is true (the default)
		the privilege will be granted to the original grantee.
		"""
		(connection, cursor) = self.getcursor(connection)
		if mapgrantee is True:
			grantee = self.grantee
		elif isinstance(mapgrantee, (list, tuple)):
			if self.grantee.lower() in (g.lower() or f in mapgrantee):
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
	``ALTER TABLE ...`` statements for adding, dropping and modifying columns.
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
		code = ["alter table %s add %s" % (getfullname(name[0], self.owner), getfullname(name[1], None))]
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

		code = ["alter table %s modify %s" % (getfullname(name[0], self.owner), getfullname(name[1], None))]
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
		code = "alter table %s drop column %s" % (getfullname(name[0], self.owner), getfullname(name[1], None))
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
		return row[0]

	def udate(self, connection=None):
		# The column modification date is the table modification date
		(connection, cursor) = self.getcursor(connection)
		cursor.execute("select last_ddl_time from all_objects where lower(object_type)='table' and object_name=:name and owner=nvl(:owner, user)", name=self.name.split(".")[0], owner=self.owner)
		row = cursor.fetchone()
		if row is None:
			raise SQLObjectNotFoundError(self)
		return row[0]

	def iterreferences(self, connection=None):
		connection = self.getconnection(connection)
		name = self.name.split(".")
		yield Table(name[0], self.owner, connection)

	def iterreferencedby(self, connection=None):
		if False:
			yield None

	def datatype(self, connection=None):
		"""
		The SQL type of this column.
		"""
		(connection, cursor) = self.getcursor(connection)
		rec = self._getcolumnrecord(cursor)
		return _columntype(rec)

	def default(self, connection=None):
		"""
		The SQL default value for this column.
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
