
# HTTPRefererProcessor.py::refactored from JJLee's _urllib2_support
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

from BaseProcessor import BaseProcessor

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
		if ((self.referer is not None) and not request.has_header("Referer")):
			request.add_unredirected_header("Referer", self.referer)
		return request

	def http_response(self, request, response):
		self.referer = response.geturl()
		return response

	https_request = http_request
	https_response = http_response

