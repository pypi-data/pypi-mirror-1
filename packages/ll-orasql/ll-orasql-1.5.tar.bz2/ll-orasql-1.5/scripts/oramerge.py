#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

## Copyright 2005 by LivingLogic AG, Bayreuth/Germany.
## Copyright 2005 by Walter Dörwald
##
## All Rights Reserved
##
## See orasql.py for the license


import sys, os, difflib, optparse, tempfile, subprocess

from ll import orasql, ansistyle


color4warning = 0010
color4error = 0010
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
	if color:
		msg = ansistyle.Text(color4comment, "-- ", msg)
	else:
		msg = ansistyle.Text("-- ", msg)
	return msg


def conflictmarker(prefix, text, color):
	if color:
		msg = ansistyle.Text((color4error, prefix), " ", text)
	else:
		msg = ansistyle.Text(prefix, " ", text)
	return msg


def showaction(action, definition, color):
	print comment(ansistyle.Text(action, " ", df(definition, color)), color)


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


if __name__ == "__main__":
	colors = ("yes", "no", "auto")
	blanks = ("literal", "trail", "lead", "both", "collapse")
	# Merge changes between oldsource and newsource into destination
	p = optparse.OptionParser(usage="usage: %prog [options] oldsourceconnectstring newsourceconnectstring destinationconnectstring")
	p.add_option("-v", "--verbose", dest="verbose", help="Give a progress report?", default=False, action="store_true")
	p.add_option("-c", "--color", dest="color", help="Color output (%s)" % ", ".join(colors), default="auto", choices=colors)
	p.add_option("-k", "--keepdollar", dest="keepdollar", help="Output objects with '$' in their name?", default=False, action="store_true")

	(options, args) = p.parse_args()
	if len(args) != 3:
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

	connection3 = orasql.connect(args[2])
	cursor3 = connection3.cursor()

	def fetch(cursor):
		objects = set()

		for definition in cursor.iterobjects(mode="flat", schema="own"):
			keep = "$" not in definition.name or options.keepdollar
			if options.verbose:
				msg = "oramerge.py: %s: %s" % (cs(cursor, options.colorstderr), df(definition, options.colorstderr))
				if not keep:
					msg += " (skipped)"
				print >>sys.stderr, msg
			if keep:
				objects.add(definition)
		return objects

	def write(file, data):
		try:
			file.write(data)
			file.write("\n")
		finally:
			file.close()

	objects1 = fetch(cursor1)
	objects2 = fetch(cursor2)
	objects3 = fetch(cursor3)

	retcode = 0

	allobjects = objects1 | objects2 | objects3
	for definition in allobjects:
		in1 = definition in objects1
		in2 = definition in objects2
		in3 = definition in objects3
		if in1 != in2 or in2 != in3:
			if not in1 and not in2 and in3: # added in in3 => keep it
				msg = ansistyle.Text(df(definition, options.colorstdout), ": only in ", cs(cursor3, options.colorstdout), " => keep it")
				action = None
			elif not in1 and in2 and not in3: # added in in2 => copy it to db3
				msg = ansistyle.Text(df(definition, options.colorstdout), ": added in ", cs(cursor2, options.colorstdout), " => add it to ", cs(cursor3, options.colorstdout))
				action = "create"
			elif not in1 and in2 and in3: # added in both in2 and in3 => collision?
				if definition.createddl(cursor2) != definition.createddl(cursor3):
					msg = ansistyle.Text(df(definition, options.colorstdout), ": added in ", cs(cursor2, options.colorstdout), " and ", cs(cursor3, options.colorstdout), " => ", (color4error, "conflict"))
					action = "collision"
					retcode = 2
				else:
					msg = ansistyle.Text(df(definition, options.colorstdout), ": added in ", cs(cursor2, options.colorstdout), " and ", cs(cursor3, options.colorstdout), " and identical => keep it")
					action = None
			elif in1 and not in2 and not in3: # removed in in2 and in3 => not needed
				msg = ansistyle.Text(df(definition, options.colorstdout), ": removed in ", cs(cursor2, options.colorstdout), " and ", cs(cursor3, options.colorstdout), " => not needed")
				action = None
			elif in1 and not in2 and in3: # removed in in2 => remove in db3
				msg = ansistyle.Text(df(definition, options.colorstdout), ": removed in ", cs(cursor2, options.colorstdout), " => remove in ", cs(cursor3, options.colorstdout))
				action = "drop"
			elif in1 and in2 and not in3: # removed in in3 => not needed
				msg = ansistyle.Text(df(definition, options.colorstdout), ": removed in ", cs(cursor3, options.colorstdout), " => not needed")
				action = None
		elif in1 and in2 and in3: # in all three => merge it
			ddl1 = definition.createddl(cursor1)
			ddl2 = definition.createddl(cursor2)
			ddl3 = definition.createddl(cursor3)

			if options.verbose:
				msg = "oramerge.py: diffing %s" % df(definition, options.colorstderr)
				print >>sys.stderr, msg

			if ddl1 != ddl2 or ddl2 != ddl3:
				# If it's a table, we do not output a merged "create table" statement, but the appropriate "alter table" statements
				if isinstance(definition, orasql.TableDefinition):
					fields1 = set(cursor1.itercolumns(definition))
					fields2 = set(cursor2.itercolumns(definition))
					fields3 = set(cursor3.itercolumns(definition))
					for field in fields1 | fields2 | fields3:
						if options.verbose:
							msg = "oramerge.py: diffing %s" % df(field, options.colorstderr)
							print >>sys.stderr, msg
						in1 = field in fields1
						in2 = field in fields2
						in3 = field in fields3
						if in1 != in2 or in2 != in3:
							if not in1 and not in2 and in3: # added in in3 => keep it
								pass
							elif not in1 and in2 and not in3: # added in in2 => copy it to db3
								print comment(ansistyle.Text("add ", df(field, options.colorstdout)), options.colorstdout)
								print field.addddl(cursor2)
							elif not in1 and in2 and in3: # added in both in2 and in3 => collision?
								print comment(ansistyle.Text("conflict ", df(field, options.colorstdout)), options.colorstdout)
								print conflictmarker(7*"<", ansistyle.Text("added in ", cs(cursor2, options.colorstdout), " and ", cs(cursor3, options.colorstdout), " with different content"), options.colorstdout)
							elif in1 and not in2 and not in3: # removed in in2 and in3 => not needed
								pass
							elif in1 and not in2 and in3: # removed in in2 => remove in db3
								print comment(ansistyle.Text("drop ", df(field, options.colorstdout)), options.colorstdout)
								print field.dropddl(cursor3)
							elif in1 and in2 and not in3: # removed in in3 => not needed
								pass
						elif in1 and in2 and in3: # in all three => modify field
							ddl1 = field.addddl(cursor1)
							ddl2 = field.addddl(cursor2)
							ddl3 = field.addddl(cursor3)
							if ddl1 != ddl2 or ddl2 != ddl3:
								try:
									ddl = field.modifyddl(cursor3, cursor1, cursor2) # add changes from db1 to db2
								except orasql.ConflictError, exc:
									print comment(ansistyle.Text("conflict ", df(field, options.colorstdout)), options.colorstdout)
									print conflictmarker(7*"<", str(exc))
								else:
									print comment(ansistyle.Text("merge ", df(field, options.colorstdout)), options.colorstdout)
									print ddl
				else:
					msg = ansistyle.Text(df(definition, options.colorstdout), ": merge them")
					action = "merge"
			else:
				msg = ansistyle.Text(df(definition, options.colorstdout), ": identical")
				action = None

		if action is not None:
			if action == "collision":
				showaction(action, definition, options.colorstdout)
				print conflictmarker(7*"<", ansistyle.Text("added in ", cs(cursor2, options.colorstdout), " and ", cs(cursor3, options.colorstdout), " with different content"), options.colorstdout)
			elif action == "create":
				showaction(action, definition, options.colorstdout)
				print definition.createddl(cursor2, term=True)
			elif action == "drop":
				showaction(action, definition, options.colorstdout)
				print definition.dropddl(cursor3, term=True)
			elif action == "merge":
				filename1 = tempfile.mktemp(suffix=".sql", prefix="oramerge_1_")
				filename2 = tempfile.mktemp(suffix=".sql", prefix="oramerge_2_")
				filename3 = tempfile.mktemp(suffix=".sql", prefix="oramerge_3_")

				lines = []
				file1 = open(filename1, "wb")
				try:
					write(file1, ddl1)

					file2 = open(filename2, "wb")
					try:
						write(file2, ddl2)

						file3 = open(filename3, "wb")
						try:
							write(file3, ddl3)

							# do the diffing
							proc = subprocess.Popen(["diff3", "-m", filename3, filename1, filename2], stdout=subprocess.PIPE)
							diffretcode = proc.wait()
							if diffretcode == 0: # no conflict
								# Check if anything has changed
								finalddl = proc.stdout.read()
								# diff3 seems to append a "\n"
								if finalddl != ddl3 and (not finalddl.endswith("\n") or finalddl[:-1] != ddl3):
									showaction("merge", definition, options.colorstdout)
									sys.stdout.write(finalddl)
							elif diffretcode == 1: # conflict
								showaction("conflict", definition, options.colorstdout)
								retcode = 2
								for line in proc.stdout:
									line = line.rstrip("\n")
									if line.startswith(7*"<") or line.startswith(7*"|") or line.startswith(7*"=") or line.startswith(7*">"):
										(prefix, line) = (line[:7], line[7:])
										line = line.strip()
										if line == filename1:
											line = conflictmarker(prefix, cs(cursor1, options.colorstdout), options.colorstdout)
										elif line == filename2:
											line = conflictmarker(prefix, cs(cursor2, options.colorstdout), options.colorstdout)
										elif line == filename3:
											line = conflictmarker(prefix, cs(cursor3, options.colorstdout), options.colorstdout)
										else:
											line = conflictmarker(prefix, line, options.colorstdout)
									print line
							else:
								raise OSError("Trouble from diff3: %d" % diffretcode)
						finally:
							os.remove(filename3)
					finally:
						os.remove(filename2)
				finally:
					os.remove(filename1)
	sys.exit(retcode)
