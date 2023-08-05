
# CheckboxControl.py::refactored from JJLee's ClientForm
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
# Copyright 2002-2003 John J. Lee <jjl@pobox.com> (BSD License)
# Copyright 1998-2000 Gisle Aas.
#

from ListControl import ListControl

class CheckboxControl(ListControl):
	"""
	Covers:

	INPUT/CHECKBOX

	"""
	def __init__(self, type, name, attrs, select_default=False):
		ListControl.__init__(self, type, name, attrs, select_default,
							 called_as_base_class=True)
		self.__dict__["multiple"] = True
		value = attrs.get("value", "on")
		self._menu = [value]
		checked = attrs.has_key("checked")
		self._selected = [checked]
		self._value_is_set = True

	def fixup(self):
		# If no items were explicitly checked in HTML, that's how we must
		# leave it, so we have nothing to do here.
		assert self._value_is_set


