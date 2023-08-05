
# ScalarControl.py::refactored from JJLee's ClientForm
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
# Copyright 2002-2003 John J. Lee <jjl@pobox.com> (BSD License)
# Copyright 1998-2000 Gisle Aas.
#

import string
from mechanoid.misc.Common import Common
from Control import Control

class ScalarControl(Control):
	"""Control whose value is not restricted to one of a prescribed set.

	Some ScalarControls don't accept any value attribute.  Otherwise, takes a
	single value, which must be string-like.

	Additional read-only public attribute:

	attrs: dictionary mapping the names of original HTML attributes of the
	 control to their values

	"""
	def __init__(self, type, name, attrs):
		self.__dict__["type"] = string.lower(type)
		self.__dict__["name"] = name
		self._value = attrs.get("value")
		self.disabled = attrs.has_key("disabled")
		self.readonly = attrs.has_key("readonly")
		self.id = attrs.get("id")
		self.attrs = attrs.copy()
		self._clicked = False
		self.common = Common()

	def __getattr__(self, name):
		if name == "value":
			return self.__dict__["_value"]
		else:
			raise AttributeError("%s instance has no attribute '%s'" %
								 (self.__class__.__name__, name))

	def __setattr__(self, name, value):
		if name == "value":
			if not self.common.isstringlike(value):
				raise TypeError("must assign a string")
			elif self.readonly:
				raise AttributeError("control '%s' is readonly" % self.name)
			elif self.disabled:
				raise AttributeError("control '%s' is disabled" % self.name)
			self.__dict__["_value"] = value
		elif name in ("name", "type"):
			raise AttributeError("%s attribute is readonly" % name)
		else:
			self.__dict__[name] = value

	def pairs(self):
		name = self.name
		value = self.value
		if name is None or value is None or self.disabled:
			return []
		return [(name, value)]

	def __str__(self):
		name = self.name
		value = self.value
		if name is None: name = "<None>"
		if value is None: value = "<None>"

		infos = []
		if self.disabled: infos.append("disabled")
		if self.readonly: infos.append("readonly")
		info = string.join(infos, ", ")
		if info: info = " (%s)" % info

		return "<%s(%s=%s)%s>" % (self.__class__.__name__, name, value, info)

