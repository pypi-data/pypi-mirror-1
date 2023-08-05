
# ListControl.py::refactored from JJLee's ClientForm
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

import string, copy
from mechanoid.misc.Errors import ControlNotFoundError, ItemNotFoundError, ItemCountError
from mechanoid.misc.Common import Common
from Control import Control

class ListControl(Control):
	"""Control representing a sequence of items.

	The value attribute of a ListControl represents the selected list items in
	the control.

	ListControl implements both list controls that take a single value and
	those that take multiple values.

	ListControls accept sequence values only.  Some controls only accept
	sequences of length 0 or 1 (RADIO, and single-selection SELECT).
	In those cases, ItemCountError is raised if len(sequence) > 1.	CHECKBOXes
	and multiple-selection SELECTs (those having the "multiple" HTML attribute)
	accept sequences of any length.

	Note the following mistake:

	control.value = some_value
	assert control.value == some_value	  # not necessarily true

	The reason for this is that the value attribute always gives the list items
	in the order they were listed in the HTML.

	ListControl items can also be referred to by their labels instead of names.
	Use the by_label argument, and the set_value_by_label, get_value_by_label
	methods.

	XXX RadioControl and CheckboxControl don't implement by_label yet.

	Note that, rather confusingly, though SELECT controls are represented in
	HTML by SELECT elements (which contain OPTION elements, representing
	individual list items), CHECKBOXes and RADIOs are not represented by *any*
	element.  Instead, those controls are represented by a collection of INPUT
	elements.  For example, this is a SELECT control, named "control1":

	<select name="control1">
	 <option>foo</option>
	 <option value="1">bar</option>
	</select>

	and this is a CHECKBOX control, named "control2":

	<input type="checkbox" name="control2" value="foo" id="cbe1">
	<input type="checkbox" name="control2" value="bar" id="cbe2">

	The id attribute of a CHECKBOX or RADIO ListControl is always that of its
	first element (for example, "cbe1" above).


	Additional read-only public attribute: multiple.

	"""

	# ListControls are built up by the parser from their component items by
	# creating one ListControl per item, consolidating them into a single
	# master ListControl held by the HTMLForm:

	# -User calls form.new_control(...)
	# -Form creates Control, and calls control.add_to_form(self).
	# -Control looks for a Control with the same name and type in the form,
	#  and if it finds one, merges itself with that control by calling
	#  control.merge_control(self).	 The first Control added to the form, of
	#  a particular name and type, is the only one that survives in the
	#  form.
	# -Form calls control.fixup for all its controls.  ListControls in the
	#  form know they can now safely pick their default values.

	# To create a ListControl without an HTMLForm, use:

	# control.merge_control(new_control)

	# (actually, it's much easier just to use ParseFile)

	def __init__(self, type, name, attrs={}, select_default=False,
				 called_as_base_class=False):
		"""
		select_default: for RADIO and multiple-selection SELECT controls, pick
		 the first item as the default if no 'selected' HTML attribute is
		 present

		"""
		if not called_as_base_class:
			raise NotImplementedError()

		self.__dict__["type"] = string.lower(type)
		self.__dict__["name"] = name
		self._value = attrs.get("value")
		self.disabled = False
		self.readonly = False
		self.id = attrs.get("id")

		self._attrs = attrs.copy()
		# As Controls are merged in with .merge_control(), self._attrs will
		# refer to each Control in turn -- always the most recently merged
		# control.	Each merged-in Control instance corresponds to a single
		# list item: see ListControl.__doc__.
		if attrs:
			self._attrs_list = [self._attrs]  # extended by .merge_control()
			self._disabled_list = [self._attrs.has_key("disabled")]	 # ditto
		else:
			self._attrs_list = []  # extended by .merge_control()
			self._disabled_list = []  # ditto

		self._select_default = select_default
		self._clicked = False
		# Some list controls can have their default set only after all items
		# are known.  If so, self._value_is_set is false, and the self.fixup
		# method, called after all items have been added, sets the default.
		self._value_is_set = False
		self.common = Common()

	def is_of_kind(self, kind):
		if kind	 == "list":
			return True
		elif kind == "multilist":
			return bool(self.multiple)
		elif kind == "singlelist":
			return not self.multiple
		else:
			return False

	def _value_from_label(self, label):
		raise NotImplementedError("control '%s' does not yet support "
								  "by_label" % self.name)

	def toggle(self, name, by_label=False):
		return self._set_selected_state(name, 2, by_label)
	def set(self, selected, name, by_label=False):
		action = int(bool(selected))
		return self._set_selected_state(name, action, by_label)

	def _set_selected_state(self, name, action, by_label):
		"""
		name: item name
		action:
		 0: clear
		 1: set
		 2: toggle

		"""
		if not self.common.isstringlike(name):
			raise TypeError("item name must be string-like")
		if self.disabled:
			raise AttributeError("control '%s' is disabled" % self.name)
		if self.readonly:
			raise AttributeError("control '%s' is readonly" % self.name)
		if by_label:
			name = self._value_from_label(name)
		try:
			i = self._menu.index(name)
		except ValueError:
			raise ItemNotFoundError("no item named '%s'" % name)

		if self.multiple:
			if action == 2:
				action = not self._selected[i]
			if action and self._disabled_list[i]:
				raise AttributeError("item '%s' is disabled" % name)
			self._selected[i] = bool(action)
		else:
			if action == 2:
				if self._selected == name:
					action = 0
				else:
					action = 1
			if action == 0 and self._selected == name:
				self._selected = None
			elif action == 1:
				if self._disabled_list[i]:
					raise AttributeError("item '%s' is disabled" % name)
				self._selected = name

	def toggle_single(self, by_label=False):
		self._set_single_selected_state(2, by_label)
	def set_single(self, selected, by_label=False):
		action = int(bool(selected))
		self._set_single_selected_state(action, by_label)

	def _set_single_selected_state(self, action, by_label):
		if len(self._menu) != 1:
			raise ItemCountError("'%s' is not a single-item control" %
								 self.name)

		name = self._menu[0]
		if by_label:
			name = self._value_from_label(name)
		self._set_selected_state(name, action, by_label)

	def get_item_disabled(self, name, by_label=False):
		"""Get disabled state of named list item in a ListControl."""
		if by_label:
			name = self._value_from_label(name)
		try:
			i = self._menu.index(name)
		except ValueError:
			raise ItemNotFoundError()
		else:
			return self._disabled_list[i]

	def set_item_disabled(self, disabled, name, by_label=False):
		"""Set disabled state of named list item in a ListControl.

		disabled: boolean disabled state

		"""
		if by_label:
			name = self._value_from_label(name)
		try:
			i = self._menu.index(name)
		except ValueError:
			raise ItemNotFoundError()
		else:
			self._disabled_list[i] = bool(disabled)

	def set_all_items_disabled(self, disabled):
		"""Set disabled state of all list items in a ListControl.

		disabled: boolean disabled state

		"""
		for i in range(len(self._disabled_list)):
			self._disabled_list[i] = bool(disabled)

	def get_item_attrs(self, name, by_label=False):
		"""Return dictionary of HTML attributes for a single ListControl item.

		The HTML element types that describe list items are: OPTION for SELECT
		controls, INPUT for the rest.  These elements have HTML attributes that
		you may occasionally want to know about -- for example, the "alt" HTML
		attribute gives a text string describing the item (graphical browsers
		usually display this as a tooltip).

		The returned dictionary maps HTML attribute names to values.  The names
		and values are taken from the original HTML.

		Note that for SELECT controls, the returned dictionary contains a
		special key "contents" -- see SelectControl.__doc__.

		"""
		if by_label:
			name = self._value_from_label(name)
		try:
			i = self._menu.index(name)
		except ValueError:
			raise ItemNotFoundError()
		return self._attrs_list[i]

	def add_to_form(self, form):
		try:
			control = form.find_control(self.name, self.type)
		except ControlNotFoundError:
			Control.add_to_form(self, form)
		else:
			control.merge_control(self)

	def merge_control(self, control):
		assert bool(control.multiple) == bool(self.multiple)
		assert isinstance(control, self.__class__)
		self._menu.extend(control._menu)
		self._attrs_list.extend(control._attrs_list)
		self._disabled_list.extend(control._disabled_list)
		if control.multiple:
			self._selected.extend(control._selected)
		else:
			if control._value_is_set:
				self._selected = control._selected
		if control._value_is_set:
			self._value_is_set = True

	def fixup(self):
		"""
		ListControls are built up from component list items (which are also
		ListControls) during parsing.  This method should be called after all
		items have been added.	See ListControl.__doc__ for the reason this is
		required.

		"""
		# Need to set default selection where no item was indicated as being
		# selected by the HTML:

		# CHECKBOX:
		#  Nothing should be selected.
		# SELECT/single, SELECT/multiple and RADIO:
		#  RFC 1866 (HTML 2.0): says first item should be selected.
		#  W3C HTML 4.01 Specification: says that client behaviour is
		#	undefined in this case.	 For RADIO, exactly one must be selected,
		#	though which one is undefined.
		#  Both Netscape and Microsoft Internet Explorer (IE) choose first
		#	item for SELECT/single.	 However, both IE5 and Mozilla (both 1.0
		#	and Firebird 0.6) leave all items unselected for RADIO and
		#	SELECT/multiple.

		# Since both Netscape and IE all choose the first item for
		# SELECT/single, we do the same.  OTOH, both Netscape and IE
		# leave SELECT/multiple with nothing selected, in violation of RFC 1866
		# (but not in violation of the W3C HTML 4 standard); the same is true
		# of RADIO (which *is* in violation of the HTML 4 standard).  We follow
		# RFC 1866 if the select_default attribute is set, and Netscape and IE
		# otherwise.  RFC 1866 and HTML 4 are always violated insofar as you
		# can deselect all items in a RadioControl.

		raise NotImplementedError()

	def __getattr__(self, name):
		if name == "value":
			menu = self._menu
			if self.multiple:
				values = []
				for i in range(len(menu)):
					if self._selected[i]: values.append(menu[i])
				return values
			else:
				if self._selected is None: return []
				else: return [self._selected]
		else:
			raise AttributeError("%s instance has no attribute '%s'" %
								 (self.__class__.__name__, name))

	def __setattr__(self, name, value):
		if name == "value":
			if self.disabled:
				raise AttributeError("control '%s' is disabled" % self.name)
			if self.readonly:
				raise AttributeError("control '%s' is readonly" % self.name)
			self._set_value(value)
		elif name in ("name", "type", "multiple"):
			raise AttributeError("%s attribute is readonly" % name)
		else:
			self.__dict__[name] = value

	def _set_value(self, value):
		if self.multiple:
			self._multiple_set_value(value)
		else:
			self._single_set_value(value)

	def _single_set_value(self, value):
		if value is None or self.common.isstringlike(value):
			raise TypeError("ListControl, must set a sequence")
		nr = len(value)
		if not (0 <= nr <= 1):
			raise ItemCountError("single selection list, must set sequence of "
								 "length 0 or 1")

		if nr == 0:
			self._selected = None
		else:
			value = value[0]
			try:
				i = self._menu.index(value)
			except ValueError:
				raise ItemNotFoundError("no item named '%s'" %
										repr(value))
			if self._disabled_list[i]:
				raise AttributeError("item '%s' is disabled" % value)
			self._selected = value

	def _multiple_set_value(self, value):
		if value is None or self.common.isstringlike(value):
			raise TypeError("ListControl, must set a sequence")

		selected = [False]*len(self._selected)
		menu = self._menu
		disabled_list = self._disabled_list

		for v in value:
			found = False
			for i in range(len(menu)):
				item_name = menu[i]
				if v == item_name:
					if disabled_list[i]:
						raise AttributeError("item '%s' is disabled" % value)
					selected[i] = True
					found = True
					break
			if not found:
				raise ItemNotFoundError("no item named '%s'" % repr(v))
		self._selected = selected

	def set_value_by_label(self, value):
		raise NotImplementedError("control '%s' does not yet support "
								  "by_label" % self.name)
	def get_value_by_label(self):
		raise NotImplementedError("control '%s' does not yet support "
								  "by_label" % self.name)

	def possible_items(self, by_label=False):
		if by_label:
			raise NotImplementedError(
				"control '%s' does not yet support by_label" % self.name)
		return copy.copy(self._menu)

	def pairs(self):
		if self.disabled:
			return []

		if not self.multiple:
			name = self.name
			value = self._selected
			if name is None or value is None:
				return []
			return [(name, value)]
		else:
			control_name = self.name  # usually the name HTML attribute
			pairs = []
			for i in range(len(self._menu)):
				item_name = self._menu[i]  # usually the value HTML attribute
				if self._selected[i]:
					pairs.append((control_name, item_name))
			return pairs

	def _item_str(self, i):
		item_name = self._menu[i]
		if self.multiple:
			if self._selected[i]:
				item_name = "*"+item_name
		else:
			if self._selected == item_name:
				item_name = "*"+item_name
		if self._disabled_list[i]:
			item_name = "(%s)" % item_name
		return item_name

	def __str__(self):
		name = self.name
		if name is None: name = "<None>"

		display = []
		for i in range(len(self._menu)):
			s = self._item_str(i)
			display.append(s)

		infos = []
		if self.disabled: infos.append("disabled")
		if self.readonly: infos.append("readonly")
		info = string.join(infos, ", ")
		if info: info = " (%s)" % info

		return "<%s(%s=[%s])%s>" % (self.__class__.__name__,
									name, string.join(display, ", "), info)


