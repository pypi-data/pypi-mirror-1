
# HTTPRedirectHandler.py::refactored from JJLee's _urllib2_support
# goosequill@users.sourceforge.net
# http://goosequill.sourceforge.net

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
"""
	Implementation notes:

	To avoid the server sending us into an infinite loop, the request
	object needs to track what URLs we have already seen.  Do this by
	adding a handler-specific attribute to the Request object.  The
	value of the dict is used to count the number of times the same url
	has been visited.  This is needed because this isn't necessarily a
	loop: there is more than one way to redirect (Refresh, 302, 303,
	307).

	Another handler-specific Request attribute, original_url, is used to
	remember the URL of the original request so that it is possible to
	decide whether or not RFC 2965 cookies should be turned on during
	redirect.

	Always unhandled redirection codes:
	  300 Multiple Choices: should not handle this here.
	  304 Not Modified: no need to handle here: only of interest to caches
		  that do conditional GETs
	  305 Use Proxy: probably not worth dealing with here
	  306 Unused: what was this for in the previous versions of protocol??

"""

import string, urllib, urllib2, urlparse
from mechanoid.misc.Request import Request
from mechanoid.misc.Common import Common

class HTTPRedirectHandler(urllib2.BaseHandler):
	# maximum number of redirections to any single URL
	# this is needed because of the state that cookies introduce
	max_repeats = 4
	# maximum total number of redirections (regardless of URL) before
	# assuming we're in a loop
	max_redirections = 10

	def __init__(self):
		self.common = Common()
		return

	def redirect_request(self, newurl, req, fp, code, msg, headers):
		"""
		Return a Request or None in response to a redirect.

		This is called by the http_error_30x methods when a redirection
		response is received.  If a redirection should take place,
		return a new Request to allow http_error_30x to perform the
		redirect; otherwise, return None to indicate that an
		urllib2.HTTPError should be raised.

		Strictly (according to RFC 2616), 301 or 302 in response to a
		POST MUST NOT cause a redirection without confirmation from the
		user (of urllib2, in this case).  In practice, essentially all
		clients do redirect in this case, so we do the same.

		"""
		if ((code in (301, 302, 303, "refresh")) or 
			(code == 307 and not req.has_data())):
			return Request(newurl, headers=req.headers)
		else:
			raise urllib2.HTTPError(req.get_full_url(), code, msg, headers, fp)

	def http_error_302(self, req, fp, code, msg, headers):
		if headers.has_key('location'):
			newurl = self.common.getheaders(headers, 'location')[0]
		elif headers.has_key('uri'):
			newurl = self.common.getheaders(headers, 'uri')[0]
		else:
			return
		newurl = urlparse.urljoin(req.get_full_url(), newurl)

		# XXX Probably want to forget about the state of the current
		# request, although that might interact poorly with other
		# handlers that also use handler-specific request attributes
		new = self.redirect_request(newurl, req, fp, code, msg, headers)
		if new is None:
			return

		# remember where we started from
		try:
			new.origin_req_host = req.origin_req_host
		except AttributeError:
			pass

		# loop detection
		# .redirect_dict has a key url if url was previously visited.
		if hasattr(req, 'redirect_dict'):
			visited = new.redirect_dict = req.redirect_dict
			if (visited.get(newurl, 0) >= self.max_repeats or
				len(visited) >= self.max_redirections):
				raise urllib2.HTTPError(req.get_full_url(), code,
								self.inf_msg + msg, headers, fp)
		else:
			visited = new.redirect_dict = req.redirect_dict = {}
		visited[newurl] = visited.get(newurl, 0) + 1

		# Don't close the fp until we are sure that we won't use it
		# with urllib2.HTTPError.  
		fp.read()
		fp.close()
		return self.parent.open(new)

	http_error_301 = http_error_303 = http_error_307 = http_error_302
	http_error_refresh = http_error_302

	inf_msg = """
	The HTTP server returned a redirect error that would lead
	to an infinite loop. The last 30x error message was:
	"""
