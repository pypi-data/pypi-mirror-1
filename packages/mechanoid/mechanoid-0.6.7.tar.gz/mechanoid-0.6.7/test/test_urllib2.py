"""Tests for ClientCookie._urllib2_support."""

# XXX
# Request (I'm too lazy)
# CacheFTPHandler (hard to write)
# parse_keqv_list, parse_http_list (I'm leaving this for Anthony Baxter
#  and Greg Stein, since they're doing Digest Authentication)
# Authentication stuff (ditto)
# ProxyHandler, CustomProxy, CustomProxyHandler (I don't use a proxy)
# GopherHandler (haven't used gopher for a decade or so...)

import unittest, StringIO, os, sys, UserDict

import urllib2
from mechanoid.misc.Request import Request
from mechanoid.misc.OpenerDirector import OpenerDirector
from mechanoid.useragent.http_handlers.HTTPHandler import HTTPHandler
from mechanoid.useragent.http_handlers.HTTPRedirectHandler import HTTPRedirectHandler
from mechanoid.useragent.http_handlers.AbstractHTTPHandler import AbstractHTTPHandler
from mechanoid.http_processors import *
from mechanoid.misc.Common import Common
common = Common()


class MockOpener:
	addheaders = []
	def open(self, req, data=None):
		self.req, self.data = req, data
	def error(self, proto, *args):
		self.proto, self.args = proto, args

class MockFile:
	def read(self, count=None): pass
	def readline(self, count=None): pass
	def close(self): pass

class MockHeaders(UserDict.UserDict):
	def getallmatchingheaders(self, name):
		r = []
		for k, v in self.data.items():
			r.append("%s: %s" % (k, v))
		return r

class MockResponse(StringIO.StringIO):
	def __init__(self, code, msg, headers, data, url=None):
		StringIO.StringIO.__init__(self, data)
		self.code, self.msg, self.headers, self.url = code, msg, headers, url
	def info(self):
		return self.headers
	def geturl(self):
		return self.url

class MockCookieJar:
	def add_cookie_header(self, request, unverifiable=False):
		self.ach_req, self.ach_u = request, unverifiable
	def extract_cookies(self, response, request, unverifiable=False):
		self.ec_req, self.ec_r, self.ec_u = request, response, unverifiable

class MockMethod:
	def __init__(self, meth_name, action, handle):
		self.meth_name = meth_name
		self.handle = handle
		self.action = action
	def __call__(self, *args):
		return apply(self.handle, (self.meth_name, self.action)+args)

class MockHandler:
	processor_order = 500
	def __init__(self, methods):
		self._define_methods(methods)
	def _define_methods(self, methods):
		for spec in methods:
			if len(spec) == 2: name, action = spec
			else: name, action = spec, None
			meth = MockMethod(name, action, self.handle)
			setattr(self.__class__, name, meth)
	def handle(self, fn_name, action, *args, **kwds):
		self.parent.calls.append((self, fn_name, args, kwds))
		if action is None:
			return None
		elif action == "return self":
			return self
		elif action == "return response":
			res = MockResponse(200, "OK", {}, "")
			return res
		elif action == "return request":
			return Request("http://blah/")
		elif common.startswith(action, "error"):
			code = int(action[-3:])
			res = MockResponse(200, "OK", {}, "")
			return self.parent.error("http", args[0], res, code, "", {})
		elif action == "raise":
			raise urllib2.URLError("blah")
		assert False
	def close(self): pass
	def add_parent(self, parent):
		self.parent = parent
		self.parent.calls = []
	def __cmp__(self, other):
		if hasattr(other, "handler_order"):
			return cmp(self.handler_order, other.handler_order)
		# No handler_order, leave in original order.  Yuck.
		return -1
		#return cmp(id(self), id(other))


def add_ordered_mock_handlers(opener, meth_spec):
	handlers = []
	count = 0
	for meths in meth_spec:
		class MockHandlerSubclass(MockHandler): pass
		h = MockHandlerSubclass(meths)
		h.handler_order = h.processor_order = count
		h.add_parent(opener)
		count = count + 1
		handlers.append(h)
		opener.add_handler(h)
	return handlers

