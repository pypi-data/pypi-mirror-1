
# Request.py::refactored from JJLee's _urllib2_support
# truenolejano@yahoo.com
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

import string, urllib2

class Request(urllib2.Request):
	def __init__(self, url, data=None, headers={}):
		urllib2.Request.__init__(self, url, data, headers)
		self.unredirected_hdrs = {}

	def add_unredirected_header(self, key, val):
		"""
		Add a header that will not be added to a redirected request.

		"""
		self.unredirected_hdrs[string.capitalize(key)] = val

	def has_header(self, header_name):
		"""
		True iff request has named header (regular or unredirected).

		"""
		if (self.headers.has_key(header_name) or
			self.unredirected_hdrs.has_key(header_name)):
			return True
		return False

	def get_header(self, header_name, default=None):
		return self.headers.get(
			header_name,
			self.unredirected_hdrs.get(header_name, default))

	def iter_headers(self):
		hdrs = self.unredirected_hdrs.copy()
		hdrs.update(self.headers)
		return hdrs.items()

