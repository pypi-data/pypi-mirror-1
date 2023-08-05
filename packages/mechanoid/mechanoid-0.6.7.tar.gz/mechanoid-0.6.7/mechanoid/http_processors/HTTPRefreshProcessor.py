
# HTTPRefreshProcessor.py::refactored from JJLee's _urllib2_support
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
from mechanoid.misc.Common import Common

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
			i = refresh.find(";")
			if i != -1:
				pause, newurl_spec = refresh[:i], refresh[i+1:]
				i = newurl_spec.find("=")
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