class OpenerDirectorTests(unittest.TestCase):

	def test_handled(self):
		# handler returning non-None means no more handlers will be called
		o = OpenerDirector()
		meth_spec = [
			["http_open", "ftp_open", "http_error_302"],
			["ftp_open"],
			[("http_open", "return self")],
			[("http_open", "return self")],
			]
		handlers = add_ordered_mock_handlers(o, meth_spec)

		req = Request("http://example.com/")
		r = o.open(req)
		# Second http_open gets called, third doesn't, since second returned
		# non-None.	 Handlers without http_open never get any methods called
		# on them.
		# In fact, second mock handler returns self (instead of response),
		# which becomes the OpenerDirector's return value.
		self.assert_(r == handlers[2])
		calls = [(handlers[0], "http_open"), (handlers[2], "http_open")]
		for i in range(len(o.calls)):
			handler, name, args, kwds = o.calls[i]
			self.assert_((handler, name) == calls[i])
			self.assert_(args == (req,))

	def test_handler_order(self):
		from mechanoid.misc.OpenerDirector import OpenerDirector
		o = OpenerDirector()
		handlers = []
		for meths, handler_order in [
			([("http_open", "return self")], 500),
			(["http_open"], 0),
			]:
			class MockHandlerSubclass(MockHandler): pass
			h = MockHandlerSubclass(meths)
			h.handler_order = handler_order
			handlers.append(h)
			o.add_handler(h)

		r = o.open("http://example.com/")
		# handlers called in reverse order, thanks to their sort order
		self.assert_(o.calls[0][0] == handlers[1])
		self.assert_(o.calls[1][0] == handlers[0])

	def test_raise(self):
		# raising URLError stops processing of request
		o = OpenerDirector()
		meth_spec = [
			[("http_open", "raise")],
			[("http_open", "return self")],
			]
		handlers = add_ordered_mock_handlers(o, meth_spec)

		req = Request("http://example.com/")
		self.assertRaises(urllib2.URLError, o.open, req)
		self.assert_(o.calls == [(handlers[0], "http_open", (req,), {})])

##	   def test_error(self):
##		   # XXX this doesn't actually seem to be used in standard library,
##		   #  but should really be tested anyway...

	def test_http_error(self):
		# XXX http_error_default
		# http errors are a special case
		o = OpenerDirector()
		meth_spec = [
			[("http_open", "error 302")],
			[("http_error_400", "raise"), "http_open"],
			[("http_error_302", "return response"), "http_error_303",
			 "http_error"],
			[("http_error_302")],
			]
		handlers = add_ordered_mock_handlers(o, meth_spec)

		class Unknown: pass

		req = Request("http://example.com/")
		r = o.open(req)
		assert len(o.calls) == 2
		calls = [(handlers[0], "http_open", (req,)),
				 (handlers[2], "http_error_302", (req, Unknown, 302, "", {}))]
		for i in range(len(calls)):
			handler, method_name, args, kwds = o.calls[i]
			self.assert_((handler, method_name) == calls[i][:2])
			# check handler methods were called with expected arguments
			expected_args = calls[i][2]
			for j in range(len(args)):
				if expected_args[j] is not Unknown:
					self.assert_(args[j] == expected_args[j])

	def test_processors(self):
		# *_request / *_response methods get called appropriately
		o = OpenerDirector()
		meth_spec = [
			[("http_request", "return request"),
			 ("http_response", "return response")],
			[("http_request", "return request"),
			 ("http_response", "return response")],
			]
		handlers = add_ordered_mock_handlers(o, meth_spec)

		req = Request("http://example.com/")
		r = o.open(req)
		# processor methods are called on *all* handlers that define them,
		# not just the first handler
		calls = [(handlers[0], "http_request"), (handlers[1], "http_request"),
				 (handlers[0], "http_response"), (handlers[1], "http_response")]

		for i in range(len(o.calls)):
			handler, name, args, kwds = o.calls[i]
			if i < 2:
				# *_request
				self.assert_((handler, name) == calls[i])
				self.assert_(len(args) == 1)
				self.assert_(isinstance(args[0], Request))
			else:
				## XXX breaks on 2.4
				# *_response
