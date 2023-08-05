
# SubmitControl.py::refactored from JJLee's ClientForm
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
# Copyright 2002-2003 John J. Lee <jjl@pobox.com> (BSD License)
# Copyright 1998-2000 Gisle Aas.
#

from ScalarControl import ScalarControl

class SubmitControl(ScalarControl):
	"""
	Covers:

	INPUT/SUBMIT
	BUTTON/SUBMIT

	"""
	def __init__(self, type, name, attrs):
		ScalarControl.__init__(self, type, name, attrs)
		# IE5 defaults SUBMIT value to "Submit Query"; Firebird 0.6 leaves it
		# blank, Konqueror 3.1 defaults to "Submit".  HTML spec. doesn't seem
		# to define this.
		if self.value is None: self.value = ""
		self.readonly = True

	def is_of_kind(self, kind): return kind == "clickable"

	def _click(self, form, coord, return_type):
		self._clicked = coord
		r = form.switch_click(return_type)
		self._clicked = False
		return r

	def pairs(self):
		if not self._clicked:
			return []
		return ScalarControl.pairs(self)

