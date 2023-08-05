
# HTTPCookieProcessor.py::refactored from JJLee's _urllib2_support
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

import os
from BaseProcessor import BaseProcessor
from mechanoid.misc.Common import Common
from mechanoid.cookiejar.CookieJar import CookieJar

class HTTPCookieProcessor(BaseProcessor):
	"""Handle HTTP cookies."""
	def __init__(self, cookies=None):
		if cookies is None:
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