##				self.assert_((handler, name) == calls[i])
##				self.assert_(len(args) == 2)
				self.assert_(isinstance(args[0], Request))
				# response from opener.open is None, because there's no
				# handler that defines http_open to handle it
##				self.assert_(args[1] is None or
##							 isinstance(args[1], MockResponse))


class MockHTTPClass:
	def __init__(self):
		self.req_headers = []
		self.data = None
		self.raise_on_endheaders = False
	def __call__(self, host):
		self.host = host
		return self
	def set_debuglevel(self, level): self.level = level
	def putrequest(self, method, selector):
		self.method, self.selector = method, selector
	def putheader(self, key, value):
		self.req_headers.append((key, value))
	def endheaders(self):
		if self.raise_on_endheaders:
			import socket
			raise socket.error()
	def send(self, data): self.data = data
	def getreply(self): return 200, "OK", {}
	def getfile(self): return MockFile()


class MockFTPWrapper:
	def __init__(self, data): self.data = data
	def retrfile(self, filename, filetype):
		self.filename, self.filetype = filename, filetype
		return StringIO.StringIO(self.data), len(self.data)

class NullFTPHandler(urllib2.FTPHandler):
	def __init__(self, data): self.data = data
	def connect_ftp(self, user, passwd, host, port, dirs):
		self.user, self.passwd = user, passwd
		self.host, self.port = host, port
		self.dirs = dirs
		self.ftpwrapper = MockFTPWrapper(self.data)
		return self.ftpwrapper

def sanepathname2url(path):
	import urllib
	urlpath = urllib.pathname2url(path)
	if os.name == "nt" and urlpath.startswith("///"):
		urlpath = urlpath[2:]
	# XXX don't ask me about the mac...
	return urlpath

class MockRobotFileParserClass:
	def __init__(self):
		self.calls = []
		self._can_fetch = True
	def clear(self):
		self.calls = []
	def __call__(self):
		self.calls.append("__call__")
		return self
	def set_url(self, url):
		self.calls.append(("set_url", url))
	def read(self):
		self.calls.append("read")
	def can_fetch(self, ua, url):
		self.calls.append(("can_fetch", ua, url))
		return self._can_fetch

