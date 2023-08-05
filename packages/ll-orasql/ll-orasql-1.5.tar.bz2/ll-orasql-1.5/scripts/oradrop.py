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
	fks = ("keep", "disable", "drop")
	p = optparse.OptionParser(usage="usage: %prog [options] connectstring >output.sql")
	p.add_option("-v", "--verbose", dest="verbose", help="Give a progress report?", default=False, action="store_true")
	p.add_option("-c", "--color", dest="color", help="Color output (%s)" % ", ".join(colors), default="auto", choices=colors)
	p.add_option("-f", "--fks", dest="fks", help="How should foreign keys from other schemas be treated (%s)?" % ", ".join(fks), default="disable", choices=fks)
	p.add_option("-x", "--execute", dest="execute", action="store_true", help="immediately execute the commands instead of printing them?")
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

	term = not options.execute
	
	cs = cursor.connection.connectstring()
	if options.colorstderr:
		cs = ansistyle.Text(color4connectstring, cs)

	ddls = []
	for definition in cursor.iterobjects(mode="drop", schema="dep"):
		# Get DDL
		ddl = ""
		action = "skipped"
		if definition.owner is not None:
			if isinstance(definition, orasql.FKDefinition):
				if options.fks == "disable":
					ddl = definition.disableddl(cursor, term)
					action = "disabled"
				elif options.fks == "drop":
					ddl = definition.dropddl(cursor, term)
					action = None
		elif "$" not in definition.name or options.keepdollar:
			ddl = definition.dropddl(cursor, term)
			action = None

		# Progress report
		if options.verbose:
			msgdef = repr(definition)
			if options.colorstderr:
				msgdef = ansistyle.Text(color4definition, msgdef)
			msg = "oradrop.py: %s: fetching %s" % (cs, msgdef)
			if action is not None:
				msg += " (%s)" % action
			print >>sys.stderr, msg

		if ddl:
			# Print or execute DDL
			if options.execute:
				ddls.append((definition, ddl))
			else:
				sys.stdout.write(ddl)

	# Execute DDL
	if options.execute:
		for (definition, ddl) in ddls:
			if options.verbose:
				msgdef = repr(definition)
				if options.colorstderr:
					msgdef = ansistyle.Text(color4definition, msgdef)
				msg = "oradrop.py: %s: dropping %s" % (cs, msgdef)
				print >>sys.stderr, msg
			try:
				cursor.execute(ddl)
			except orasql.DatabaseError, exc:
				if not options.ignore or "ORA-01013" in str(exc):
					raise
				msg = "%s: %s" % (exc.__class__, str(exc).strip())
				if options.colorstderr:
					msg = ansistyle.Text(color4error, msg)
				print >>sys.stderr, msg
