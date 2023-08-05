
# AList.py::refactored from JJLee's ClientForm
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
# Copyright 2002-2003 John J. Lee <jjl@pobox.com>  (BSD License)
# Copyright 1998-2000 Gisle Aas.
#

import copy, string
from types import TupleType
from MapBase import MapBase

class AList(MapBase):
	"""
	Read-only ordered mapping.

	"""
	def __init__(self, seq=[]):
		self.readonly = True
		self._inverted = False
		self._data = list(seq[:])
		self._keys = []
		self._values = []
		for key, value in seq:
			self._keys.append(key)
			self._values.append(value)

	def __getitem__(self, key):
		try:
			i = self._keys.index(key)
		except ValueError:
			raise KeyError(key)
		return self._values[i]

	def __delitem__(self, key):
		try:
			i = self._keys.index[key]
		except ValueError:
			raise KeyError(key)
		del self._values[i]

	#
	# Public Methods
	#

	def items(self):
		data = self._data[:]
		if not self._inverted:
			return data
		else:
			newdata = []
			for k, v in data:
				newdata.append((v, k))
			return newdata

	def keys(self): return list(self._keys[:])

	def set_inverted(self, inverted):
		if (inverted and not self._inverted) or (
			not inverted and self._inverted):
			self._keys, self._values = self._values, self._keys
		if inverted: self._inverted = True
		else: self._inverted = False

	def values(self): return list(self._values[:])

