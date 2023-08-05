#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

# Setup script for ll-toxic


try:
	import setuptools as tools
except ImportError:
	from distutils import core as tools

import textwrap


DESCRIPTION = """
ll-toxic is an XIST namespace that can be used for generating
Oracle database functions that return XML strings. This is done
by embedding processing instructions containing PL/SQL code
into XML files and transforming those files with XIST.
"""

CLASSIFIERS="""
Development Status :: 5 - Production/Stable
Intended Audience :: Developers
License :: OSI Approved :: Python License (CNRI Python License)
Operating System :: OS Independent
Programming Language :: Python
Topic :: Database
Topic :: Internet :: WWW/HTTP
Topic :: Software Development :: Libraries :: Python Modules
Topic :: Text Processing :: Markup :: HTML
Topic :: Text Processing :: Markup :: XML
"""

KEYWORDS = """
Oracle
user defined function
PL/SQL
XML
HTML
processing instruction
PI
embed
"""


try:
	news = list(open("NEWS.rst", "r"))
except IOError:
	description = DESCRIPTION.strip()
else:
	underlines = [i for (i, line) in enumerate(news) if line.startswith("---")]
	news = news[underlines[0]-1:underlines[1]-1]
	news = "".join(news)
	description = "%s\n\n\n%s" % (DESCRIPTION.strip(), news)


args = dict(
	name="ll-toxic",
	version="0.10",
	description="Generate Oracle functions from PL/SQL embedded in XML.",
	long_description=description,
	author=u"Walter Doerwald",
	author_email="walter@livinglogic.de",
	url="http://www.livinglogic.de/Python/toxic/",
	download_url="http://www.livinglogic.de/Python/toxic/Download.html",
	license="Python",
	classifiers=CLASSIFIERS.strip().splitlines(),
	keywords=",".join(KEYWORDS.strip().splitlines()),
	py_modules=["ll.toxic"],
	package_dir={"": "src"},
	install_requires=[
		"ll-core >= 1.10",
		"ll-xist >= 3.0",
		"cx_Oracle >= 4.3.1",
	],
	namespace_packages=["ll"],
	zip_safe=False,
	dependency_links=[
		"http://starship.python.net/crew/atuining/cx_Oracle/index.html", # cx_Oracle
	]
)


if __name__ == "__main__":
	tools.setup(**args)
