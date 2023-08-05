
# UserAgent.py::refactored from JJLee's _useragent
# richardharris@operamail.com
# http://cheeseshop.python.org

# Copyright (C) 2004 by Richard Harris
# Released under the GNU General Public License
# (See the included COPYING file)

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.

# You should have received a copy of the GNU General Public License
# with this program; if not, write to the Free Software Foundation,
# Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

# Hack_History:
# 
# Copyright 2004 Richard Harris (mechanoid fork under GNU GPL)
# Copyright 2003 John J. Lee <jjl@pobox.com>  (BSD License)
#

"""
HTTP UserAgent class.

Subclass of urllib2.OpenerDirector. Do not use .add_handler() to add a
handler for something already dealt with by this code.

Public attributes:

addheaders: list of (name, value) pairs specifying headers to send with
every request, unless they are overridden in the Request instance.

>>> ua = UserAgent()
>>> ua.addheaders = [
...	 ("User-agent", "Mozilla/5.0 (compatible)"),
...	 ("From", "jjl@pobox.com")]

"""

import urllib2, httplib
from http_handlers.HTTPHandler import HTTPHandler
from http_handlers.HTTPSHandler import HTTPSHandler
from http_handlers.HTTPRedirectHandler import HTTPRedirectHandler
from mechanoid.misc.OpenerDirector import OpenerDirector
from mechanoid.http_processors.HTTPProcessors import HTTPErrorProcessor, HTTPRequestUpgradeProcessor, \
	 HTTPCookieProcessor, HTTPRefreshProcessor, HTTPRefererProcessor, HTTPEquivProcessor, \
	 SeekableProcessor, HTTPRedirectDebugProcessor, HTTPResponseDebugProcessor

