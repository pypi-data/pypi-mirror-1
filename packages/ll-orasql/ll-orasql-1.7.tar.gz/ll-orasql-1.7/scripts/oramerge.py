#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

## Copyright 2005 by LivingLogic AG, Bayreuth/Germany.
## Copyright 2005 by Walter Dörwald
##
## All Rights Reserved
##
## See orasql.py for the license


import sys, os, difflib, optparse, tempfile, subprocess

from ll import orasql, astyle


s4warning = astyle.Style.fromenv("LL_ORASQL_REPRANSI_WARNING", "red:black")
s4error = astyle.Style.fromenv("LL_ORASQL_REPRANSI_ERROR", "red:black")
s4comment = astyle.Style.fromenv("LL_ORASQL_REPRANSI_COMMENT", "black:black:bold")
s4addedfile = astyle.Style.fromenv("LL_ORASQL_REPRANSI_ADDEDFILE", "black:green")
s4addedline = astyle.Style.fromenv("LL_ORASQL_REPRANSI_ADDEDLINE", "green:black")
s4removedfile = astyle.Style.fromenv("LL_ORASQL_REPRANSI_REMOVEDFILE", "black:red")
s4removedline = astyle.Style.fromenv("LL_ORASQL_REPRANSI_REMOVEDLINE", "red:black")
s4changedfile = astyle.Style.fromenv("LL_ORASQL_REPRANSI_CHANGEDFILE", "black:blue")
s4changedline = astyle.Style.fromenv("LL_ORASQL_REPRANSI_CHANGEDLINE", "blue:black")
s4pos = astyle.Style.fromenv("LL_ORASQL_REPRANSI_POS", "black:black:bold")
s4connectstring = astyle.Style.fromenv("LL_ORASQL_REPRANSI_CONNECTSTRING", "green:black")
s4definition = astyle.Style.fromenv("LL_ORASQL_REPRANSI_DEFINITION", "blue:black")



def cs(cursor):
	return s4connectstring(cursor.connection.connectstring())


def df(definition):
	return s4definition(repr(definition))


def comment(*msg):
	return s4comment("-- ", *msg)


def conflictmarker(prefix, *text):
	return astyle.style_default(s4error(prefix), " ", *text)


