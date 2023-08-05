#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

# Setup script for ll-orasql


__version__ = "$Revision: 1.39 $"[11:-2]
# $Source: /data/cvsroot/LivingLogic/Python/orasql/setup.py,v $


try:
	import setuptools as tools
except ImportError:
	from distutils import core as tools

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


args=dict(
	name="ll-orasql",
	version="1.12.1",
	description="Utilities for working with cx_Oracle",
	long_description=DESCRIPTION,
	author=u"Walter Doerwald",
	author_email="walter@livinglogic.de",
	url="http://www.livinglogic.de/Python/orasql/",
	download_url="http://www.livinglogic.de/Python/orasql/Download.html",
	license="Python",
	classifiers=CLASSIFIERS.strip().splitlines(),
	keywords=",".join(KEYWORDS.strip().splitlines()),
	packages=["ll", "ll.orasql", "ll.orasql.scripts"],
	package_dir={"": "src"},
	entry_points=dict(
		console_scripts=[
			"oracreate = ll.orasql.scripts.oracreate:main",
			"oradrop = ll.orasql.scripts.oradrop:main",
			"oradiff = ll.orasql.scripts.oradiff:main",
			"oramerge = ll.orasql.scripts.oramerge:main",
		]
	),
	scripts=[
		"scripts/oracreate.py",
		"scripts/oradrop.py",
		"scripts/oradiff.py",
		"scripts/oramerge.py",
	],
	install_requires=[
		"ll-core >= 1.4",
		"cx_Oracle >= 4.1.2",
	],
	namespace_packages=["ll"],
	zip_safe=False,
	dependency_links=[
		"http://starship.python.net/crew/atuining/cx_Oracle/index.html", # cx_Oracle
	]
)


if __name__ == "__main__":
	tools.setup(**args)
