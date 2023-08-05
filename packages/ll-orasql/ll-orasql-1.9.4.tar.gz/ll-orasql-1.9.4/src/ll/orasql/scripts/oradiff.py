#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

## Copyright 2005/2006 by LivingLogic AG, Bayreuth/Germany.
## Copyright 2005/2006 by Walter Dörwald
##
## All Rights Reserved
##
## See orasql/__init__.py for the license


import sys, os, difflib, optparse

from ll import orasql, astyle


s4comment = astyle.Style.fromenv("LL_ORASQL_REPRANSI_COMMENT", "black:black:bold")
s4addedfile = astyle.Style.fromenv("LL_ORASQL_REPRANSI_ADDEDFILE", "black:green")
s4addedline = astyle.Style.fromenv("LL_ORASQL_REPRANSI_ADDEDLINE", "green:black")
s4removedfile = astyle.Style.fromenv("LL_ORASQL_REPRANSI_REMOVEDFILE", "black:red")
s4removedline = astyle.Style.fromenv("LL_ORASQL_REPRANSI_REMOVEDLINE", "red:black")
s4changedfile = astyle.Style.fromenv("LL_ORASQL_REPRANSI_CHANGEDFILE", "black:blue")
s4changedline = astyle.Style.fromenv("LL_ORASQL_REPRANSI_CHANGEDLINE", "blue:black")
s4pos = astyle.Style.fromenv("LL_ORASQL_REPRANSI_POS", "black:black:bold")
s4connectstring = astyle.Style.fromenv("LL_ORASQL_REPRANSI_CONNECTSTRING", "yellow:black")
s4definition = astyle.Style.fromenv("LL_ORASQL_REPRANSI_DEFINITION", "green:black")


def cs(connection):
	return s4connectstring(connection.connectstring())


def df(definition):
	return s4definition(repr(definition))


def comment(msg, color):
	return s4comment("-- ", msg)


def gettimestamp(definition, connection, format):
	try:
		timestamp = definition.udate(connection)
	except orasql.SQLObjectNotFoundError:
		return "doesn't exist"
	if timestamp is not None:
		timestamp = timestamp.strftime(format)
	else:
		timestamp = "without timestamp"
	return timestamp


def getcanonicalddl(ddl, blank):
	return [Line(line, blank) for line in ddl.splitlines()]


class Line(object):
	__slots__ = ("originalline", "compareline")

	def __init__(self, line, blank):
		self.originalline = line
		if blank == "literal":
			self.compareline = line
		elif blank == "trail":
			self.compareline = line.rstrip()
		elif blank == "lead":
			self.compareline = line.lstrip()
		elif blank == "both":
			self.compareline = line.strip()
		elif blank == "collapse":
			self.compareline = " ".join(line.strip().split())
		else:
			raise ValueError("unknown blank value %r" % blank)

	def __eq__(self, other):
		return self.compareline == other.compareline

	def __ne__(self, other):
		return self.compareline != other.compareline

	def __hash__(self):
		return hash(self.compareline)


def showudiff(out, definition, ddl1, ddl2, connection1, connection2, context=3, timeformat="%c"):
	def header(prefix, style, connection):
		return style("%s %r in %s: %s" % (prefix, definition, connection.connectstring(), gettimestamp(definition, connection, timeformat)))

	started = False
	for group in difflib.SequenceMatcher(None, ddl1, ddl2).get_grouped_opcodes(context):
		if not started:
			out.writeln(header("---", s4removedfile, cursor1))
			out.writeln(header("+++", s4addedfile, cursor2))
			started = True
		(i1, i2, j1, j2) = group[0][1], group[-1][2], group[0][3], group[-1][4]
		out.writeln(s4pos("@@ -%d,%d +%d,%d @@" % (i1+1, i2-i1, j1+1, j2-j1)))
		for (tag, i1, i2, j1, j2) in group:
			if tag == "equal":
				for line in ddl1[i1:i2]:
					out.writeln(" %s" % line.originalline)
				continue
			if tag == "replace" or tag == "delete":
				for line in ddl1[i1:i2]:
					out.writeln(s4removedline("-", line.originalline))
			if tag == "replace" or tag == "insert":
				for line in ddl2[j1:j2]:
					out.writeln(s4addedline("+", line.originalline))


