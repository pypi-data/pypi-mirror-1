#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-

## Copyright 2004-2007 by LivingLogic AG, Bayreuth/Germany.
## Copyright 2004-2007 by Walter Dörwald
##
## All Rights Reserved
##
## Permission to use, copy, modify, and distribute this software and its documentation
## for any purpose and without fee is hereby granted, provided that the above copyright
## notice appears in all copies and that both that copyright notice and this permission
## notice appear in supporting documentation, and that the name of LivingLogic AG or
## the author not be used in advertising or publicity pertaining to distribution of the
## software without specific, written prior permission.
##
## LIVINGLOGIC AG AND THE AUTHOR DISCLAIM ALL WARRANTIES WITH REGARD TO THIS SOFTWARE,
## INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS, IN NO EVENT SHALL
## LIVINGLOGIC AG OR THE AUTHOR BE LIABLE FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL
## DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER
## IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR
## IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.


'''
<par>This module is an &xist; namespace. It can be used for
generating Oracle database functions that return &xml; strings.
This is done by embedding processing instructions containing
PL/SQL code into &xml; files and transforming those files with &xist;.</par>

<par>An example that generates an &html; table containing the result
of a search for names in a <lit>person</lit> table might look
like this:</par>

<example>
<prog>
from ll.xist import xsc
from ll.xist.ns import html, htmlspecials
from ll import toxic

class search(xsc.Element):
	def convert(self, converter):
		e = xsc.Frag(
			toxic.args("search varchar2"),
			toxic.vars("i integer;"),
			toxic.type("varchar2(32000);"),
			htmlspecials.plaintable(
				toxic.code("""
					i := 1;
					for row in (select name from person where name like search) loop
						"""),
						html.tr(
							html.th(toxic.expr("i"), align="right"),
							html.td(toxic.expr("xmlescape(row.name)"))
						),
						toxic.code("""
						i := i+1;
					end loop;
				""")
			)
		)
		return e.convert(converter)

print toxic.xml2ora(search().conv().asString(encoding"us-ascii")).encode("us-ascii")
</prog>
</example>

<par>Running this script will give the following output
(the indentation will be different though):</par>

<prog>
(
	search varchar2
)
return varchar2
as
	c_out varchar2(32000);
	i integer;
begin
	c_out := c_out || '&lt;table cellpadding="0" border="0" cellspacing="0"&gt;';
	i := 1;
	for row in (select name from person where name like search) loop
		c_out := c_out || '&lt;tr&gt;&lt;th align="right"&gt;';
		c_out := c_out || i;
		c_out := c_out || '&lt;/th&gt;&lt;td&gt;';
		c_out := c_out || xmlescape(row.name);
		c_out := c_out || '&lt;/td&gt;&lt;/tr&gt;';
		i := i+1;
	end loop;
	c_out := c_out || '&lt;/table&gt;';
	return c_out;
end;
</prog>

<par>Instead of generating the &xml; from a single &xist; element,
it's of course also possible to use an &xml; file. One that generates
the same function as the one above looks like this:</par>

<example>
<prog>
&lt;?args
	search varchar2
?&gt;
&lt;?vars
	i integer;
?&gt;
&lt;plaintable class="search"&gt;
	&lt;?code
		i := 1;
		for row in (select name from person where name like search) loop
			?&gt;
			&lt;tr&gt;
				&lt;th align="right"&gt;&lt;?expr i?&gt;&lt;/th&gt;
				&lt;td&gt;&lt;?expr xmlescape(row.name)?&gt;&lt;/td&gt;
			&lt;/tr&gt;
			&lt;?code
			i := i + 1;
		end loop;
	?&gt;
&lt;/plaintable&gt;
</prog>
</example>

<par>When we save the file above as <filename>search.sqlxsc</filename> then
parsing the file, transforming it and printing the function body
works like this:</par>

<example>
<prog>
from ll.xist import parsers
from ll.xist.ns import html, htmlspecials
from ll import toxic

node = parsers.parseFile("search.sqlxsc")
node = node.conv()
print toxic.xml2ora(node.asString(encoding="us-ascii")).encode("us-ascii")
</prog>
</example>
'''


