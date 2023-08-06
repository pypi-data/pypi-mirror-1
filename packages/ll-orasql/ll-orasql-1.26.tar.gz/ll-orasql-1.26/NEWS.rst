Changes in 1.26 (released 03/27/2009)
-------------------------------------

*	:mod:`ll.orasql` now requires cx_Oracle 5.0 compiled in Unicode mode
	(i.e. with ``WITH_UNICODE=1``). Lots of unicode handling stuff has been
	rewritten to take advantage of Unicode mode.

*	``orafind`` has a new option ``--encoding`` to decode the searchstring on the
	commandline.

*	The :class:`Pool` constructor now supports the additional arguments
	:var:`getmode` and :var:`homogeneous` from cx_Oracle 5.0.

*	Fix a typo in :meth:`Privilege.grantddl`.


Changes in 1.25.4 (released 01/21/2009)
---------------------------------------

*	Procedures and functions with timestamp arguments can now be called.


Changes in 1.25.3 (released 11/07/2008)
---------------------------------------

*	Procedures and functions now should handle arguments of type ``BLOB``
	correctly.


Changes in 1.25.2 (released 08/29/2008)
---------------------------------------

*	:class:`Record` has a new method :meth:`get` which works like the dictionary
	method :meth:`get`.


Changes in 1.25.1 (released 07/21/2008)
---------------------------------------

*	``orafind.py`` now has an additional options :option:`readlobs` (defaulting
	to false). If this option is set, the value of LOBs in the records found,
	will be printed.


Changes in 1.25 (released 06/17/2008)
-------------------------------------

*	A new script has been added: ``orafind.py`` will search for a specified
	string in all columns of all tables in a schema.


Changes in 1.24.1 (released 05/30/2008)
---------------------------------------

*	Fixed two bugs in :meth:`Callable._calcargs` and :meth:`Connection.getobject`.


Changes in 1.24 (released 05/20/2008)
---------------------------------------

*	:meth:`Connection.getobject`, :class:`Procedure` and :class:`Function` now
	support functions and procedures in packages.

*	Added :meth:`__repr__` to the exception classes.


Changes in 1.23.4 (released 04/04/2008)
---------------------------------------

*	All database scripts now have an additional option :option:`encoding` that
	specifies the encoding for the output script.


Changes in 1.23.3 (released 04/03/2008)
---------------------------------------

*	Fixed a regression in the scripts ``oracreate.py``, ``oradrop.py`` and
	``oragrant.py``.


Changes in 1.23.2 (released 04/01/2008)
---------------------------------------

*	When calling functions/procedures, arguments are now wrapped in variable
	objects for their real type instead of ones for the type the function or
	procedure expects.


Changes in 1.23.1 (released 03/25/2008)
---------------------------------------

*	Added a :meth:`__contains__` to :class:`Record` for checking the existence
	of a field.


Changes in 1.23 (released 03/25/2008)
-------------------------------------

*	Calling procedures and functions has been rewritten: :mod:`ll.orasql` will
	only pass those parameters to the procedure/function that are passed to the
	call (or variables for out parameters). Internally this is handled by
	executing the call as a parameterized query calling the procedure/function
	with named arguments.

*	:class:`FetchRecord` has been renamed to :class:`Record` (and is used for
	the result of procedure and function calls now, which required some internal
	changes to :class:`FetchRecord`). The former :class:`Record` has been renamed
	to :class:`Args` as its only use now is collecting arguments for
	procedure/function calls. (The method :meth:`fromdata` has been dropped.)

*	The :meth:`__repr__` output of :class:`Argument` objects now shows the
	datatype.


Changes in 1.22 (released 03/19/2008)
-------------------------------------

*	Added a new method :meth:`_getobject` to :class:`Connection` that does
	what :meth:`getobject` does, but is case sensitive (This is used internally
	by :meth:`Synonym.getobject`).