def showaction(out, action, definition):
	out.writeln(comment(action, " ", df(definition)))


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
		color = True
	elif options.color == "no":
		color = False
	else:
		color = None
	stdout = astyle.Stream(sys.stdout, color)
	stderr = astyle.Stream(sys.stderr, color)

	connection1 = orasql.connect(args[0])
	cursor1 = connection1.cursor()

	connection2 = orasql.connect(args[1])
	cursor2 = connection2.cursor()

	connection3 = orasql.connect(args[2])
	cursor3 = connection3.cursor()

	def fetch(cursor):
		objects = set()

		for (i, definition) in enumerate(cursor.connection.iterobjects(mode="flat", schema="own")):
			keep = "$" not in definition.name or options.keepdollar
			if options.verbose:
				msg = astyle.style_default("oramerge.py: ", cs(cursor), " fetching #%d " % (i+1), df(definition))
				if not keep:
					msg += " (skipped)"
				stderr.writeln(msg)
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
	for (i, definition) in enumerate(allobjects):
		in1 = definition in objects1
		in2 = definition in objects2
		in3 = definition in objects3
		if in1 != in2: # ignore changes from in2 to in3, because only if something changed in the sources we have to do something
			if not in1 and in2 and not in3: # added in in2 => copy it to db3
				msg = astyle.style_default(df(definition), ": added in ", cs(cursor2), " => add it to ", cs(cursor3))
				action = "create"
			elif not in1 and in2 and in3: # added in both in2 and in3 => collision?
				if definition.createddl(cursor2) != definition.createddl(cursor3):
					msg = astyle.style_default(df(definition), ": added in ", cs(cursor2), " and ", cs(cursor3), " => ", s4error("conflict"))
					action = "collision"
					retcode = 2
				else:
					msg = astyle.style_default(df(definition), ": added in ", cs(cursor2), " and ", cs(cursor3), " and identical => keep it")
					action = None
			elif in1 and not in2 and not in3: # removed in in2 and in3 => not needed
				msg = astyle.style_default(df(definition), ": removed in ", cs(cursor2), " and ", cs(cursor3), " => not needed")
				action = None
			elif in1 and not in2 and in3: # removed in in2 => remove in db3
				msg = astyle.style_default(df(definition), ": removed in ", cs(cursor2), " => remove in ", cs(cursor3))
				action = "drop"
			else:
				raise ValueError("the boolean world is about to end")
		elif in1 and in2 and in3: # in all three => merge it
			ddl1 = definition.createddl(cursor1)
			ddl2 = definition.createddl(cursor2)
			ddl3 = definition.createddl(cursor3)

			if options.verbose:
				stderr.writeln("oramerge.py: diffing #%d/%d " % (i+1, len(allobjects)), df(definition))

			if ddl1 != ddl2: # ignore changes between ddl2 and ddl3 here too
				# If it's a table, we do not output a merged "create table" statement, but the appropriate "alter table" statements
				if isinstance(definition, orasql.TableDefinition):
					fields1 = set(definition.itercolumns(cursor1))
					fields2 = set(definition.itercolumns(cursor2))
					fields3 = set(definition.itercolumns(cursor3))
					for field in fields1 | fields2 | fields3:
						if options.verbose:
							stderr.writeln("oramerge.py: diffing ", df(field))
						in1 = field in fields1
						in2 = field in fields2
						in3 = field in fields3
						if in1 != in2: # ignore changes between in2 and in3 here too
							if not in1 and in2 and not in3: # added in in2 => copy it to db3
								stdout.writeln(comment("add ", df(field)))
								stdout.writeln(field.addddl(cursor2))
							elif not in1 and in2 and in3: # added in both in2 and in3 => collision?
								stdout.writeln(comment("conflict ", df(field)))
								stdout.writeln(conflictmarker(7*"<", "added in ", cs(cursor2), " and ", cs(cursor3), " with different content"))
							elif in1 and not in2 and not in3: # removed in in2 and in3 => not needed
								pass
							elif in1 and not in2 and in3: # removed in in2 => remove in db3
								stdout.writeln(comment("drop ", df(field)))
								stdout.writeln(field.dropddl(cursor3))
						elif in1 and in2 and in3: # in all three => modify field
							ddl1 = field.addddl(cursor1)
							ddl2 = field.addddl(cursor2)
							ddl3 = field.addddl(cursor3)
							if ddl1 != ddl2 or ddl2 != ddl3:
								try:
									ddl = field.modifyddl(cursor3, cursor1, cursor2) # add changes from db1 to db2
								except orasql.ConflictError, exc:
									stdout.writeln(comment("conflict ", df(field)))
									stdout.writeln(conflictmarker(7*"<", str(exc)))
								else:
									stdout.writeln(comment("merge ", df(field)))
									stdout.writeln(ddl)
				else:
					msg = astyle.style_default(df(definition), ": merge them")
					action = "merge"
			else:
				msg = astyle.style_default(df(definition), ": identical")
				action = None

		if action is not None:
			if action == "collision":
				showaction(stdout, action, definition)
				stdout.writeln(conflictmarker(7*"<", "added in ", cs(cursor2), " and ", cs(cursor3), " with different content"))
			elif action == "create":
				showaction(stdout, action, definition)
				stdout.writeln(definition.createddl(cursor2, term=True))
			elif action == "drop":
				showaction(stdout, action, definition)
				stdout.writeln(definition.dropddl(cursor3, term=True))
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
									showaction(stdout, "merge", definition)
									stdout.write(finalddl)
							elif diffretcode == 1: # conflict
								showaction(stdout, "conflict", definition)
								retcode = 2
								for line in proc.stdout:
									line = line.rstrip("\n")
									if line.startswith(7*"<") or line.startswith(7*"|") or line.startswith(7*"=") or line.startswith(7*">"):
										(prefix, line) = (line[:7], line[7:])
										line = line.strip()
										if line == filename1:
											line = conflictmarker(prefix, cs(cursor1))
										elif line == filename2:
											line = conflictmarker(prefix, cs(cursor2))
										elif line == filename3:
											line = conflictmarker(prefix, cs(cursor3))
										else:
											line = conflictmarker(prefix, line)
									stdout.writeln(line)
							else:
								raise OSError("Trouble from diff3: %d" % diffretcode)
						finally:
							os.remove(filename3)
					finally:
						os.remove(filename2)
				finally:
					os.remove(filename1)
	sys.exit(retcode)