class UserAgent(OpenerDirector):
	handler_classes = {
		# scheme handlers
		"http": HTTPHandler,
		"https": HTTPSHandler,
		"ftp": urllib2.FTPHandler, 
		"file": urllib2.FileHandler,
		"gopher": urllib2.GopherHandler,

		# other handlers
		"_unknown": urllib2.UnknownHandler,
		"_http_error": HTTPErrorProcessor,
		"_http_request_upgrade": HTTPRequestUpgradeProcessor,
		"_http_default_error": urllib2.HTTPDefaultErrorHandler,

		# feature handlers
		"_authen": urllib2.HTTPBasicAuthHandler,
		"_redirect": HTTPRedirectHandler,
		"_cookies": HTTPCookieProcessor,
		"_refresh": HTTPRefreshProcessor,
		"_referer": HTTPRefererProcessor,
		"_equiv": HTTPEquivProcessor,
		"_seek": SeekableProcessor,
		"_proxy": urllib2.ProxyHandler,

		# debug handlers
		"_debug_redirect": HTTPRedirectDebugProcessor,
		"_debug_response_body": HTTPResponseDebugProcessor,
		}

	default_schemes = ["http", "https", "ftp", "file", "gopher"]
	default_others = ["_unknown", "_http_error", "_http_request_upgrade", "_http_default_error"]
	default_features = ["_authen", "_redirect", "_cookies", "_seek", "_proxy"]

	def __init__(self):
		OpenerDirector.__init__(self)
		self._ua_handlers = {}
		for scheme in (self.default_schemes+
					   self.default_others+
					   self.default_features):
			klass = self.handler_classes[scheme]
			self._ua_handlers[scheme] = klass()
		for handler in self._ua_handlers.itervalues():
			self.add_handler(handler)
		return

	#
	# Private Methods
	#

	def __add_referer_header(self, request):
		raise NotImplementedError("HTTP referer headers not implemented")

	def __replace_handler(self, name, newhandler=None):
		# if handler was previously added, remove it
		if name is not None:
			try:
				handler = self._ua_handlers[name]
			except:
				pass
			else:
 				tables = [self.handle_open, self.process_request, self.process_response]
 				tables = tables + self.handle_error.values()
 				for table in tables:
					for handlers in table.values():
						i = 0
						while i < len(handlers):
							if handlers[i] is handler:
								del handlers[i]
							else:
								i += 1
					i = 0 
					while i < len(self.handlers):
						if self.handlers[i] is handler:
							# can't use .remove() because of __cmp__
							del self.handlers[i]
						else:
							i += 1
		if newhandler is not None:	# then add the replacement, if any
			self.add_handler(newhandler)
			self._ua_handlers[name] = newhandler
		return

	def __set_handler(self, name, handle=None, obj=None):
		if handle is None:
			handle = bool(obj)
		handler_class = self.handler_classes[name]
		if handle:
			if obj is not None:
				newhandler = handler_class(obj)
			else:
				newhandler = handler_class()
		else:
			newhandler = None
		self.__replace_handler(name, newhandler)
		return

	#
	# Public Methods
	#

	def close(self):
		"""
		set self and parent to neutral state

		"""
		OpenerDirector.close(self)
		self._ua_handlers = None
		return

	def set_handled_schemes(self, schemes):
		"""
		Set sequence of protocol scheme strings.

		If this fails (with ValueError) because you've passed an unknown
		scheme, the set of handled schemes WILL be updated, but schemes
		in the list that come after the unknown scheme won't be handled.

		"""
		want = {}
		for scheme in schemes:
			if scheme.startswith("_"):
				raise ValueError("invalid scheme '%s'" % scheme)
			want[scheme] = None

		# get rid of scheme handlers we don't want
		for scheme, oldhandler in self._ua_handlers.items():
			if scheme.startswith("_"): continue	 # not a scheme handler
			if scheme not in want:
				self.__replace_handler(scheme, None)
			else:
				del want[scheme]  # already got it

		# add the scheme handlers that are missing
		for scheme in want.keys():
			if scheme not in self.handler_classes:
				raise ValueError("unknown scheme '%s'")
			self.__set_handler(scheme, True)
		return	

	def set_cookiejar(self, cookiejar):
		"""
		Set a mechanoid.cookiejar.CookieJar, or None.

		"""
		self.__set_handler("_cookies", obj=cookiejar)
		return
	
	def set_credentials(self, credentials):
		"""
		Set a urllib2.HTTPPasswordMgr, or None.

		"""
		self.__set_handler("_authen", obj=credentials)
		return

	def set_seekable_responses(self, handle):
		"""
		Make response objects .seek()able.

		"""
		self.__set_handler("_seek", handle)
		return

	#
	# handle methods all take a boolean parameter
	#

	def set_handle_redirect(self, handle):
		"""
		Set whether to handle HTTP Refresh headers.

		"""
		self.__set_handler("_redirect", handle)
		return

	def set_handle_refresh(self, handle):
		"""
		Set whether to handle HTTP Refresh headers.

		"""
		self.__set_handler("_refresh", handle)
		return

	def set_handle_equiv(self, handle):
		"""
		Set whether to treat HTML http-equiv headers like HTTP headers.
		Response objects will be .seek()able if this is set.

		"""
		self.__set_handler("_equiv", handle)
		return

	def set_handle_referer(self, handle):
		"""
		Set whether to add Referer header to each request.

		This base class does not implement this feature; so don't turn
		this on if you're using this base class directly.  But the
		subclass mechanize.Browser does implement referers.

		"""
		self.__set_handler("_referer", handle)
		self.handle_referer = handle
		return

	#
	# debug methods make operation verbose
	#
	
	def set_debug_redirects(self, handle):
		"""
		Print information about HTTP redirects.

		This includes refreshes, which show up as faked 302 redirections
		at the moment.

		"""
		self.__set_handler("_debug_redirect", handle)
		return

	def set_debug_responses(self, handle):
		"""
		Print HTTP response bodies.

		"""
		self.__set_handler("_debug_response_body", handle)
		return

	def set_debug_http(self, handle):
		"""
		Print HTTP headers.

		"""
		level = int(bool(handle))
		for scheme in "http", "https":
			h = self._ua_handlers.get(scheme)
			if h is not None:
				h.set_http_debuglevel(level)
		return