__version__ = tuple(map(int, "$Revision: 1.3 $"[11:-2].split(".")))
# $Source: /data/cvsroot/LivingLogic/Python/toxic/src/ll/toxic.py,v $


import cStringIO

from ll.xist import xsc, publishers


class args(xsc.ProcInst):
	"""
	<par>Specifies the arguments to be used by the generated function. For example:</par>
	<example>
	<prog>
	&lt;?args
		key in integer,
		lang in varchar2
	?&gt;
	</prog>
	</example>
	<par>If <class>args</class> is used multiple times, the contents will simple
	be concatenated.</par>
	"""


class vars(xsc.ProcInst):
	"""
	<par>Specifies the local variables to be used by the function.
	For example:</par>
	<example>
	<prog>
	&lt;?vars
		buffer varchar2(200) := 'foo';
		counter integer;
	?&gt;
	</prog>
	</example>
	<par>If <class>vars</class> is used multiple times, the contents will simple
	be concatenated.</par>
	"""


class code(xsc.ProcInst):
	"""
	<par>A PL/SQL code fragment that will be embedded literally in the
	generated function. For example:</par>
	<example>
	<prog>
	&lt;?code select user into v_user from dual;?&gt;
	</prog>
	</example>
	"""


class expr(xsc.ProcInst):
	"""
	The data of an <class>expr</class> processing instruction
	must contain a PL/SQL expression whose value will be embedded
	in the string returned by the generated function. This value will
	not be escaped in any way, so you can generate &xml; tags with
	<class>expr</class> PIs but you must make sure to generate
	the value in the encoding that the caller of the generated
	function expects.
	"""


class proc(xsc.ProcInst):
	"""
	When this processing instruction is found in the source
	<pyref function="xml2ora"><function>xml2ora</function></pyref>
	will no longer generate a function as a result, but a procedure.
	This procedure must have <lit>c_out</lit> as an <z>out</z> variable
	(of the appropriate type (see <pyref class="type"><class>type</class></pyref>)
	where the output will be written to.
	"""


class type(xsc.ProcInst):
	"""
	<par>Can be used to specify the return type of the generated
	function. The default is <lit>clob</lit>.
	"""


@classmethod
def stringify(cls, string, nchar=False):
	"""
	Format <arg>string</arg> as multiple PL/SQL string constants or expressions.
	<arg>nchar</arg> specifies if a <lit>NVARCHAR</lit> constant should be
	generated or a <lit>VARCHAR</lit>. This is a generator.
	"""
	current = []

	for c in string:
		if ord(c) < 32:
			if current:
				if nchar:
					yield u"N'%s'" % u"".join(current)
				else:
					yield u"'%s'" % u"".join(current)
				current = []
			yield u"chr(%d)" % ord(c)
		else:
			if c == u"'":
				c = u"''"
			current.append(c)
			if len(current) > 1000:
				if nchar:
					yield u"N'%s'" % u"".join(current)
				else:
					yield u"'%s'" % u"".join(current)
				current = []
	if current:
		if nchar:
			yield u"N'%s'" % u"".join(current)
		else:
			yield u"'%s'" % u"".join(current)