class HandlerTests(unittest.TestCase):

	if hasattr(sys, "version_info") and sys.version_info > (2, 1, 3, "final", 0):

		def test_ftp(self):
			import ftplib, socket
			data = "rheum rhaponicum"
			h = NullFTPHandler(data)
			o = h.parent = MockOpener()

			for url, host, port, type_, dirs, filename, mimetype in [
				("ftp://localhost/foo/bar/baz.html",
				 "localhost", ftplib.FTP_PORT, "I",
				 ["foo", "bar"], "baz.html", "text/html"),
				# XXXX Bug: FTPHandler tries to gethostbyname "localhost:80",
				#  with the port still there.
				#("ftp://localhost:80/foo/bar/",
				# "localhost", 80, "D",
				# ["foo", "bar"], "", None),
				# XXXX bug: second use of splitattr() in FTPHandler should be
				#  splitvalue()
				#("ftp://localhost/baz.gif;type=a",
				# "localhost", ftplib.FTP_PORT, "A",
				# [], "baz.gif", "image/gif"),
				]:
				r = h.ftp_open(Request(url))
				# ftp authentication not yet implemented by FTPHandler
				self.assert_(h.user == h.passwd == "")
				self.assert_(h.host == socket.gethostbyname(host))
				self.assert_(h.port == port)
				self.assert_(h.dirs == dirs)
				self.assert_(h.ftpwrapper.filename == filename)
				self.assert_(h.ftpwrapper.filetype == type_)
				headers = r.info()
				self.assert_(headers["Content-type"] == mimetype)
				self.assert_(int(headers["Content-length"]) == len(data))

		def test_file(self):
			import time, rfc822, socket
			h = urllib2.FileHandler()
			o = h.parent = MockOpener()

			#TESTFN = test_support.TESTFN
			TESTFN = "test.txt"
			urlpath = sanepathname2url(os.path.abspath(TESTFN))
			towrite = "hello, world\n"
			for url in [
				"file://localhost%s" % urlpath,
				"file://%s" % urlpath,
				"file://%s%s" % (socket.gethostbyname('localhost'), urlpath),
				"file://%s%s" % (socket.gethostbyname(socket.gethostname()),
								 urlpath),
				]:
				f = open(TESTFN, "wb")
				try:
					try:
						f.write(towrite)
					finally:
						f.close()

					r = h.file_open(Request(url))
					try:
						data = r.read()
						headers = r.info()
						newurl = r.geturl()
					finally:
						r.close()
					stats = os.stat(TESTFN)
					modified = rfc822.formatdate(stats.st_mtime)
				finally:
					os.remove(TESTFN)
				self.assertEqual(data, towrite)
				self.assertEqual(headers["Content-type"], "text/plain")
				self.assertEqual(headers["Content-length"], "13")
				self.assertEqual(headers["Last-modified"], modified)

			for url in [
				"file://localhost:80%s" % urlpath,
	# XXXX bug: these fail with socket.gaierror, should be URLError
	##			   "file://%s:80%s/%s" % (socket.gethostbyname('localhost'),
	##									  os.getcwd(), TESTFN),
	##			   "file://somerandomhost.ontheinternet.com%s/%s" %
	##			   (os.getcwd(), TESTFN),
				]:
				try:
					f = open(TESTFN, "wb")
					try:
						f.write(towrite)
					finally:
						f.close()

					self.assertRaises(urllib2.URLError,
									  h.file_open, Request(url))
				finally:
					os.remove(TESTFN)

			h = urllib2.FileHandler()
			o = h.parent = MockOpener()
			# XXXX why does // mean ftp (and /// mean not ftp!), and where
			#  is file: scheme specified?  I think this is really a bug, and
			#  what was intended was to distinguish between URLs like:
			# file:/blah.txt (a file)
			# file://localhost/blah.txt (a file)
			# file:///blah.txt (a file)
			# file://ftp.example.com/blah.txt (an ftp URL)
			for url, ftp in [
				("file://ftp.example.com//foo.txt", True),
				("file://ftp.example.com///foo.txt", False),
	# XXXX bug: fails with OSError, should be URLError
				("file://ftp.example.com/foo.txt", False),
				]:
				req = Request(url)
				try:
					h.file_open(req)
				# XXXX remove OSError when bug fixed
				except (urllib2.URLError, OSError):
					self.assert_(not ftp)
				else:
					self.assert_(o.req is req)
					self.assertEqual(req.type, "ftp")

##		   def test_file(self):
##			   import time, rfc822, socket
##			   h = urllib2.FileHandler()
##			   o = h.parent = MockOpener()

##			   #from test_support import TESTFN
##			   TESTFN = "test.txt"
##			   towrite = "hello, world\n"
##			   for url in [
##				   "file://localhost%s/%s" % (os.getcwd(), TESTFN),
##				   "file://%s/%s" % (os.getcwd(), TESTFN),
##				   "file://%s%s/%s" % (socket.gethostbyname('localhost'),
##									   os.getcwd(), TESTFN),
##				   "file://%s%s/%s" % (socket.gethostbyname(socket.gethostname()),
##									   os.getcwd(), TESTFN),
##				   # XXX Windows / Mac format(s), ... ?
##				   ]:
##				   create_time = time.time()
##				   f = open(TESTFN, "w")
##				   try:
##					   try:
##						   f.write(towrite)
##					   finally:
##						   f.close()

