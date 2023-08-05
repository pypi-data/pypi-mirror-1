#! /usr/bin/env/python
# -*- coding: iso-8859-1 -*-

## Copyright 2004-2006 by LivingLogic AG, Bayreuth/Germany.
## Copyright 2004-2006 by Walter Dörwald
##
## All Rights Reserved
##
## See orasql/__init__.py for the license


import os, datetime

from ll import orasql
from ll.orasql.scripts import oracreate, oradrop


dbname = os.environ["CONNECTSTRING"] # Need a connectstring as environment var


# here all definitions are collected, so we don't need to call iterdefinitions() multiple times
deflist = []
defdict = {}


def setup_module(module):
	db = orasql.connect(dbname)
	# get all definitions (this tests that iterdefinition(), iterreferences() and iterreferencedby() run to completion)
	module.defdict = {}
	for definition in db.iterdefinitions():
		module.deflist.append(definition)
		references = list(definition.iterreferences())
		referencedby = list(definition.iterreferencedby())
		module.defdict[definition] = (references, referencedby)


def teardown_module(module):
	del module.deflist
	del module.defdict


def test_connect():
	db = orasql.connect(dbname)
	assert isinstance(db, orasql.Connection)


def test_connection_connectstring():
	db = orasql.connect(dbname)
	user = dbname.split("/")[0]
	name = dbname.split("@")[1]
	assert "%s@%s" % (user, name) == db.connectstring()


def test_connection_iterschema():
	db = orasql.connect(dbname)
	list(db.iterschema())


def test_referenceconsistency():
	for (definition, (references, referencedby)) in defdict.iteritems():
		for refdef in references:
			# check that iterdefinitions() returned everything from this schema
			assert refdef.owner is not None or refdef in defdict
			# check that the referenced definition points back to this one (via referencedby)
			if refdef.owner is None:
				assert definition in defdict[refdef][1]

		# do the inverted check
		for refdef in referencedby:
			assert refdef.owner is not None or refdef in defdict
			if refdef.owner is None:
				assert definition in defdict[refdef][0]


def test_ddl():
	# check various ddl methods
	for definition in defdict:
		definition.createddl()
		if isinstance(definition, orasql.SequenceDefinition):
			definition.createddlcopy()
		definition.dropddl()
		if isinstance(definition, orasql.FKDefinition):
			definition.enableddl()
			definition.disableddl()


def test_repr():
	# check that each repr method works
	for definition in defdict:
		repr(definition)


def test_cudate():
	# check that cdate/udate method works
	for definition in defdict:
		cdate = definition.cdate()
		assert cdate is None or isinstance(cdate, datetime.datetime)
		udate = definition.udate()
		assert udate is None or isinstance(udate, datetime.datetime)


def test_table_columns():
	for definition in defdict:
		if isinstance(definition, orasql.TableDefinition):
			for col in definition.itercolumns():
				# comments are not output by iterdefinitions(), so we have to call iterreferences() instead of using definitions
				assert definition in col.iterreferences()
				# check various methods
				# calling modifyddl() doesn't make sense
				col.addddl()
				col.dropddl()
				col.cdate()
				col.udate()


def test_table_comments():
	for definition in defdict:
		if isinstance(definition, orasql.TableDefinition):
			# comments are output by iterdefinitions(), but not for materialized views
			if definition.ismview():
				for com in definition.itercomments():
					assert definition in com.iterreferences()
			else:
				for com in definition.itercomments():
					assert definition in defdict[com][0]


def test_table_constraints():
	for definition in defdict:
		if isinstance(definition, orasql.TableDefinition):
			for con in definition.iterconstraints():
				assert definition in defdict[con][0]


def test_table_records():
	for definition in defdict:
		if isinstance(definition, orasql.TableDefinition):
			# fetch only a few records
			for (i, rec) in enumerate(definition.iterrecords()):
				if i >= 5:
					break


def test_table_mview():
	for definition in defdict:
		if isinstance(definition, orasql.TableDefinition):
			assert (definition.mview() is not None) == definition.ismview()


def test_constaints():
	for definition in defdict:
		if isinstance(definition, orasql.ConstraintDefinition):
			definition.table()
			if isinstance(definition, orasql.FKDefinition):
				definition.pk()


def test_createorder():
	# check that the default output order of iterdefinitions() (i.e. create order) works
	done = set()
	for definition in deflist:
		for refdef in defdict[definition][0]:
			print definition, refdef
			assert refdef in done
		done.add(definition)


def test_scripts():
	# Test oracreate without executing anything
	args = "--color yes --verbose --seqcopy %s" % dbname
	oracreate.main(args.split())

	# Test oradrop without executing anything
	args = "--color yes --verbose %s" % dbname
	oradrop.main(args.split())
	
