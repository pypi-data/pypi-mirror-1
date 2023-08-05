History
=======


Changes in 0.10 (released 01/07/2008)
-------------------------------------

*	Adapted to XIST 3.0.


Changes in 0.9.1 (released 01/24/2007)
--------------------------------------

*	Fixed a bug related to empty ``CLOB``s.


Changes in 0.9 (released 06/29/2006)
------------------------------------

*	:mod:`setuptools` is supported for installation now.


Changes in 0.8 (released 04/18/2006)
------------------------------------

*	The class :class:`Publisher` has been removed.

*	When the new processing instruction :class:`proc` appears in the source,
	:func:`xml2ora` will generate a procedure instead of a function. This
	procedure must have ``c_out`` as an appropriate out variable.


Changes in 0.7.1 (released 11/11/2005)
--------------------------------------

*	The :func:`write` generated for appending :class:`CLOB`s to ``c_out`` uses
	:func:`DBMS_LOB.APPEND` now instead of :func:`DBMS_LOB.WRITEAPPEND`.


Changes in 0.7 (released 10/31/2005)
------------------------------------

*	:meth:`xml2ora` operates on unicode strings now and will no longer escape
	byte values above 127 as ``char(<rep>c</rep>)``. The :var:`encoding`
	argument is gone now.


Changes in 0.6.3 (released 06/21/2005)
--------------------------------------

*	Rewrote string output: Each string fragment will now be shipped with a
	separate call to the :func:`write` procedure. This fixes several bugs with
	long strings.


Changes in 0.6.2 (released 06/10/2005)
--------------------------------------

*	If the return value of the generated function is ``NCLOB`` or ``NVARCHAR2``,
	all generated string constants will have an ``N`` prefix now.


Changes in 0.6.1 (released 03/22/2005)
--------------------------------------

*	Added a note about the package init file to the installation documentation.


Changes in 0.6 (released 01/03/2005)
------------------------------------

*	:mod:`toxic` now requires the core module and Python 2.4.


Changes in 0.5.1 (released 11/23/2004)
--------------------------------------

*	The local clob writing procedures are now defined after the local variables.


Changes in 0.5 (released 11/11/2004)
------------------------------------

*	When the return type is a CLOB, then writing to the CLOB is done via local
	procedures in the generated function, that use the ``DBMS_LOB`` package for
	writing to the CLOB. This speeds up the functions tremendously (a factor of
	100 is possible).


Changes in 0.4 (released 10/27/2004)
------------------------------------

*	It's now possible to specify the return type of the generated function (via
	the processing instruction :class:`type`).

*	:mod:`ll.toxic` is compatible to XIST 2.6 now.


Changes in 0.3 (released 07/06/2004)
------------------------------------

*	A new function :func:`prettify` is included that tries to fix the indentation
	of a PL/SQL snippet.

*	:class:`OraclePublisher` has been renamed to :class:`Publisher`.


Changes in 0.2 (released 07/01/2004)
------------------------------------

*	A bug in :meth:`tokenize` that surfaced when the PI didn't have data, has
	been fixed.

*	:class:`OraclePublisher` now no longer creates the function directly. Instead
	it's just a normal publisher that transforms the XML into PL/SQL after the
	usual publishing step.


Changes in 0.1.2 (released 05/26/2004)
--------------------------------------

*	Optimized the :func:`stringify` function. It will no longer generate empty
	string constants now.


Changes in 0.1.1 (released 05/19/2004)
--------------------------------------

*	Added XIST to the list of required software.


Changes in 0.1 (released 05/18/2004)
------------------------------------

*	Initial release.
