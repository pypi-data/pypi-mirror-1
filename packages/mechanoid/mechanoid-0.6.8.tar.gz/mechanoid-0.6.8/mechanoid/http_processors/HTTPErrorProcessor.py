
# HTTPErrorProcessor.py::refactored from JJLee's _urllib2_support
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

