#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Setup script for ll-orasql


try:
	import setuptools as tools
except ImportError:
	from distutils import core as tools

import textwrap, re


DESCRIPTION = """
ll-orasql contains utilities for working with :mod:`cx_Oracle`: It allows
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


try:
	news = list(open("NEWS.rst", "r"))
except IOError:
	description = DESCRIPTION.strip()
else:
	# Extract the first section (which are the changes for the current version)
	underlines = [i for (i, line) in enumerate(news) if line.startswith("---")]
	news = news[underlines[0]-1:underlines[1]-1]
	news = "".join(news)
	descr = "%s\n\n\n%s" % (DESCRIPTION.strip(), news)

	# Get rid of text roles PyPI doesn't know about
	descr = re.subn(":[a-z]+:`([a-zA-Z0-9_.]+)`", "``\\1``", descr)[0]


args=dict(
	name="ll-orasql",
	version="1.27.1",
	description="Utilities for working with cx_Oracle",
	long_description=descr,
	author=u"Walter Doerwald",
	author_email="walter@livinglogic.de",
	url="http://www.livinglogic.de/Python/orasql/",
	download_url="http://www.livinglogic.de/Python/Download.html#orasql",
	license="Python",
	classifiers=CLASSIFIERS.strip().splitlines(),
	keywords=",".join(KEYWORDS.strip().splitlines()),
	packages=["ll", "ll.orasql", "ll.orasql.scripts"],
	package_dir={"": "src"},
	entry_points=dict(
		console_scripts=[
			"oracreate = ll.orasql.scripts.oracreate:main",
			"oradrop = ll.orasql.scripts.oradrop:main",
			"oradelete = ll.orasql.scripts.oradelete:main",
			"oradiff = ll.orasql.scripts.oradiff:main",
			"oramerge = ll.orasql.scripts.oramerge:main",
			"oragrant = ll.orasql.scripts.oragrant:main",
			"orafind = ll.orasql.scripts.orafind:main",
		]
	),
	scripts=[
		"scripts/oracreate.py",
		"scripts/oradrop.py",
		"scripts/oradelete.py",
		"scripts/oradiff.py",
		"scripts/oramerge.py",
		"scripts/oragrant.py",
		"scripts/orafind.py",
	],
	install_requires=[
		"ll-xist >= 3.6.4",
		"cx_Oracle >= 5.0.1",
	],
	namespace_packages=["ll"],
	zip_safe=False,
	dependency_links=[
		"http://sourceforge.net/project/showfiles.php?group_id=84168", # cx_Oracle
	]
)


if __name__ == "__main__":
	tools.setup(**args)
