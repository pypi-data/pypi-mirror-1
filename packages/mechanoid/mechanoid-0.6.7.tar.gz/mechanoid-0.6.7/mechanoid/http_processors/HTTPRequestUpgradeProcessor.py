
# HTTPRequestUpgradeProcessor.py::refactored from JJLee's _urllib2_support
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

from mechanoid.misc.Request import Request
from BaseProcessor import BaseProcessor

class HTTPRequestUpgradeProcessor(BaseProcessor):

	processor_order = 0	 # before anything else

	def http_request(self, request):
		# upgrade Request to one w/support for headers that don't get redirected
		if not hasattr(request, "add_unredirected_header"):
			newrequest = Request(request._Request__original,
								 request.data, request.headers)
			try:
				newrequest.origin_req_host = request.origin_req_host
			except AttributeError:
				pass
			try:
				newrequest.unverifiable = request.unverifiable
			except AttributeError:
				pass
			request = newrequest
		return request

	https_request = http_request


