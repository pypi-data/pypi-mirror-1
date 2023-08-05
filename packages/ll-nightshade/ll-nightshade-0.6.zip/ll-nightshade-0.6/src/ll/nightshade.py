# -*- coding: iso-8859-1 -*-

"""
<par>This module provides a class <pyref class="Call"><class>Call</class></pyref>
that allows you to use Oracle PL/SQL procedures/functions as
<link href="http://www.cherrypy.org/">CherryPy</link> response handlers.
A <class>Call</class> objects wraps a <pyref module="ll.orasql" class="Procedure"><class>Procedure</class></pyref>
or <pyref module="ll.orasql" class="Function"><class>Function</class></pyref> object
from  <pyref module="ll.orasql"><module>ll.orasql</module></pyref>.</par>
<par>For example, you might have the following PL/SQL function:</par>
<prog><![CDATA[
create or replace function helloworld
(
	who varchar2
)
return varchar2
as
begin
	return '<html><head><title>Hello ' || who || '</title></head><body><h1>Hello, ' || who || '!</h1></body></html>';
end;
]]></prog>
<par>Using this function as a CherryPy response handler can be done like this:</par>
<prog>
import cherrypy

from ll import orasql, nightshade


proc = nightshade.Call(orasql.Function("helloworld"), connectstring="user/pwd")

class HelloWorld(object):
	@cherrypy.expose
	def default(self, who="World"):
		cherrypy.response.headers["Content-Type"] = "text/html"
		return proc(who=who)

cherrypy.quickstart(HelloWorld())
"""

import time, datetime, threading

import cherrypy

import cx_Oracle

from ll import orasql


