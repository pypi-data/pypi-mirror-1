
# HTTPEquivProcessor.py::refactored from JJLee's _urllib2_support
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
from HeadParser import HeadParser
from mechanoid.misc.Errors import EndOfHeadError
from mechanoid.seek_wrapper.Response_Seek_Wrapper import Response_Seek_Wrapper

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


