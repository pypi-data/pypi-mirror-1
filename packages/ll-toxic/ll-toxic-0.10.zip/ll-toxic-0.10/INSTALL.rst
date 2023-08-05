Requirements
============

To use this module you need the following software packages:

	1.	`Python 2.5`_;
	2.	`ll-core`_ (version 1.11 or newer);
	3.	`ll-xist`_ (version 3.0 or newer);
	4.	To make use of the generated Oracle functions, you need an Oracle
		installation;
	5.	To create the Oracle functions from Python you need cx_Oracle_;
	6.	setuptools_, if you want to install this package as an egg.

	.. _Python 2.5: http://www.python.org/
	.. _ll-core: http://www.livinglogic.de/Python/core
	.. _ll-xist: http://www.livinglogic.de/Python/xist
	.. _cx_Oracle: http://www.python.net/crew/atuining/cx_Oracle/
	.. _setuptools: http://peak.telecommunity.com/DevCenter/setuptools
	

Installation
============
setuptools is used for installation so you can install this module with the
following command::

	$ easy_install ll-toxic

If you want to install from source, you can download one of the
`distribution archives`__, unpack it, enter the directory and execute the
following command::

	$ python setup.py install

__ http://www.livinglogic.de/Python/toxic/Download.html

This will install ``toxic.py`` as part of the :mod:`ll` package.

For Windows a binary distribution is provided. To install it, double click it,
and follow the instructions.

If you have difficulties installing this software, send a problem report
to Walter Dörwald (walter@livinglogic.de).
