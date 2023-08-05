Migrating to version 0.13
-------------------------

The decorator :func:`cache` and :func:`conditional` no longer exist. Use
CherryPy's tools ``tools.etag`` and ``tools.caching`` instead.


Migrating to version 0.10
-------------------------

When a :class:`Connect` object is used as a decorator the database connection is
no longer passed to the decorated function. You have to store the
:class:`Connect` object somewhere and call it's new :meth:`cursor` method
explicitely.


Migrating to version 0.8
------------------------

The class :class:`withconnection` has been renamed to :class:`Connect`.

Calling functions and procedures has changed a bit. Replace the following
old code::

	proc = nightshade.Call(orasql.Procedure("proc"), connectstring=connectstring)
	
	@cherrypy.expose
	def foo(arg):
		return proc(arg)

with::

	connection = nightshade.Connect(connectstring=connectstring)
	proc = nightshade.Call(orasql.Procedure("proc"), connection)
	
	@cherrypy.expose
	def foo(arg):
		return proc(arg)
