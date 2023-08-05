#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

## Copyright 2005 by LivingLogic AG, Bayreuth/Germany.
## Copyright 2005 by Walter Dörwald
##
## All Rights Reserved
##
## See orasql.py for the license


import sys, os, difflib, optparse

from ll import orasql, ansistyle


color4comment = 0100
color4addedfile = 0002
color4addedline = 0020
color4removedfile = 0001
color4removedline = 0010
color4changedfile = 0004
color4changedline = 0040
color4pos = 0100
color4connectstring = 0040
color4definition = 0020


def cs(cursor, color):
	connectstring = cursor.connection.connectstring()
	if color:
		connectstring = ansistyle.Text(color4connectstring, connectstring)
	return connectstring


def df(definition, color):
	msg = repr(definition)
	if color:
		msg = ansistyle.Text(color4definition, msg)
	return msg


def comment(msg, color):
	msg = "-- %s" % msg
	if color:
		msg = ansistyle.Text(color4comment, msg)
	return msg


def gettimestamp(definition, cursor, format):
	try:
		timestamp = definition.udate(cursor)
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


def showudiff(definition, ddl1, ddl2, cursor1, cursor2, docolor, context=3, timeformat="%c"):
	def header(prefix, color, cursor):
		line = "%s %r in %s: %s" % (prefix, definition, cursor.connection.connectstring(), gettimestamp(definition, cursor, timeformat))
		if docolor:
			line = ansistyle.Text(color, line)
		return line

	started = False
	for group in difflib.SequenceMatcher(None, ddl1, ddl2).get_grouped_opcodes(context):
		if not started:
			print header("---", color4removedfile, cursor1)
			print header("+++", color4addedfile, cursor2)
			started = True
		(i1, i2, j1, j2) = group[0][1], group[-1][2], group[0][3], group[-1][4]
		line = "@@ -%d,%d +%d,%d @@" % (i1+1, i2-i1, j1+1, j2-j1)
		if docolor:
			line = ansistyle.Text(color4pos, line)
		print line
		for (tag, i1, i2, j1, j2) in group:
			if tag == "equal":
				for line in ddl1[i1:i2]:
					print " %s" % line.originalline
				continue
			if tag == "replace" or tag == "delete":
				for line in ddl1[i1:i2]:
					line = "-%s" % line.originalline
					if docolor:
						line = ansistyle.Text(color4removedline, line)
					print line
			if tag == "replace" or tag == "insert":
				for line in ddl2[j1:j2]:
					line = "+%s" % line.originalline
					if docolor:
						line = ansistyle.Text(color4addedline, line)
					print line


if __name__ == "__main__":
	colors = ("yes", "no", "auto")
	modes = ("brief", "udiff", "full")
	blanks = ("literal", "trail", "lead", "both", "collapse")
	p = optparse.OptionParser(usage="usage: %prog [options] connectstring1 connectstring2")
	p.add_option("-v", "--verbose", dest="verbose", help="Give a progress report?", default=False, action="store_true")
	p.add_option("-c", "--color", dest="color", help="Color output (%s)" % ", ".join(colors), default="auto", choices=colors)
	p.add_option("-m", "--mode", dest="mode", help="Output mode (%s)" % ", ".join(modes), default="udiff", choices=modes)
	p.add_option("-n", "--context", dest="context", help="Number of context lines", type="int", default=2)
	p.add_option("-k", "--keepdollar", dest="keepdollar", help="Output objects with '$' in their name?", default=False, action="store_true")
	p.add_option("-b", "--blank", dest="blank", help="How to treat whitespace (%s)" % ", ".join(blanks), default="literal", choices=blanks)

	(options, args) = p.parse_args()
	if len(args) != 2:
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

	connection1 = orasql.connect(args[0])
	cursor1 = connection1.cursor()

	connection2 = orasql.connect(args[1])
	cursor2 = connection2.cursor()

	def fetch(cursor):
		objects = set()

		for definition in cursor.iterobjects(mode="flat", schema="own"):
			keep = "$" not in definition.name or options.keepdollar
			if options.verbose:
				msg = "%s: %s: %s" % (sys.argv[0], cs(cursor, options.colorstderr), df(definition, options.colorstdout))
				if not keep:
					msg += " (skipped)"
				print >>sys.stderr, msg
			if keep:
				objects.add(definition)
		return objects

	objects1 = fetch(cursor1)
	objects2 = fetch(cursor2)

	for definition in objects1 - objects2:
		if options.mode == "brief":
			print "%s: only in %s" % (df(definition, options.colorstdout), cs(cursor1, options.colorstdout))
		elif options.mode == "full":
			print comment("%s: only in %s" % (df(definition, options.colorstdout), cs(cursor1, options.colorstdout)), options.colorstdout)
			ddl = definition.dropddl(cursor1, term=True)
			if ddl:
				sys.stdout.write(ddl)
		elif options.mode == "udiff":
			ddl = getcanonicalddl(definition.createddl(cursor1), options.blank)
			showudiff(definition, ddl, [], cursor1, cursor2, options.colorstdout, options.context)

	for definition in objects2 - objects1:
		if options.mode == "brief":
			print "%s: only in %s" % (df(definition, options.colorstdout), cs(cursor2, options.colorstdout))
		elif options.mode == "full":
			print comment("%s: only in %s" % (df(definition, options.colorstdout), cs(cursor2, options.colorstdout)), options.colorstdout)
			ddl = definition.createddl(cursor2, term=True)
			if ddl:
				sys.stdout.write(ddl)
		elif options.mode == "udiff":
			ddl = getcanonicalddl(definition.createddl(cursor2), options.blank)
			showudiff(definition, [], ddl, cursor1, cursor2, options.colorstdout, options.context)

	for definition in objects1 & objects2:
		ddl1 = definition.createddl(cursor1)
		ddl2 = definition.createddl(cursor2)
		ddl1c = getcanonicalddl(ddl1, options.blank)
		ddl2c = getcanonicalddl(ddl2, options.blank)
		if ddl1c != ddl2c:
			if options.mode == "brief":
				print "%s: different" % df(definition, options.colorstdout)
			elif options.mode == "full":
				print comment("%s: different" % df(definition, options.colorstdout), options.colorstdout)
				print definition.createddl(cursor2)
			elif options.mode == "udiff":
				showudiff(definition, ddl1c, ddl2c, cursor1, cursor2, options.colorstdout, options.context)
