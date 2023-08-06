Changes in 0.14 (released 01/14/2009)
-------------------------------------

*	:class:`ll.nightshade.Connection` has new methods :meth:`commit`,
	 :meth:`rollback`, :meth:`close` and  :meth:`cancel`.


Changes in 0.13.1 (released 08/29/2008)
---------------------------------------

*	:meth:`Connect.cursor` now passes keyword arguments through to
	:meth:`ll.orasql.Connection.cursor`.


Changes in 0.13 (released 02/15/2008)
-------------------------------------

*	CherryPy 3.0 is required now.

*	The :func:`conditional` decorator has been removed. You can use CherryPy's
	``tools.etags`` tool.

*	The :func:`cache` decorator has been removed. You can use CherryPy's
	``tools.caching`` tool.


Changes in 0.12 (released 02/01/2008)
-------------------------------------

*	All docstrings use ReST now.


Changes in 0.11 (released 01/07/2008)
-------------------------------------

*	Updated the docstrings to XIST 3.0.

*	Added ReST versions of the documentation.


Changes in 0.10 (released 09/04/2007)
-------------------------------------

*	When a :class:`Connect` object is used as a decorator the database connection
	is no longer passed to the decorated function. This means that there will no
	longer be any signature mismatch between the original function and the
	decorated function. However the :class:`Connect` object must be stored
	somewhere else and the user must call the new :meth:`cursor` method to get a
	cursor.

*	Keyword argument in the :class:`Connect` constructor are passed on to the
	:func:`connect` call.


Changes in 0.9 (released 07/18/2007)
------------------------------------

*	Added support for the ``Cache-Control`` header.


Changes in 0.8.1 (released 06/26/2007)
--------------------------------------

*	Fixed a bug in :meth:`Call.__call__` (calling the procedure wasn't retried
	after the connection got lost).


Changes in 0.8 (released 06/21/2007)
------------------------------------

*	:class:`withconnection` has been renamed to :class:`Connect` and the
	implementation of :meth:`__call__` has been fixed.

*	:class:`Call` now needs a :class:`Connect` object as the second argument in
	the constructor (instead of taking :var:`connectstring`, :var:`pool` and
	:var:`retry` arguments).


Changes in 0.7.1 (released 05/12/2007)
--------------------------------------

*	Fixed a bug that surfaced after the connection to the database was lost.


Changes in 0.7 (released 03/16/2007)
------------------------------------

*	A new decorator :class:`withconnection` has been added. This can be use to
	retry database operations in case of stale connections.


Changes in 0.6 (released 03/12/2007)
------------------------------------

*	Initial public release.
