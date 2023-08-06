Requirements
============

To use this module you need the following software packages:

	1.	`Python 2.5`_;
	2.	`ll-xist`_ (version 3.2 or later);
	3.	`ll-orasql`_ (version 1.19 or later; which in turn requires cx_Oracle_);
	4.	`CherryPy`_

	.. _Python 2.5: http://www.python.org/
	.. _ll-xist: http://www.livinglogic.de/Python/xist
	.. _ll-orasql: http://www.livinglogic.de/Python/orasql
	.. _cx_Oracle: http://www.python.net/crew/atuining/cx_Oracle/
	.. _CherryPy: http://www.cherrypy.org


Installation
============

setuptools__ is used for installation so you can install this module with the
following command::

	$ easy_install ll-nightshade

__ http://peak.telecommunity.com/DevCenter/setuptools

If you want to install from source, you can download one of the
`distribution archives`__, unpack it, enter the directory and execute the
following command::

	$ python setup.py install

__ http://www.livinglogic.de/Python/Download.html#nightshade

This will install :mod:`ll.nightshade` as part of the :mod:`ll` package.

For Windows a binary distribution is provided. To install it, double click it,
and follow the instructions.

If you have difficulties installing this software, send a problem report
to Walter Dörwald (walter@livinglogic.de).
