
# IgnoreControl.py::refactored from JJLee's ClientForm
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

from ScalarControl import ScalarControl

class IgnoreControl(ScalarControl):
	"""Control that we're not interested in.

	Covers:

	INPUT/RESET
	BUTTON/RESET
	INPUT/BUTTON
	BUTTON/BUTTON

	These controls are always unsuccessful, in the terminology of HTML 4 (ie.
	they never require any information to be returned to the server).

	BUTTON/BUTTON is used to generate events for script embedded in HTML.

	The value attribute of IgnoreControl is always None.

	"""
	def __init__(self, type, name, attrs):
		ScalarControl.__init__(self, type, name, attrs)
		self._value = None

	def is_of_kind(self, kind): return False

	def __setattr__(self, name, value):
		if name == "value":
			raise AttributeError(
				"control '%s' is ignored, hence read-only" % self.name)
		elif name in ("name", "type"):
			raise AttributeError("%s attribute is readonly" % name)
		else:
			self.__dict__[name] = value


