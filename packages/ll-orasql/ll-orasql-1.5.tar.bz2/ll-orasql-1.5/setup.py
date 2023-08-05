#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

# Setup script for orasql

__version__ = "$Revision: 1.22.2.1 $"[11:-2]
# $Source: /data/cvsroot/LivingLogic/Python/orasql/setup.py,v $

from distutils.core import setup
import textwrap

DESCRIPTION = """
ll-orasql contains utilities for working with ``cx_Oracle``: It allows
calling Oracle procedures via keyword arguments, it wraps the result of
fetch calls in a custom dictionary and it contains some utilitiy functions
and scripts for accessing and copying database metadata.
"""

CLASSIFIERS="""
Development Status :: 4 - Beta
Intended Audience :: Developers
License :: OSI Approved :: Python License (CNRI Python License)
Operating System :: OS Independent
Programming Language :: Python
Topic :: Database
"""

KEYWORDS = """
database
Oracle
cx_Oracle
record
procedure
schema
"""

DESCRIPTION = "\n".join(textwrap.wrap(DESCRIPTION.strip(), width=64, replace_whitespace=True))

setup(
	name="ll-orasql",
	version="1.5",
	description="Utilities for working with cx_Oracle",
	long_description=DESCRIPTION,
	author=u"Walter Dörwald".encode("utf-8"),
	author_email="walter@livinglogic.de",
	url="http://www.livinglogic.de/Python/orasql/",
	download_url="http://www.livinglogic.de/Python/orasql/Download.html",
	license="Python",
	classifiers=CLASSIFIERS.strip().splitlines(),
	keywords=",".join(KEYWORDS.strip().splitlines()),
	py_modules=["ll.orasql"],
	package_dir={"ll": ""},
	scripts=[
		"scripts/oracreate.py",
		"scripts/oradrop.py",
		"scripts/oradiff.py",
		"scripts/oramerge.py",
	]
	
)
