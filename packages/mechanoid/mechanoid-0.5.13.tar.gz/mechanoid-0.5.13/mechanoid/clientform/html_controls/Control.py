
# Control.py::refactored from JJLee's ClientForm
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

class Control:
	"""An HTML form control.

	An HTMLForm contains a sequence of Controls.  HTMLForm delegates lots of
	things to Control objects, and most of Control's methods are, in effect,
	documented by the HTMLForm docstrings.

	The Controls in an HTMLForm can be got at via the HTMLForm.find_control
	method or the HTMLForm.controls attribute.

	Control instances are usually constructed using the ParseFile /
	ParseResponse functions, so you can probably ignore the rest of this
	paragraph.	A Control is only properly initialised after the fixup method
	has been called.  In fact, this is only strictly necessary for ListControl
	instances.	This is necessary because ListControls are built up from
	ListControls each containing only a single item, and their initial value(s)
	can only be known after the sequence is complete.

	The types and values that are acceptable for assignment to the value
	attribute are defined by subclasses.

	If the disabled attribute is true, this represents the state typically
	represented by browsers by `greying out' a control.	 If the disabled
	attribute is true, the Control will raise AttributeError if an attempt is
	made to change its value.  In addition, the control will not be considered
	`successful' as defined by the W3C HTML 4 standard -- ie. it will
	contribute no data to the return value of the HTMLForm.click* methods.	To
	enable a control, set the disabled attribute to a false value.

	If the readonly attribute is true, the Control will raise AttributeError if
	an attempt is made to change its value.	 To make a control writable, set
	the readonly attribute to a false value.

	All controls have the disabled and readonly attributes, not only those that
	may have the HTML attributes of the same names.

	On assignment to the value attribute, the following exceptions are raised:
	TypeError, AttributeError (if the value attribute should not be assigned
	to, because the control is disabled, for example) and ValueError.

	If the name or value attributes are None, or the value is an empty list, or
	if the control is disabled, the control is not successful.

	Public attributes:

	type: string describing type of control (see the keys of the
	 HTMLForm.type2class dictionary for the allowable values) (readonly)
	name: name of control (readonly)
	value: current value of control (subclasses may allow a single value, a
	 sequence of values, or either)
	disabled: disabled state
	readonly: readonly state
	id: value of id HTML attribute

	"""
	def __init__(self, type, name, attrs):
		"""
		type: string describing type of control (see the keys of the
		 HTMLForm.type2class dictionary for the allowable values)
		name: control name
		attrs: HTML attributes of control's HTML element

		"""
		raise NotImplementedError()

	def add_to_form(self, form):
		form.controls.append(self)

	def fixup(self):
		pass

	def is_of_kind(self, kind):
		raise NotImplementedError()

	def __getattr__(self, name): raise NotImplementedError()
	def __setattr__(self, name, value): raise NotImplementedError()

	def pairs(self):
		"""Return list of (key, value) pairs suitable for passing to urlencode.
		"""
		raise NotImplementedError()

	def _write_mime_data(self, mw):
		"""Write data for this control to a MimeWriter."""
		# called by HTMLForm
		for name, value in self.pairs():
			mw2 = mw.nextpart()
			mw2.addheader("Content-disposition",
						  'form-data; name="%s"' % name, 1)
			f = mw2.startbody(prefix=0)
			f.write(value)

	def __str__(self):
		raise NotImplementedError()


