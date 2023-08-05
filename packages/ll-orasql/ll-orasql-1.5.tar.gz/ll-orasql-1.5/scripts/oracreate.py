#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

## Copyright 2005 by LivingLogic AG, Bayreuth/Germany.
## Copyright 2005 by Walter Dörwald
##
## All Rights Reserved
##
## See orasql.py for the license


import sys, os, optparse

from ll import ansistyle, orasql


color4warning = 0010
color4error = 0010
color4connectstring = 0040
color4definition = 0020


if __name__ == "__main__":
	colors = ("yes", "no", "auto")
	p = optparse.OptionParser(usage="usage: %prog [options] connectstring >output.sql")
	p.add_option("-v", "--verbose", dest="verbose", help="Give a progress report?", default=False, action="store_true")
	p.add_option("-c", "--color", dest="color", help="Color output (%s)" % ", ".join(colors), default="auto", choices=colors)
	p.add_option("-x", "--execute", metavar="CONNECTSTRING2", dest="execute", help="Execute in target database", type="str")
	p.add_option("-k", "--keepdollar", dest="keepdollar", help="Output objects with '$' in their name?", default=False, action="store_true")
	p.add_option("-i", "--ignore", dest="ignore", help="Ignore errors?", default=False, action="store_true")

	(options, args) = p.parse_args()
	if len(args) != 1:
		p.error("incorrect number of arguments")
		sys.exit(1)

	if options.color == "yes":
		options.colorstdout = True
		options.colorstderr = True
	elif options.color == "no":
		options.colorstdout = False
		options.colorstderr = False
	else:
		try:
			options.colorstdout = os.isatty(sys.stdout.fileno())
			options.colorstderr = os.isatty(sys.stderr.fileno())
		except (KeyboardInterrupt, SystemExit):
			raise
		except Exception:
			options.colorstdout = False
			options.colorstderr = False

	connection = orasql.connect(args[0])
	cursor = connection.cursor()

	if options.execute:
		connection2 = orasql.connect(options.execute)
		cursor2 = connection2.cursor()
		term = False
	else:
		term = True

	cs1 = cursor.connection.connectstring()
	if options.colorstderr:
		cs1 = ansistyle.Text(color4connectstring, cs1)
	if options.execute:
		cs2 = cursor2.connection.connectstring()
		if options.colorstderr:
			cs2 = ansistyle.Text(color4connectstring, cs2)
		msgbase = "oracreate.py: %s -> %s: fetching/creating" % (cs1, cs2)
	else:
		msgbase = "oracreate.py: %s: fetching" % cs1

	for definition in cursor.iterobjects(mode="create", schema="own"):
		keep = "$" not in definition.name or options.keepdollar
		if options.verbose:
			msgdef = repr(definition)
			if options.colorstderr:
				msgdef = ansistyle.Text(color4definition, msgdef)
			msg = "%s %s" % (msgbase, msgdef)
			if not keep:
				warning = "(skipped)"
				if options.colorstderr:
					warning = ansistyle.Text(color4warning, warning)
				msg = "%s %s" % (msg, warning)
			print >>sys.stderr, msg
		if keep:
			ddl = definition.createddl(cursor, term)
			if ddl:
				if options.execute:
					try:
						cursor2.execute(ddl)
					except orasql.DatabaseError, exc:
						if not options.ignore or "ORA-01013" in str(exc):
							raise
						msg = "oracreate.py: %s: %s" % (exc.__class__, str(exc).strip())
						if options.colorstderr:
							msg = ansistyle.Text(color4error, msg)
						print >>sys.stderr, msg
				else:
					print ddl
					print