##					   r = h.file_open(Request(url))
##					   try:
##						   data = r.read()
##						   headers = r.info()
##						   newurl = r.geturl()
##					   finally:
##						   r.close()
##					   stats = os.stat(TESTFN)
##					   modified = rfc822.formatdate(stats.st_mtime)
##				   finally:
##					   os.remove(TESTFN)
##				   self.assert_(data == towrite)
##				   self.assert_(headers["Content-type"] == "text/plain")
##				   self.assert_(headers["Content-length"] == "13")
## ##				  # Fudge Last-modified string comparison by one second to
## ##				  # prevent spurious failure on crossing a second boundary while
## ##				  # executing this test.
## ##				  # XXXX This test still fails occasionally!  Why?
## ##				  unfudged = rfc822.formatdate(create_time)
## ##				  fudged = rfc822.formatdate(create_time+1)
## ##				  self.assert_(headers["Last-modified"] in [unfudged, fudged])
##				   self.assert_(headers["Last-modified"] == modified)

##			   for url in [
##				   "file://localhost:80%s/%s" % (os.getcwd(), TESTFN),
##				   # XXXX bug: these fail with socket.gaierror, should be URLError
##				   #"file://%s:80%s/%s" % (socket.gethostbyname('localhost'),
##				   #					   os.getcwd(), TESTFN),
##				   #"file://somerandomhost.ontheinternet.com%s/%s" %
##				   #(os.getcwd(), TESTFN),
##				   ]:
##				   try:
##					   f = open(TESTFN, "w")
##					   try:
##						   f.write(towrite)
##					   finally:
##						   f.close()

##					   self.assertRaises(urllib2.URLError,
##										 h.file_open, Request(url))
##				   finally:
##					   os.remove(TESTFN)

##			   h = urllib2.FileHandler()
##			   o = h.parent = MockOpener()
##			   # XXXX why does // mean ftp (and /// mean not ftp!), and where
##			   #  is file: scheme specified?  I think this is really a bug, and
##			   #  what was intended was to distinguish between URLs like:
##			   # file:/blah.txt (a file)
##			   # file://localhost/blah.txt (a file)
##			   # file:///blah.txt (a file)
##			   # file://ftp.example.com/blah.txt (an ftp URL)
##			   for url, ftp in [
##				   ("file://ftp.example.com//foo.txt", True),
##				   ("file://ftp.example.com///foo.txt", False),
##				   # XXXX bug: fails with OSError, should be URLError
##				   ("file://ftp.example.com/foo.txt", False),
##				   ]:
##				   req = Request(url)
##				   try:
##					   h.file_open(req)
##				   except (urllib2.URLError, OSError):	# XXXX remove OSError
##					   self.assert_(not ftp)
##				   else:
##					   self.assert_(o.req is req)
##					   self.assert_(req.type == "ftp")

	def test_http(self):
		h = AbstractHTTPHandler()
		o = h.parent = MockOpener()

		url = "http://example.com/"
		for method, data in [("GET", None), ("POST", "blah")]:
			req = Request(url, data, {"Foo": "bar"})
			req.add_unredirected_header("Spam", "eggs")
			http = MockHTTPClass()
			r = h.do_open(http, req)

			# result attributes
			r.read; r.readline	# wrapped MockFile methods
			r.info; r.geturl  # addinfourl methods
			r.code, r.msg == 200, "OK"	# added from MockHTTPClass.getreply()
			hdrs = r.info()
			hdrs.get; hdrs.has_key	# r.info() gives dict from .getreply()
			self.assert_(r.geturl() == url)

			self.assert_(http.host == "example.com")
			self.assert_(http.level == 0)
			self.assert_(http.method == method)
			self.assert_(http.selector == "/")
			http.req_headers.sort()
			self.assert_(http.req_headers == [("Foo", "bar"), ("Spam", "eggs")])
			self.assert_(http.data == data)

		# check socket.error converted to URLError
		http.raise_on_endheaders = True
		self.assertRaises(urllib2.URLError, h.do_open, http, req)

		# check adding of standard headers
		o.addheaders = [("Spam", "eggs")]
		for data in "", None:  # POST, GET
			req = Request("http://example.com/", data)
			r = MockResponse(200, "OK", {}, "")
			newreq = h.do_request_(req)
			if data is None:  # GET
				self.assert_(not req.unredirected_hdrs.has_key("Content-length"))
				self.assert_(not req.unredirected_hdrs.has_key("Content-type"))
			else:  # POST
				self.assert_(req.unredirected_hdrs["Content-length"] == "0")
				self.assert_(req.unredirected_hdrs["Content-type"] ==
							 "application/x-www-form-urlencoded")
			# XXX the details of Host could be better tested
			self.assert_(req.unredirected_hdrs["Host"] == "example.com")
			self.assert_(req.unredirected_hdrs["Spam"] == "eggs")

			# don't clobber existing headers
			req.add_unredirected_header("Content-length", "foo")
			req.add_unredirected_header("Content-type", "bar")
			req.add_unredirected_header("Host", "baz")
			req.add_unredirected_header("Spam", "foo")
			newreq = h.do_request_(req)
			self.assert_(req.unredirected_hdrs["Content-length"] == "foo")
			self.assert_(req.unredirected_hdrs["Content-type"] == "bar")
			self.assert_(req.unredirected_hdrs["Host"] == "baz")
			self.assert_(req.unredirected_hdrs["Spam"] == "foo")

