#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

# Setup script for TOXIC

__version__ = "$Revision: 1.11 $"[11:-2]
# $Source: /data/cvsroot/LivingLogic/Python/toxic/setup.py,v $

from distutils.core import setup
import textwrap

DESCRIPTION = """
ll-toxic is an XIST namespace that can be used for generating
Oracle database functions that return XML strings. This is done
by embedding processing instructions containing PL/SQL code
into XML files and transforming those files with XIST.
"""

CLASSIFIERS="""
Development Status :: 3 - Alpha
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

DESCRIPTION = "\n".join(textwrap.wrap(DESCRIPTION.strip(), width=64, replace_whitespace=True))

setup(
	name="ll-toxic",
	version="0.6.1",
	description="Generate Oracle functions from PL/SQL embedded in XML.",
	long_description=DESCRIPTION,
	author=u"Walter Dörwald",
	author_email="walter@livinglogic.de",
	url="http://www.livinglogic.de/Python/toxic/",
	download_url="http://www.livinglogic.de/Python/toxic/Download.html",
	license="Python",
	classifiers=CLASSIFIERS.strip().splitlines(),
	keywords=",".join(KEYWORDS.strip().splitlines()),
	py_modules=["ll.toxic"],
	package_dir={"ll": ""}
)
