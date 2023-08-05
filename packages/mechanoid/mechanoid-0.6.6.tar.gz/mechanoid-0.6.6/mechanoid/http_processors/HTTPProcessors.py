
# HTTPProcessors.py::refactored from JJLee's _urllib2_support
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
# Copyright 2002-2003 John J. Lee <jjl@pobox.com>
#

import urllib2, cStringIO, string, time, robotparser, os
from mechanoid.misc.Common import Common
from mechanoid.misc.Errors import EndOfHeadError
from mechanoid.cookiejar.CookieJar import CookieJar
from HeadParser import HeadParser
from mechanoid.misc.Request import Request
from mechanoid.seek_wrapper.Response_Seek_Wrapper import Response_Seek_Wrapper

class BaseProcessor:
	processor_order = 500

	def add_parent(self, parent):
		self.parent = parent
	def close(self):
		self.parent = None
	def __cmp__(self, other):
		if not hasattr(other, "processor_order"):
			return 0
		return cmp(self.processor_order, other.processor_order)

class HTTPRequestUpgradeProcessor(BaseProcessor):
	# upgrade Request to class with support for headers that don't get
	# redirected
	processor_order = 0	 # before anything else

	def http_request(self, request):
		if not hasattr(request, "add_unredirected_header"):
			newrequest = Request(request._Request__original, request.data,
							  request.headers)
			# yuck
			try: newrequest.origin_req_host = request.origin_req_host
			except AttributeError: pass
			try: newrequest.unverifiable = request.unverifiable
			except AttributeError: pass
			request = newrequest
		return request

	https_request = http_request

class HTTPEquivProcessor(BaseProcessor):
	"""Append META HTTP-EQUIV headers to regular HTTP headers."""
	def __init__(self):
		return

	def parse_head(self, fileobj):
		"""Return a list of key, value pairs."""
		hp = HeadParser()
		data = fileobj.read()
		try:
			hp.feed(data)
		except EndOfHeadError:
			pass
		return hp.http_equiv
	
	def http_response(self, request, response):
		if not hasattr(response, "seek"):
			response = Response_Seek_Wrapper(response)
		# grab HTTP-EQUIV headers and add them to the true HTTP headers
		headers = response.info()
		for hdr, val in self.parse_head(response):
			headers[hdr] = val
		response.seek(0)
		return response

	https_response = http_response

# XXX ATM this only takes notice of http responses -- probably
#	should be independent of protocol scheme (http, ftp, etc.)
class SeekableProcessor(BaseProcessor):
	"""Make responses seekable."""

	def http_response(self, request, response):
		if not hasattr(response, "seek"):
			return Response_Seek_Wrapper(response)
		return response

	https_response = http_response

# XXX if this gets added to urllib2, unverifiable would end up as an
#	attribute / method on Request.
class HTTPCookieProcessor(BaseProcessor):
	"""Handle HTTP cookies."""
	def __init__(self, cookies=None):
		if cookies is None:
##			cookies = CookieJar()
			cookies = CookieJar(os.path.expandvars("$HOME/.mechcookies"))
			cookies.load()
		self.cookies = cookies
		self.common = Common()

	def _unverifiable(self, request):
		if hasattr(request, "redirect_dict") and request.redirect_dict:
			redirect = True
		else:
			redirect = False
		if (redirect or
			(hasattr(request, "unverifiable") and request.unverifiable)):
			unverifiable = True
		else:
			unverifiable = False
		return unverifiable

	def http_request(self, request):
		unverifiable = self._unverifiable(request)
		if not unverifiable:
			# Stuff request-host of this origin transaction into Request
			# object, because we need to know it to know whether cookies
			# should be in operation during derived requests (redirects,
			# specifically -- including refreshes).
			request.origin_req_host = self.common.request_host(request)
		self.cookies.add_cookie_header(request, unverifiable)
		return request

	def http_response(self, request, response): 
		unverifiable = self._unverifiable(request)
		self.cookies.extract_cookies(response, request, unverifiable)
		return response

	https_request = http_request
	https_response = http_response

class RobotExclusionError(urllib2.HTTPError):
	def __init__(self, request, *args):
		apply(urllib2.HTTPError.__init__, (self,)+args)
		self.request = request


class HTTPRefererProcessor(BaseProcessor):
	"""Add Referer header to requests.
	
	This only makes sense if you use each RefererProcessor for a single
	chain of requests only (so, for example, if you use a single
	HTTPRefererProcessor to fetch a series of URLs extracted from a single
	page, this will break).
	
	"""
	def __init__(self):
		self.referer = None

	def http_request(self, request):
		if ((self.referer is not None) and
			not request.has_header("Referer")):
			request.add_unredirected_header("Referer", self.referer)
		return request

	def http_response(self, request, response):
		self.referer = response.geturl()
		return response

	https_request = http_request
	https_response = http_response

class HTTPResponseDebugProcessor(BaseProcessor):
	processor_order = 900  # before redirections, after everything else

	def http_response(self, request, response):
		if not hasattr(response, "seek"):
			response = Response_Seek_Wrapper(response)
		response.seek(0)
		return response

	https_response = http_response

class HTTPRedirectDebugProcessor(BaseProcessor):
	def http_request(self, request):
		if hasattr(request, "redirect_dict"):
			print ("redirecting to %s", request.get_full_url())
		return request

class HTTPRefreshProcessor(BaseProcessor):
	"""Perform HTTP Refresh redirections.

	Note that if a non-200 HTTP code has occurred (for example, a 30x
	redirect), this processor will do nothing.

	By default, only zero-time Refresh headers are redirected.	Use the
	max_time constructor argument to allow Refresh with longer pauses.	Use
	the honor_time argument to control whether the requested pause is
	honoured (with a time.sleep()) or skipped in favour of immediate
	redirection.

	"""
	processor_order = 1000

	def __init__(self, max_time=0, honor_time=True):
		self.max_time = max_time
		self.honor_time = honor_time
		self.common = Common()

	def http_response(self, request, response):
		code, msg, hdrs = response.code, response.msg, response.info()

		if code == 200 and hdrs.has_key("refresh"):
			refresh = self.common.getheaders(hdrs, "refresh")[0]
			i = string.find(refresh, ";")
			if i != -1:
				pause, newurl_spec = refresh[:i], refresh[i+1:]
				i = string.find(newurl_spec, "=")
				if i != -1:
					pause = int(pause)
					if (self.max_time is None) or (pause <= self.max_time):
						if pause != 0 and self.honor_time:
							time.sleep(pause)
						newurl = newurl_spec[i+1:]
						hdrs["location"] = newurl
						response = self.parent.error(
							'http', request, response,
							"refresh", msg, hdrs)

		return response

	https_response = http_response

class HTTPErrorProcessor(BaseProcessor):
	"""Process HTTP error responses.

	The purpose of this handler is to to allow other response processors a
	look-in by removing the call to parent.error() from
	AbstractHTTPHandler.

	For non-200 error codes, this just passes the job on to the
	Handler.<proto>_error_<code> methods, via the OpenerDirector.error
	method.	 Eventually, urllib2.HTTPDefaultErrorHandler will raise an
	HTTPError if no other handler handles the error.

	"""
	processor_order = 1000	# after all other processors

	def http_response(self, request, response):
		code, msg, hdrs = response.code, response.msg, response.info()

		if code != 200:
			response = self.parent.error(
				'http', request, response, code, msg, hdrs)

		return response

	https_response = http_response

