
# MapBase.py::refactored from JJLee's ClientForm
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
# Copyright 2002-2003 John J. Lee <jjl@pobox.com>  (BSD License)
# Copyright 1998-2000 Gisle Aas.
#

import copy, string
from types import TupleType

class MapBase:
	"""
	Mapping designed to be easily derived from.  This is essentially the
	same as UserDict.DictMixin.  I wrote this before that, and DictMixin
	isn't available in 1.5.2 anyway.

	Subclass it and override __init__, __setitem__, __getitem__,
	__delitem__ and keys.  Nothing else should need to be overridden,
	unlike UserDict.  This significantly simplifies dictionary-like
	classes.

	Also different from UserDict in that it has a readonly flag, and can
	be updated (and initialised) with a sequence of pairs (key, value).

	"""
	def __init__(self, init=None):
		self._data = {}
		self.readonly = False
		if init is not None: self.update(init)

	def __cmp__(self, dict):
		# note: return value is *not* boolean
		for k, v in self.items():
			if not (dict.has_key(k) and dict[k] == v):
				return 1  # different
		return 0  # the same

	def __delitem__(self, key):
		if not self.readonly:
			del self._data[key]
		else:
			raise TypeError("Object doesn't support item deletion")

	def __getitem__(self, key):
		return self._data[key]

	def __len__(self):
		return len(self.keys())

	def __repr__(self):
		rep = []
		for k, v in self.items():
			rep.append("%s: %s" % (repr(k), repr(v)))
		return self.__class__.__name__+"{"+(string.join(rep, ", "))+"}"

	def __setitem__(self, key, item):
		if not self.readonly:
			self._data[key] = item
		else:
			raise TypeError("Object doesn't support item assignment")

	#
	# Private Methods
	#

	def __issequence(self, x):
		try:
			x[0]
		except (TypeError, KeyError):
			return False
		except IndexError:
			pass
		return True

	def __isstringlike(self, x):
		try:
			x+""
		except:
			return False
		return True
	
	#
	# Public Methods
	#

	def clear(self):
		for k in self.keys():
			del self[k]

	def copy(self):
		return copy.copy(self)

	def get(self, key, failobj=None):
		if key in self.keys():
			return self[key]
		else:
			return failobj

	def has_key(self, key):
		return key in self.keys()

	def items(self):
		keys = self.keys()
		vals = self.values()
		r = []
		for i in len(self):
			r.append((keys[i], vals[i]))
		return r

	def keys(self):
		return self._data.keys()

	def setdefault(self, key, failobj=None):
		if not self.has_key(key):
			self[key] = failobj
		return self[key]

	def update(self, map):
		if self.__issequence(map) and not self.__isstringlike(map):
			items = map
		else:
			items = map.items()
		for tup in items:
			if not isinstance(tup, TupleType):
				raise TypeError(
					"MapBase.update requires a map or a sequence of pairs")
			k, v = tup
			self[k] = v

	def values(self):
		r = []
		for k in self.keys():
			r.append(self[k])
		return r


