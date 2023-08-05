#! /usr/bin/env/python
# -*- coding: iso-8859-1 -*-

## Copyright 2007 by LivingLogic AG, Bayreuth/Germany.
## Copyright 2007 by Walter Dörwald
##
## All Rights Reserved
##
## See toxic.py for the license


import re

from ll import toxic
from ll.xist import xsc


def test_basics():
	e = toxic.code("foo;")
	s = toxic.xml2ora(e.asString())
	assert "return c_out" in s


def test_proc():
	s = toxic.xml2ora(u"")
	assert "return c_out" in s

	e = toxic.proc()
	s = toxic.xml2ora(e.asString())
	assert "return c_out" not in s


def test_type():
	e = toxic.type("varchar2")
	s = toxic.xml2ora(e.asString())
	assert "return varchar2" in s


def test_args():
	e = toxic.args("p_foo integer")
	s = toxic.xml2ora(e.asString())
	assert re.search(r"(\s*p_foo integer\s*)", s)


def test_vars():
	e = e = xsc.Frag(
		toxic.type("varchar2"),
		toxic.vars("v_foo integer;")
	)
	s = toxic.xml2ora(e.asString())
	assert re.search(r"as\s*c_out varchar2;\s*v_foo integer;\s*begin", s)