@classmethod
def xml2ora(cls, string):
	"""
	The <class>unicode</class> object <arg>string</arg> must be an &xml; string.
	<function>xml2ora</function> extracts the relevant processing instructions
	and creates the body of an Oracle function from it.
	"""
	foundproc = False
	foundargs = []
	foundvars = []
	foundplsql = []
	foundtype = u"clob"

	for (t, s) in cls.tokenize(string):
		if t is unicode:
			foundplsql.append((-1, s))
		elif issubclass(t, code):
			foundplsql.append((0, s))
		elif issubclass(t, expr):
			foundplsql.append((1, s))
		elif issubclass(t, args):
			foundargs.append(s)
		elif issubclass(t, vars):
			foundvars.append(s)
		elif issubclass(t, type):
			foundtype = s
		elif issubclass(t, proc):
			foundproc = True

	result = []
	if foundargs:
		result.append(u"(\n\t%s\n)\n" % u",\n\t".join(foundargs))
	plaintype = foundtype
	if u"(" in plaintype:
		plaintype = plaintype[:plaintype.find(u"(")]
	isclob = plaintype.lower() in ("clob", "nclob")
	if not foundproc:
		result.append(u"return %s\n" % plaintype)
	result.append(u"as\n")
	if not foundproc:
		result.append(u"\tc_out %s;\n" % foundtype)
	if foundvars:
		result.append(u"\t%s\n" % u"".join(foundvars))
	nchar = foundtype.lower().startswith(u"n")
	if isclob:
		for arg in (u"clob", u"varchar2"):
			result.append(u"\tprocedure write(p_text in %s%s)\n" % (plaintype.rstrip(u"clob"), arg))
			result.append(u"\tas\n")
			result.append(u"\t\tbegin\n")
			if arg == u"clob":
				result.append(u"\t\t\tif p_text is not null and length(p_text) != 0 then\n")
				result.append(u"\t\t\t\tdbms_lob.append(c_out, p_text);\n")
			else:
				result.append(u"\t\t\tif p_text is not null then\n")
				result.append(u"\t\t\t\tdbms_lob.writeappend(c_out, length(p_text), p_text);\n")
			result.append(u"\t\tend if;\n")
			result.append(u"\tend;\n")
	result.append(u"begin\n")
	if isclob:
		result.append(u"\tdbms_lob.createtemporary(c_out, true);\n")
	for (mode, string) in foundplsql:
		if mode == -1:
			for s in cls.stringify(string, nchar):
				if isclob:
					result.append(u"\twrite(%s);\n" % s)
				else:
					result.append(u"\tc_out := c_out || %s;\n" % s)
		elif mode == 0:
			result.append(string)
			result.append(u"\n")
		else: # mode == 1
			if isclob:
				result.append(u"\twrite(%s);\n" % string)
			else:
				result.append(u"\tc_out := c_out || %s;\n" % string)
	if not foundproc:
		result.append(u"\treturn c_out;\n")
	result.append(u"end;\n")
	return u"".join(result)


@classmethod
def prettify(cls, string):
	"""
	Try to fix the indentation of the PL/SQL snippet passed in.
	"""
	lines = [line.lstrip("\t") for line in string.split("\n")]
	newlines = []
	indents = {
		"(": (0, 1),
		");": (-1, 0),
		")": (-1, 0),
		"as": (0, 1),
		"begin": (0, 1),
		"loop": (0, 1),
		"end;": (-1, 0),
		"end": (-1, 0),
		"exception": (-1, 1),
		"if": (0, 1),
		"for": (0, 1),
		"while": (0, 1),
		"elsif": (-1, 1),
		"else": (-1, 1),
	}
	indent = 0
	firstafteras = False
	for line in lines:
		if not line:
			newlines.append("")
		else:
			prefix = line.split(None, 1)[0]
			(pre, post) = indents.get(prefix, (0, 0))
			if line.endswith("("):
				post = 1
			elif firstafteras and prefix == "begin":
				# as followed by begin has same indentation
				pre = -1
			indent = max(0, indent+pre)
			newlines.append("%s%s" % ("\t"*indent, line))
			indent = max(0, indent+post)
			if prefix == "as":
				firstafteras = True
	return "\n".join(newlines)


class __ns__(xsc.Namespace):
	xmlname = "toxic"
	xmlurl = "http://xmlns.livinglogic.de/toxic"
import __builtin__
__ns__.makemod(__builtin__.vars())
del __builtin__