# XXX Fails on Python 2.4
## 	def test_request_upgrade(self):
## 		h = HTTPRequestUpgradeProcessor()
## 		o = h.parent = MockOpener()

## 		# urllib2.Request gets upgraded
## 		req = urllib2.Request("http://example.com/")
## 		newreq = h.http_request(req)
## 		self.assert_(newreq is not req) #XXX
## 		self.assert_(newreq.__class__ is Request)
## 		# ClientCookie._urllib2_support.Request doesn't
## 		req = Request("http://example.com/")
## 		newreq = h.http_request(req)
## 		self.assert_(newreq is req)
## 		self.assert_(newreq.__class__ is Request)

	def test_referer(self):
		h = HTTPRefererProcessor()
		o = h.parent = MockOpener()

		# normal case
		url = "http://example.com/"
		req = Request(url)
		r = MockResponse(200, "OK", {}, "", url)
		newr = h.http_response(req, r)
		self.assert_(r is newr)
		self.assert_(h.referer == url)
		newreq = h.http_request(req)
		self.assert_(req is newreq)
		self.assert_(req.unredirected_hdrs["Referer"] == url)
		# don't clobber existing Referer
		ref = "http://set.by.user.com/"
		req.add_unredirected_header("Referer", ref)
		newreq = h.http_request(req)
		self.assert_(req is newreq)
		self.assert_(req.unredirected_hdrs["Referer"] == ref)

	def test_errors(self):
		h = HTTPErrorProcessor()
		o = h.parent = MockOpener()

		url = "http://example.com/"
		req = Request(url)
		# 200 OK is passed through
		r = MockResponse(200, "OK", {}, "", url)
		newr = h.http_response(req, r)
		self.assert_(r is newr)
		self.assert_(not hasattr(o, "proto"))  # o.error not called
		# anything else calls o.error (and MockOpener returns None, here)
		r = MockResponse(201, "Created", {}, "", url)
		self.assert_(h.http_response(req, r) is None)
		self.assert_(o.proto == "http")	 # o.error called
		self.assert_(o.args == (req, r, 201, "Created", {}))

	def test_cookies(self):
		cj = MockCookieJar()
		h = HTTPCookieProcessor(cj)
		o = h.parent = MockOpener()

		req = urllib2.Request("http://example.com/")
		r = MockResponse(200, "OK", {}, "")
		newreq = h.http_request(req)
		self.assert_(cj.ach_req is req is newreq)
		self.assert_(req.origin_req_host == "example.com")
		self.assert_(cj.ach_u == False)
		newr = h.http_response(req, r)
		self.assert_(cj.ec_req is req)
		self.assert_(cj.ec_r is r is newr)
		self.assert_(cj.ec_u == False)

	def test_seekable(self):
		h = SeekableProcessor()
		o = h.parent = MockOpener()

		req = urllib2.Request("http://example.com/")
		class MockUnseekableResponse: pass
		r = MockUnseekableResponse()
		newr = h.http_response(req, r)
		self.assert_(not hasattr(r, "seek"))
		self.assert_(hasattr(newr, "seek"))

	def test_http_equiv(self):
		h = HTTPEquivProcessor()
		o = h.parent = MockOpener()

		req = Request("http://example.com/")
		r = MockResponse(200, "OK", {"Foo": "Bar"},
						 '<html><head>'
						 '<meta http-equiv="Refresh" content="spam">'
						 '</head></html>')
		newr = h.http_response(req, r)
		headers = newr.info()
		self.assert_(headers["Refresh"] == "spam")
		self.assert_(headers["Foo"] == "Bar")

	def test_refresh(self):
		# XXX processor constructor optional args
		h = HTTPRefreshProcessor()
		o = h.parent = MockOpener()

		req = Request("http://example.com/")
		headers = MockHeaders({"refresh": '0; url="http://example.com/foo/"'})
		r = MockResponse(200, "OK", headers, "")
		newr = h.http_response(req, r)
		self.assert_(o.proto == "http")
		self.assert_(o.args == (req, r, "refresh", "OK", headers))

	def test_redirect(self):
		from_url = "http://example.com/a.html"
		to_url = "http://example.com/b.html"
		h = HTTPRedirectHandler()
		o = h.parent = MockOpener()

		# ordinary redirect behaviour
		for code in 301, 302, 303, 307, "refresh":
			for data in None, "blah\nblah\n":
				method = getattr(h, "http_error_%s" % code)
				req = Request(from_url, data)
				req.add_header("Nonsense", "viking=withhold")
				req.add_unredirected_header("Spam", "spam")
				req.origin_req_host = "example.com"	 # XXX
				try:
					method(req, MockFile(), code, "Blah",
						   MockHeaders({"location": to_url}))
				except urllib2.HTTPError:
					# 307 in response to POST requires user OK
					self.assert_(code == 307 and data is not None)
				self.assert_(o.req.get_full_url() == to_url)
				try:
					self.assert_(o.req.get_method() == "GET")
				except AttributeError:
					self.assert_(not o.req.has_data())
				self.assert_(o.req.headers["Nonsense"] == "viking=withhold")
				self.assert_(not o.req.headers.has_key("Spam"))
				self.assert_(not o.req.unredirected_hdrs.has_key("Spam"))

		# loop detection
		def redirect(h, req, url=to_url):
			h.http_error_302(req, MockFile(), 302, "Blah",
							 MockHeaders({"location": url}))
		# Note that the *original* request shares the same record of
		# redirections with the sub-requests caused by the redirections.

		# detect infinite loop redirect of a URL to itself
		req = Request(from_url)
		req.origin_req_host = "example.com"
		count = 0
		try:
			while 1:
				redirect(h, req, "http://example.com/")
				count = count + 1
		except urllib2.HTTPError:
			# don't stop until max_repeats, because cookies may introduce state
			self.assert_(count == HTTPRedirectHandler.max_repeats)

		# detect endless non-repeating chain of redirects
		req = Request(from_url)
		req.origin_req_host = "example.com"
		count = 0
		try:
			while 1:
				redirect(h, req, "http://example.com/%d" % count)
				count = count + 1
		except urllib2.HTTPError:
			self.assert_(count == HTTPRedirectHandler.max_redirections)

class MyHTTPHandler(HTTPHandler): pass
class FooHandler(urllib2.BaseHandler):
	def foo_open(self): pass
class BarHandler(urllib2.BaseHandler):
	def bar_open(self): pass

class A:
	def a(self): pass
class B(A):
	def a(self): pass
	def b(self): pass
class C(A):
	def c(self): pass
class D(C, B):
	def a(self): pass
	def d(self): pass


if __name__ == "__main__":
	unittest.main()