*	The methods :meth:`xfetchone`, :meth:`xfetchmany`, :meth:`xfetchall`,
	:meth:`xfetch`, :meth:`xexecute` and :meth:`xexecutemany` have been dropped
	again. Fetch result objects are now of type :class:`FetchRecord`. Field
	access is available via index (i.e. ``row[0]``), key (``row["name"]``)
	and attribute (``row.name``). These result objects are generated via the
	:attr:`rowfactory` attribute (which was added in cx_Oracle 4.3.2).
	All fetch and execute methods support unicode values.


Changes in 1.21.1 (released 03/17/2008)
---------------------------------------

*	Updated the scripts to work with the new execute methods.


Changes in 1.21 (released 03/13/2008)
-------------------------------------

*	:class:`Connection` has a new method :meth:`getobject`, which returns the
	schema object with a specified name.

*	:class:`Synonym` has a new method :meth:`getobject`, that returns the object
	for which the :class:`Synonym` object is a synonym.

*	The name of :class:`Procedure` and :class:`Function` objects now is case
	sensitive when calling the procedure or function.



Changes in 1.20 (released 02/07/2008)
-------------------------------------

*	The fancy fetch methods have been renamed to :meth:`xfetchone`,
	:meth:`xfetchmany`, :meth:`xfetchall` and :meth:`xfetch`. :meth:`__iter__`
	no longer gets overwritten. New methods :meth:`xexecute` and
	:meth:`xexecutemany` have been added, that support passing unicode
	parameters.


Changes in 1.19 (released 02/01/2008)
-------------------------------------

*	All docstrings use ReST now.


Changes in 1.18 (released 01/07/2008)
-------------------------------------

*	Updated the docstrings to XIST 3.0.

*	Added ReST versions of the documentation.


Changes in 1.17.5 (released 08/09/2007)
---------------------------------------

*	Fixed a bug in the error handling of wrong arguments when calling
	functions or procedures.


Changes in 1.17.4 (released 04/30/2007)
---------------------------------------

*	The threshold for string length for procedure and function arguments has
	been reduced to 4000.


Changes in 1.17.3 (released 03/08/2007)
---------------------------------------

*	``BLOB`` arguments for procedures and functions are always passed as
	variables now.


Changes in 1.17.2 (released 03/07/2007)
---------------------------------------

