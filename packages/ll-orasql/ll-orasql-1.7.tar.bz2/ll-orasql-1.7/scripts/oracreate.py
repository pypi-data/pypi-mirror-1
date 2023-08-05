#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

## Copyright 2005 by LivingLogic AG, Bayreuth/Germany.
## Copyright 2005 by Walter Dörwald
##
## All Rights Reserved
##
## See orasql.py for the license


import sys, os, optparse

from ll import astyle, orasql


s4warning = astyle.Style.fromenv("LL_ORASQL_REPRANSI_WARNING", "red:black")
s4error = astyle.Style.fromenv("LL_ORASQL_REPRANSI_ERROR", "red:black")
s4connectstring = astyle.Style.fromenv("LL_ORASQL_REPRANSI_CONNECTSTRING", "green:black")
s4definition = astyle.Style.fromenv("LL_ORASQL_REPRANSI_DEFINITION", "blue:black")


if __name__ == "__main__":
	colors = ("yes", "no", "auto")
	p = optparse.OptionParser(usage="usage: %prog [options] connectstring >output.sql")
	p.add_option("-v", "--verbose", dest="verbose", help="Give a progress report?", default=False, action="store_true")
	p.add_option("-c", "--color", dest="color", help="Color output (%s)" % ", ".join(colors), default="auto", choices=colors)
	p.add_option("-s", "--seqcopy", dest="seqcopy", help="copy sequence values?", default=False, action="store_true")
	p.add_option("-x", "--execute", metavar="CONNECTSTRING2", dest="execute", help="Execute in target database", type="str")
	p.add_option("-k", "--keepdollar", dest="keepdollar", help="Output objects with '$' in their name?", default=False, action="store_true")
	p.add_option("-i", "--ignore", dest="ignore", help="Ignore errors?", default=False, action="store_true")

	(options, args) = p.parse_args()
	if len(args) != 1:
		p.error("incorrect number of arguments")
		sys.exit(1)

	if options.color == "yes":
		color = True
	elif options.color == "no":
		color = False
	else:
		color = None
	stdout = astyle.Stream(sys.stdout, color)
	stderr = astyle.Stream(sys.stderr, color)

	connection = orasql.connect(args[0])
	cursor = connection.cursor()

	if options.execute:
		connection2 = orasql.connect(options.execute)
		cursor2 = connection2.cursor()
		term = False
	else:
		term = True

	cs1 = s4connectstring(cursor.connection.connectstring())
	if options.execute:
		cs2 = s4connectstring(cursor2.connection.connectstring())

	for (i, definition) in enumerate(connection.iterobjects(mode="create", schema="own")):
		keep = "$" not in definition.name or options.keepdollar
		if options.verbose:
			if options.execute:
				msg = astyle.style_default("oracreate.py: ", cs1, " -> ", cs2, ": fetching/creating #%d" % (i+1))
			else:
				msg = astyle.style_default("oracreate.py: ", cs1, " fetching #%d" % (i+1))
			msg = astyle.style_default(msg, " ", s4definition(repr(definition)))
			if not keep:
				msg = astyle.style_default(msg, " ", s4warning("(skipped)"))
			stderr.writeln(msg)
		if keep:
			if isinstance(definition, orasql.SequenceDefinition) and options.seqcopy:
				ddl = definition.createddlcopy(cursor, term)
			else:
				ddl = definition.createddl(cursor, term)
			if ddl:
				if options.execute:
					try:
						cursor2.execute(ddl)
					except orasql.DatabaseError, exc:
						if not options.ignore or "ORA-01013" in str(exc):
							raise
						stderr.writeln("oracreate.py: ", s4error("%s: %s" % (exc.__class__.__name__, str(exc).strip())))
				else:
					stdout.writeln(ddl)
					stdout.writeln()