weekdayname = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
monthname = [None, "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


class UTC(datetime.tzinfo):
	"""
	Timezone object for UTC
	"""
	def utcoffset(self, dt):
		return datetime.timedelta(0)

	def dst(self, dt):
		return datetime.timedelta(0)

	def tzname(self, dt):
		return "UTC"

utc = UTC()


def getnow():
	"""
	Get the current date and time as a <class>datetime.datetime</class>
	object in UTC with timezone info.
	"""
	return datetime.datetime.utcnow().replace(tzinfo=utc)


def httpdate(dt):
	"""
	<par>Return a string suitable for a <z>Last-Modified</z> and <z>Expires</z> header.</par>
	
	<par><arg>dt</arg> is a <class>datetime.datetime</class> object.
	If <lit><arg>dt</arg>.tzinfo</lit> is <lit>None</lit> <arg>dt</arg> is assumed
	to be in the local timezone (using the current UTFC offset which might be
	different from the one used by <arg>dt</arg>).</par>
	"""
	if dt.tzinfo is None:
		dt += datetime.timedelta(seconds=[time.timezone, time.altzone][time.daylight])
	else:
		dt -= dt.tzinfo.utcoffset(dt)
	return "%s, %02d %3s %4d %02d:%02d:%02d GMT" % (weekdayname[dt.weekday()], dt.day, monthname[dt.month], dt.year, dt.hour, dt.minute, dt.second)


class cache(object):
	"""
	<par>Decorator that adds caching to a CherryPy handler.</par>
	
	<par>Calling a <class>cache</class> object will cache return values
	of the decorated function for a certain amount of time. You can pass
	the timespan either via <arg>timedelta</arg> (which must be a
	<class>datetime.timedelta</class> object), or via <arg>timedeltaargs</arg>
	(which will be used as keyword arguments for creating a
	<class>datetime.timedelta</class> object).
	"""
	def __init__(self, timedelta=None, **timedeltaargs):
		if timedelta is None:
			timedelta = datetime.timedelta(**timedeltaargs)
		self.timedelta = timedelta
		self.lock = threading.Lock()
		self.cache = {}

	def __call__(self, func):
		def wrapper(*args, **kwargs):
			# Don't cache POST requests etc.
			if cherrypy.request.method != "GET":
				return func(*args, **kwargs)
			now = getnow()
			cachekey = (args, tuple(sorted(kwargs.iteritems())))
			self.lock.acquire()
			try:
				fetch = False
				try:
					(timestamp, content, headers) = self.cache[cachekey]
				except KeyError:
					fetch = True
				else:
					if timestamp+self.timedelta < now:
						fetch = True
					else:
						cherrypy.response.headers.update(headers)
				if fetch:
					timestamp = getnow()
					content = func(*args, **kwargs)
					# Don't cache error responses
					if cherrypy.response.status is None or 200 <= cherrypy.response.status <= 203:
						self.cache[cachekey] = (timestamp, content, cherrypy.response.headers.copy())
			finally:
				self.lock.release()
			return content
		wrapper.__name__ = func.__name__
		wrapper.__doc__ = func.__doc__
		wrapper.__dict__.update(func.__dict__)
		return wrapper


def conditional(func):
	"""
	<par>Decorator that adds handling of conditional <lit>GET</lit>s to a CherryPy handler.</par>
	
	<par>The decorated function will correctly handle the <lit>If-Modified-Since</lit>
	and <lit>If-None-Match</lit> request headers. For this to work properly
	the decorated function should set the <lit>Last-Modified</lit> and/or
	the <lit>ETag</lit> header.
	"""
	def wrapper(*args, **kwargs):
		data = func(*args, **kwargs)

		req_ifmodifiedsince = cherrypy.request.headerMap.get("If-Modified-Since", None)
		req_ifnonematch = cherrypy.request.headerMap.get("If-None-Match", None)
		res_lastmodified = cherrypy.response.headerMap.get("Last-Modified", None)
		res_etag = cherrypy.response.headerMap.get("ETag", None)

		modified = True
		if req_ifmodifiedsince is not None and res_lastmodified is not None:
			modified = req_ifmodifiedsince != res_lastmodified
		if req_ifnonematch is not None and res_etag is not None and not modified:
			modified = req_ifnonematch != res_etag
		if not modified:
			cherrypy.response.status = "304 Not Modified"
			# The proper headers have already been set, but Content-Length seems to be broken
			cherrypy.response.body = None
			return ""
		return data

	wrapper.__name__ = func.__name__
	wrapper.__doc__ = func.__doc__
	wrapper.__dict__.update(func.__dict__)
	return wrapper


class Call(object):
	"""
	<par>Wrap an Oracle procedure or function in a CherryPy handler.</par>

	<par><class>Call</class> object wraps a procedure or function object from
	<pyref module="ll.orasql"><module>ll.orasql</module></pyref> and makes it
	callable just like a CherryPy handler.
	"""
	_badoracleexceptions = set((
		28,    # your session has been killed
		1012,  # not logged on
		1014,  # Oracle shutdown in progress
		1033,  # Oracle startup or shutdown in progress
		1034,  # Oracle not available
		1035,  # Oracle only available to users with RESTRICTED SESSION privilege
		1089,  # immediate shutdown in progress - no operations are permitted
		1090,  # Shutdown in progress - connection is not permitted
		1092,  # ORACLE instance terminated. Disconnection forced
		3106,  # fatal two-task communication protocol error
		3113,  # end-of-file on communication channel
		3114,  # not connected to ORACLE
		3135,  # connection lost contact
		12154, # TNS:could not resolve the connect identifier specified
		12540, # TNS:internal limit restriction exceeded
		12541, # TNS:no listener
		12543, # TNS:destination host unreachable
	))

	def __init__(self, callable, pool=None, connectstring=None):
		"""
		Create a <class>Call</class> object wrapping the function or procedure
		<arg>callable</arg>.
		"""
		if (pool is not None) == (connectstring is not None):
			raise TypeError("either pool or connectstring must be specified")
		self.callable = callable
		# Calculate parameter mapping now, so we don't get concurrency problems later
		self.pool = pool
		self.connection = None
		self.connectstring = connectstring
		cursor = self._cursor()
		callable._calcargs(cursor)

	def _cursor(self):
		if self.pool is not None:
			connection = self.pool.acquire()
			cursor = connection.cursor()
		elif self.connection is not None:
			cursor = self.connection.cursor()
		else:
			self.connection = orasql.connect(self.connectstring, threaded=True)
			cursor = self.connection.cursor()
		return cursor

	def _call(self, cursor, *args, **kwargs):
		if isinstance(self.callable, orasql.Procedure):
			return (None, self.callable(cursor, *args, **kwargs))
		else:
			return self.callable(cursor, *args, **kwargs)

	def _isbadoracleexception(self, exc):
		if exc.args:
			code = getattr(exc[0], "code", 0)
			if code in self._badoracleexceptions:
				return True
		return False

	def __call__(self, *args, **kwargs):
		"""
		<par>Call the procedure/function with the arguments <arg>args</arg> and
		<arg>kwargs</arg> mapping Python function arguments to Oracle procedure/function
		arguments. On return from the procedure the <lit>out</lit> parameter is
		mapped to the CherryPy response body, and the parameters <lit>expires</lit>
		(the number of days from now), <lit>lastmodified</lit> (a date in UTC),
		<lit>mimetype</lit> (a string), <lit>encoding</lit> (a string) and
		<lit>etag</lit> (a string) are mapped to the appropriate CherryPy response
		headers. If <lit>etag</lit> is not specified a value is calculated.</par>
		<par>If the procedure/function raised a PL/SQL exception with a code between
		20200 and 20599, 20000 will be substracted from this value and the resulting
		value will be used as the HTTP repsonse code, i.e. 20404 will give a
		"Not Found" response.
		"""
		
		now = getnow()
		try:
			if self.pool is not None:
				for i in xrange(10):
					try:
						cursor = self._cursor()
						(body, result) = self._call(cursor, *args, **kwargs)
					except cx_Oracle.DatabaseError, exc:
						if self._isbadoracleexception(exc):
							# Drop dead connection and retry
							self.pool.drop(connection)
						else:
							raise
					else:
						break
			else:
				for i in xrange(10):
					try:
						cursor = self._cursor()
						(body, result) = self._call(cursor, *args, **kwargs)
					except cx_Oracle.DatabaseError, exc:
						if self._isbadoracleexception(exc):
							self.connection = None # retry with new connection
						else:
							raise
					else:
						break
		except cx_Oracle.DatabaseError, exc:
			if exc.args:
				code = getattr(exc[0], "code", 0)
				if 20200 <= code <= 20599:
					raise cherrypy.HTTPError(code-20000)
				else:
					raise

		# Set HTTP headers from parameters
		expires = result.get("p_expires", None)
		if expires is not None:
			cherrypy.response.headers["Expires"] = httpdate(now + datetime.timedelta(days=expires))
		lastmodified = result.get("p_lastmodified", None)
		if lastmodified is not None:
			cherrypy.response.headers["Last-Modified"] = httpdate(lastmodified)
		mimetype = result.get("p_mimetype", None)
		if mimetype is not None:
			encoding = result.get("p_encoding", None)
			if encoding is not None:
				cherrypy.response.headers["Content-Type"] = "%s; charset=%s" % (mimetype, encoding)
			else:
				cherrypy.response.headers["Content-Type"] = mimetype
		hasetag = False
		etag = result.get("p_etag", None)
		if etag is not None:
			cherrypy.response.headers["ETag"] = etag
			hasetag = True

		# Get status code
		status = result.get("p_status", None)
		if status is not None:
			cherrypy.response.status = status

		# Get response body
		if "c_out" in result:
			body = result.c_out
			if hasattr(result, "read"):
				result = result.read()
			if not hasetag:
				cherrypy.response.headers["ETag"] = '"%x"' % hash(body)

		if hasattr(body, "read"):
			body = body.read()
		return body
