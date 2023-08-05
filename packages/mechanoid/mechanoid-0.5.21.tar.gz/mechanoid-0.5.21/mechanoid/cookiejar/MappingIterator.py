
# cookiejar.MappingIterator.py::refactored from JJLee's ClientCookie
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
# Copyright 2002-2003 John J Lee <jjl@pobox.com>
# Copyright 1997-1999 Gisle Aas (original libwww-perl code)
# Copyright 2002-2003 Johnny Lee (original MSIE Perl code)
#

from exceptions import StopIteration

class MappingIterator:
	"""Iterates over nested mapping, depth-first, in sorted order by key."""
	def __init__(self, mapping):
		self._s = [(self.vals_sorted_by_key(mapping), 0, None)]	 # LIFO stack

	def __iter__(self): return self

	def next(self):
		# this is hairy because of lack of generators
		while 1:
			try:
				vals, i, prev_item = self._s.pop()
			except IndexError:
				raise StopIteration()
			if i < len(vals):
				item = vals[i]
				i = i + 1
				self._s.append((vals, i, prev_item))
				try:
					item.items
				except AttributeError:
					# non-mapping
					break
				else:
					# mapping
					self._s.append((self.vals_sorted_by_key(item), 0, item))
					continue
		return item

	def vals_sorted_by_key(self, adict):
		keys = adict.keys()
		keys.sort()
		return map(adict.get, keys)
