
# SelectControl.py::refactored from JJLee's ClientForm
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

import copy
from alist.AList import AList
from mechanoid.misc.Errors import ItemNotFoundError
from mechanoid.misc.Common import Common
from ListControl import ListControl

class SelectControl(ListControl):
	"""
	Covers:

	SELECT (and OPTION)

	SELECT control values and labels are subject to some messy defaulting
	rules.	For example, if the HTML repreentation of the control is:

	<SELECT name=year>
	  <OPTION value=0 label="2002">current year</OPTION>
	  <OPTION value=1>2001</OPTION>
	  <OPTION>2000</OPTION>
	</SELECT>

	The items, in order, have labels "2002", "2001" and "2000", whereas their
	values are "0", "1" and "2000" respectively.  Note that the value of the
	last OPTION in this example defaults to its contents, as specified by RFC
	1866, as do the labels of the second and third OPTIONs.

	The OPTION labels are sometimes more meaningful than the OPTION values,
	which can make for more maintainable code.

	Additional read-only public attribute: attrs

	The attrs attribute is a dictionary of the original HTML attributes of the
	SELECT element.	 Other ListControls do not have this attribute, because in
	other cases the control as a whole does not correspond to any single HTML
	element.  The get_item_attrs method may be used as usual to get at the
	HTML attributes of the HTML elements corresponding to individual list items
	(for SELECT controls, these are OPTION elements).

	Another special case is that the attributes dictionaries returned by
	get_item_attrs have a special key "contents" which does not correspond to
	any real HTML attribute, but rather contains the contents of the OPTION
	element:

	<OPTION>this bit</OPTION>

	"""
	# HTML attributes here are treated slightly from other list controls:
	# -The SELECT HTML attributes dictionary is stuffed into the OPTION
	#  HTML attributes dictionary under the "__select" key.
	# -The content of each OPTION element is stored under the special
	#  "contents" key of the dictionary.
	# After all this, the dictionary is passed to the SelectControl constructor
	# as the attrs argument, as usual.	However:
	# -The first SelectControl constructed when building up a SELECT control
	#  has a constructor attrs argument containing only the __select key -- so
	#  this SelectControl represents an empty SELECT control.
	# -Subsequent SelectControls have both OPTION HTML-attribute in attrs and
	#  the __select dictionary containing the SELECT HTML-attributes.
	def __init__(self, type, name, attrs, select_default=False):
		# fish out the SELECT HTML attributes from the OPTION HTML attributes
		# dictionary
		self.attrs = attrs["__select"].copy()
		attrs = attrs.copy()
		del attrs["__select"]

		ListControl.__init__(self, type, name, attrs, select_default,
							 called_as_base_class=True)

		self._label_map = None
		self.disabled = self.attrs.has_key("disabled")
		self.id = self.attrs.get("id")

		self._menu = []
		self._selected = []
		self._value_is_set = False
		if self.attrs.has_key("multiple"):
			self.__dict__["multiple"] = True
			self._selected = []
		else:
			self.__dict__["multiple"] = False
			self._selected = None

		if attrs:  # OPTION item data was provided
			value = attrs["value"]
			self._menu.append(value)
			selected = attrs.has_key("selected")
			if selected:
				self._value_is_set = True
			if self.attrs.has_key("multiple"):
				self._selected.append(selected)
			elif selected:
				self._selected = value
		self.common = Common()

	def _build_select_label_map(self):
		"""Return an ordered mapping of labels to values.

		For example, if the HTML repreentation of the control is as given in
		SelectControl.__doc__,	this function will return a mapping like:

		{"2002": "0", "2001": "1", "2000": "2000"}

		"""
		alist = []
		for val in self._menu:
			attrs = self.get_item_attrs(val)
			alist.append((attrs["label"], val))
		return AList(alist)

	def _value_from_label(self, label):
		try:
			return self._label_map[label]
		except KeyError:
			raise ItemNotFoundError("no item has label '%s'" % label)

	def fixup(self):
		if not self._value_is_set:
			# No item explicitly selected.
			if len(self._menu) > 0:
				if self.multiple:
					if self._select_default:
						self._selected[0] = True
				else:
					assert self._selected is None
					self._selected = self._menu[0]
			self._value_is_set = True
		self._label_map = self._build_select_label_map()

	def _delete_items(self):
		# useful for simulating JavaScript code, but not a stable interface yet
		self._menu = []
		self._value_is_set = False
		if self.multiple:
			self._selected = []
		else:
			self._selected = None

	def possible_items(self, by_label=False):
		if not by_label:
			return copy.copy(self._menu)
		else:
			self._label_map.set_inverted(True)
			try:
				r = map(lambda v, self=self: self._label_map[v], self._menu)
			finally:
				self._label_map.set_inverted(False)
			return r

	def set_value_by_label(self, value):
		if self.common.isstringlike(value):
			raise TypeError("ListControl, must set a sequence, not a string")
		if self.disabled:
			raise AttributeError("control '%s' is disabled" % self.name)
		if self.readonly:
			raise AttributeError("control '%s' is readonly" % self.name)

		try:
			value = map(lambda v, self=self: self._label_map[v], value)
		except KeyError, e:
			raise ItemNotFoundError("no item has label '%s'" % e.args[0])
		self._set_value(value)

	def get_value_by_label(self):
		menu = self._menu
		self._label_map.set_inverted(True)
		try:
			if self.multiple:
				values = []
				for i in range(len(menu)):
					if self._selected[i]:
						values.append(self._label_map[menu[i]])
				return values
			else:
				return [self._label_map[self._selected]]
		finally:
			self._label_map.set_inverted(False)