def main():
	colors = ("yes", "no", "auto")
	modes = ("brief", "udiff", "full")
	blanks = ("literal", "trail", "lead", "both", "collapse")
	p = optparse.OptionParser(usage="usage: %prog [options] connectstring1 connectstring2")
	p.add_option("-v", "--verbose", dest="verbose", help="Give a progress report?", default=False, action="store_true")
	p.add_option("-c", "--color", dest="color", help="Color output (%s)" % ", ".join(colors), default="auto", choices=colors)
	p.add_option("-m", "--mode", dest="mode", help="Output mode (%s)" % ", ".join(modes), default="udiff", choices=modes)
	p.add_option("-n", "--context", dest="context", help="Number of context lines", type="int", default=2)
	p.add_option("-k", "--keepjunk", dest="keepjunk", help="Output objects with '$'  or 'SYS_EXPORT_SCHEMA_' in their name?", default=False, action="store_true")
	p.add_option("-b", "--blank", dest="blank", help="How to treat whitespace (%s)" % ", ".join(blanks), default="literal", choices=blanks)

	(options, args) = p.parse_args()
	if len(args) != 2:
		p.error("incorrect number of arguments")
		return 1

	if options.color == "yes":
		color = True
	elif options.color == "no":
		color = False
	else:
		color = None
	stdout = astyle.Stream(sys.stdout, color)
	stderr = astyle.Stream(sys.stderr, color)

	connection1 = orasql.connect(args[0])
	connection2 = orasql.connect(args[1])

	def fetch(connection):
		objects = set()

		def keep(definition):
			if definition.owner is not None:
				return False
			if options.keepjunk:
				return True
			if "$" in definition.name or definition.name.startswith("SYS_EXPORT_SCHEMA_"):
				return False
			return True
	
		for (i, definition) in enumerate(connection.iterdefinitions(mode="flat", schema="user")):
			keepdef = keep(definition)
			if options.verbose:
				msg = astyle.style_default("oradiff.py: ", cs(connection), ": fetching #%d " % (i+1), df(definition))
				if not keepdep:
					msg += " (skipped)"
				stderr.writeln(msg)
			if keepdep:
				objects.add(definition)
		return objects

	objects1 = fetch(connection1)
	objects2 = fetch(connection2)

	onlyin1 = objects1 - objects2
	for (i, definition) in enumerate(onlyin1):
		if options.verbose:
			stderr.writeln("oradiff.py: only in ", cs(connection1), " #%d/%d " % (i+1, len(onlyin1)), df(definition))
		if options.mode == "brief":
			stdout.writeln(df(definition), ": only in ", cs(connection1))
		elif options.mode == "full":
			stdout.writeln(comment(df(definition), ": only in " % cs(connection1)))
			ddl = definition.dropddl(connection1, term=True)
			if ddl:
				stdout.write(ddl)
		elif options.mode == "udiff":
			ddl = getcanonicalddl(definition.createddl(connection1), options.blank)
			showudiff(stdout, definition, ddl, [], connection1, connection2, options.context)

	onlyin2 = objects2 - objects1
	for (i, definition) in enumerate(onlyin2):
		if options.verbose:
			stderr.writeln("oradiff.py: only in ", cs(connection2), " #%d/%d " % (i+1, len(onlyin2)), df(definition))
		if options.mode == "brief":
			stdout.writeln(df(definition), ": only in ", cs(connection2))
		elif options.mode == "full":
			stdout.writeln(comment(df(definition), ": only in ", cs(connection2)))
			ddl = definition.createddl(connection2, term=True)
			if ddl:
				stdout.write(ddl)
		elif options.mode == "udiff":
			ddl = getcanonicalddl(definition.createddl(connection2), options.blank)
			showudiff(stdout, definition, [], ddl, connection1, connection2, options.context)

	common = objects1 & objects2
	for (i, definition) in enumerate(common):
		if options.verbose:
			stderr.writeln("oradiff.py: diffing #%d/%d " % (i+1, len(common)), df(definition))
		ddl1 = definition.createddl(connection1)
		ddl2 = definition.createddl(connection2)
		ddl1c = getcanonicalddl(ddl1, options.blank)
		ddl2c = getcanonicalddl(ddl2, options.blank)
		if ddl1c != ddl2c:
			if options.mode == "brief":
				stdout.writeln(df(definition), ": different")
			elif options.mode == "full":
				stdout.writeln(comment(df(definition), ": different"))
				stdout.write(definition.createddl(connection2))
			elif options.mode == "udiff":
				showudiff(stdout, definition, ddl1c, ddl2c, connection1, connection2, options.context)


if __name__ == "__main__":
	sys.exit(main())