*	Arguments for procedures and functions that are longer that 32000 characters
	are passed as variables now (the threshold was 32768 before and didn't work).


Changes in 1.17.1 (released 03/02/2007)
---------------------------------------

*	Fix an inverted logic bug in :meth:`Record.fromdata` that surfaced in unicode
	mode: ``BLOB``\s were treated as string and ``CLOB``\s as binary data.


Changes in 1.17 (released 02/23/2007)
-------------------------------------

*	The :var:`readlobs` and :var:`unicode` parameters are now honored when
	calling procedures and functions via :class:`Procedure` and
	:class:`Function` objects.


Changes in 1.16 (released 02/21/2007)
-------------------------------------

*	A parameter :var:`unicode` has been added to various constructors and methods.
	This parameter can be used to get strings (i.e. ``VARCHAR2`` and ``CLOB``\s)
	as :class:`unicode` object instead of :class:`str` objects.


Changes in 1.15 (released 02/17/2007)
-------------------------------------

*	Fixed an output bug in ``oradiff.py`` when running in full output mode.

*	A parameter :var:`readlobs` has been added to various constructors and
	methods that can be used to get small (or all) ``LOB`` values as strings in
	cursor fetch calls.


Changes in 1.14 (released 02/01/2007)
-------------------------------------

*	A new method :meth:`iterprivileges` has been added to :class:`Connection`.

*	A script ``oragrant.py`` has been added for copying privileges.


Changes in 1.13 (released 11/06/2006)
-------------------------------------

*	Two new methods (:meth:`itertables` and :meth:`iterfks`) have been added to
	:class:`Connection`. They yield all table definitions or all foreign keys
	respectively.

*	A new method :meth:`isenabled` has been added to :class:`ForeignKey`.

*	A :meth:`__str__` method has been added to :class:`Object`.

*	A bug in ``oramerge.py`` has been fixed: In certain situations ``oramerge.py``
	used merging actions that were meant to be used for the preceeding object.


Changes in 1.12.2 (released 10/18/2006)
---------------------------------------

*	Fixed a bug that showed up when an index and a foreign key of the same name
	existed.


Changes in 1.12.1 (released 09/19/2006)
---------------------------------------

*	Fixed a bug in :meth:`Index.__xattrs__`.


Changes in 1.12 (released 09/06/2006)
-------------------------------------

*	:class:`Function` objects are now callable too. They return the return value
	and a :class:`Record` containing the modified input parameters.


Changes in 1.11.1 (released 08/29/2006)
---------------------------------------

*	Fixed a bug in :meth:`Column.modifyddl`.


Changes in 1.11 (released 08/22/2006)
-------------------------------------

*	The class :class:`Column` has gained a few new methods: :meth:`datatype`,
	:meth:`default`, :meth:`nullable` and :meth:`comment`.

*	Calling a procedure will now raise a :class:`SQLObjectNotFoundError` error,
	if the procedure doesn't exist.


Changes in 1.10 (released 08/11/2006)
-------------------------------------

*	The classes :class:`Proc` and :class:`LLProc` have been removed. The
	functionality of :class:`Proc` has been merged into
	:class:`ProcedureDefinition` (with has been renamed to :class:`Procedure`).
	Information about the procedure arguments is provided by the
	:meth:`iteraguments` method.

*	All other subclasses of :class:`Definition` have been renamed to remove the
	"Definition" for the name to reduce typing. (Methods have been renamed
	accordingly too.)</li>

*	:func:`oramerge.main` and :func:`oradiff.main` now accept option arrays as
	arguments.

*	``oradiff.py`` has finally been fixed.


Changes in 1.9.4 (released 08/09/2006)
--------------------------------------

*	Fixed a bug in ``oradiff.py``.


Changes in 1.9.3 (released 08/08/2006)
--------------------------------------

*	Fixed a bug in ``oramerge.py``.


Changes in 1.9.2 (released 08/04/2006)
--------------------------------------

*	Fixed a bug in :meth:`TableDefinition.iterdefinitions`.


Changes in 1.9.1 (released 08/02/2006)
--------------------------------------

*	Fixed a bug in ``oracreate.py``.


Changes in 1.9 (released 07/24/2006)
------------------------------------

*	Dependencies involving :class:`MaterializedViewDefinition` and
	:class:`IndexDefinition` objects generated by constraints work properly now,
	so that iterating all definitions in create order really results in a
	working SQL script.

*	A method :meth:`table` has been added to :class:`PKDefinition`,
	:class:`FKDefinition`, :class:`UniqueDefinition` and
	:class:`IndexDefinition`. This method returns the :class:`TableDefinition` to
	object belongs to.

*	A method :meth:`pk` has been added to :class:`FKDefinition`. It returns the
	primary key that this foreign key references.

*	Indexes and constraints belonging to skipped tables are now skipped too in
	``oracreate.py``.

*	Arguments other than ``sys.argv[1:]`` can now be passed to the
	``oracreate.py`` and ``oradrop.py`` :func:`main` functions.


Changes in 1.8.1 (released 07/17/2006)
--------------------------------------

*	:mod:`ll.orasql` can now handle objects name that are not in uppercase.


Changes in 1.8 (released 07/14/2006)
------------------------------------

*	:meth:`Connection.iterobjects` has been renamed to :meth:`iterdefinitions`.

*	Each :class:`Definition` subclass has a new classmethod
	:meth:`iterdefinitions` that iterates through all definitions of this type
	in a schema (or all schemas).

*	Each :class:`Definition` subclass has new methods :meth:`iterreferences` and
	:meth:`iterreferencedby` that iterate through related definitions. The
	methods :meth:`iterreferencesall` and :meth:`iterreferencedbyall` do this
	recursively. The method :meth:`iterdependent` is gone now.

*	The method :meth:`iterschema` of :class:`Connection` now has an additional
	parameter :var:`schema`. Passing ``"all"`` for :var:`schema` will give you
	statistics for the complete database not just one schema.

*	A new definition class :class:`MaterializedViewDefinition` has been added
	that handles materialized views. Handling of create options is rudimentary
	though. Patches are welcome.

*	:class:`TableDefinition` has a three new methods: :meth:`ismview` returns
	whether the table is a materialized view; :meth:`itercomments` iterates
	through comments and :meth:`iterconstraints` iterates through primary keys,
	foreign keys and unique constraints.

*	The method :meth:`getcursor` will now raise a :class:`TypeError` if it can't
	get a cursor.


Changes in 1.7.2 (released 07/05/2006)
--------------------------------------

*	``RAW`` fields in tables are now output properly in
	:meth:`TableDefinition.createddl`.

*	A class :class:`PackageBodyDefinition` has been added. ``oracreate.py`` will
	output package body definitions and ``oradrop.py`` will drop them.


Changes in 1.7.1 (released 07/04/2006)
--------------------------------------

*	Duplicate code in the scripts has been removed.

*	Fixed a bug in ``oramerge.py``: If the source to be diffed was long enough
	the call to ``diff3`` deadlocked.


Changes in 1.7 (released 06/29/2006)
------------------------------------

*	The method :meth:`iterobjects` has been moved from :class:`Cursor` to
	:class:`Connection`.

*	The method :meth:`itercolumns` has been moved from :class:`Cursor` to
	:class:`TableDefinition`.

*	:class:`LLProc` now recognizes the ``c_out`` parameter used by
	:mod:`ll.toxic` 0.8.

*	Support for positional arguments has been added for :class:`Proc` and
	:class:`LLProc`. Error messages for calling procedures have been enhanced.

*	:class:`SequenceDefinition` now has a new method :meth:`createddlcopy` that
	returns code that copies the sequence value. ``oracreate.py`` has a new
	option :option:`-s`/:option:`--seqcopy` that uses this feature.

*	:mod:`setuptools` is now supported for installation.


Changes in 1.6 (released 04/26/2006)
------------------------------------

*	Added a :class:`SessionPool` (a subclass of :class:`SessionPool` in
	:mod:`cx_Oracle`) whose :meth:`acquire` method returns
	:mod:`ll.orasql.Connection` objects.


Changes in 1.5 (released 04/05/2006)
------------------------------------

*	Added a class :class:`IndexDefinition` for indexes. ``oracreate.py`` will
	now issue create statements for indexes.


Changes in 1.4.3 (released 12/07/2005)
--------------------------------------

*	Fixed a bug with empty lines in procedure sources.

*	Remove spurious spaces at the start of procedure and function definitions.


Changes in 1.4.2 (released 12/07/2005)
--------------------------------------

*	Fixed a bug that the DDL output of Java source.

*	Trailing whitespace in each line of procedures, functions etc. is now stripped.


Changes in 1.4.1 (released 12/06/2005)
--------------------------------------

*	Fixed a bug that resulted in omitted field lengths.


Changes in 1.4 (released 12/05/2005)
------------------------------------

*	The option :option:`-m`/:option:`--mode` has been dropped from the script
	``oramerge.py``.

*	A new class :class:`ColumnDefinition` has been added to :mod:`ll.orasql`.
	The :class:`Cursor` class has a new method :meth:`itercolumns` that iterates
	the :class:`ColumnDefinition` objects of a table.

*	``oramerge.py`` now doesn't output a merged ``create table`` statement, but
	the appropriate ``alter table`` statements.


Changes in 1.3 (released 11/24/2005)
------------------------------------

*	Added an option :option:`-i` to ``oracreate.py`` and ``oradrop.py`` to
	ignore errors.

*	The argument :var:`all` of the cursor method :meth:`iterobjects` is now
	named :var:`schema` and may have three values: ``"own"``, ``"dep"`` and
	``"all"``.

*	Added an script ``oramerge.py`` that does a three way merge of three database
	schemas and outputs the resulting script.

*	DB links are now copied over in :class:`SynonymDefinition` objects.


Changes in 1.2 (released 10/24/2005)
------------------------------------

*	Added a argument to :meth:`createddl` and :meth:`dropddl` to specify if
	terminated or unterminated DDL is wanted (i.e. add ``;`` or ``/`` or not).

*	:class:`CommentsDefinition` has been renamed to :class:`CommentDefinition`
	and holds the comment for one field only.

*	:class:`JavaSourceDefinition` has been added.

*	The scripts ``oracreate.py``, ``oradrop.py`` and ``oradiff.py`` now skip
	objects with ``"$"`` in their name by default. This can be changed with the
	:option:`-k` option (but this will lead to unexecutable scripts).

*	``oradiff.py`` has a new options :option:`-b`: This allows you to specify
	how whitespace should be treated.

*	Added an option :option:`-x` to ``oracreate.py`` to make it possible to
	directly execute the DDL in another database.

*	Fixed a bug in :class:`SequenceDefinition` when the ``CACHE`` field was ``0``.


Changes in 1.1 (released 10/20/2005)
------------------------------------

*	A script ``oradiff.py`` has been added which can be used for diffing Oracle
	schemas.

*	Definition classes now have two new methods :meth:`cdate` and :meth:`udate`
	that give the creation and modification time of the schema object
	(if available).

*	A ``"flat"`` iteration mode has been added to :meth:`Cursor.iterobjects` that
	returns objects unordered.

*	:class:`Connection` has a new method :meth:`connectstring`.

*	A class :class:`LibraryDefinition` has been added.

*	:meth:`CommentsDefinition.createddl` returns ``""`` instead of ``"\n"`` now
	if there are no comments.

*	:class:`SQLObjectNotfoundError` has been renamed to
	:class:`SQLObjectNotFoundError`.


Changes in 1.0 (released 10/13/2005)
------------------------------------

*	:mod:`ll.orasql` requires version 1.0 of the core package now.

*	A new generator method :func:`iterobjects` has been added to the
	:class:`Cursor` class. This generator returns "definition objects" for all
	the objects in a schema in topological order (i.e. if the name of an object
	(e.g. a table) is generated it will only depend on objects whose name has
	been yielded before). SQL for recreating and deleting these SQL objects can
	be generated from the definition objects.

*	Two scripts (``oracreate.py`` and ``oradrop.py``) have been added, that
	create SQL scripts for recreating or deleting the content of an Oracle schema.


Changes in 0.7 (released 08/09/2005)
------------------------------------

*	The commands generated by :func:`iterdrop` no longer have a terminating ``;``,
	as this seems to confuse Oracle/cx_Oracle.


Changes in 0.6 (released 06/20/2005)
------------------------------------

*	Two new functions have been added: :func:`iterdrop` is a generator that
	yields information about how to clear the schema (i.e. drop all table,
	sequences, etc.). :func:`itercreate` yields information about how to recreate
	a schema.


Changes in 0.5 (released 06/07/2005)
------------------------------------

*	Date values are now supported as ``OUT`` parameters.


Changes in 0.4.1 (released 03/22/2005)
--------------------------------------

*	Added a note about the package init file to the installation documentation.


Changes in 0.4 (released 01/03/2005)
------------------------------------

*	:mod:`ll.orasql` now requires ll-core.

*	Procedures can now be called with string arguments longer that 32768
	characters. In this case the argument will be converted to a variable before
	the call. The procedure argument must be a ``CLOB`` in this case.

*	Creating :class:`Record` instances from database data is now done by the
	class method :meth:`Record.fromdata`. This means it's now possible to use any
	other class as long as it provides this method.


Changes in 0.3 (released 12/09/2004)
------------------------------------

*	:mod:`ll.orasql` requires cx_Oracle 4.1 now.


Changes in 0.2.1 (released 09/09/2004)
--------------------------------------

*	Fixed a regression bug in :meth:`Proc._calcrealargs` as cursors will now
	always return :class:`Record` objects.


Changes in 0.2 (released 09/08/2004)
------------------------------------

*	Now generating :class:`Record` object is done automatically in a subclass of
	:class:`cx_Oracle.Cursor`. So now it's possible to use :mod:`ll.orasql` as an
	extended :mod:`cx_Oracle`.


Changes in 0.1 (released 07/15/2004)
------------------------------------

*	Initial release.
