
# AbstractFormParser.py::refactored from JJLee's ClientForm
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
# Copyright 2002-2003 John J. Lee <jjl@pobox.com>  (BSD License)
# Copyright 1998-2000 Gisle Aas.
#

import string
from mechanoid.misc.Errors import ParseError

class AbstractFormParser:
	"""forms attribute contains HTMLForm instances on completion."""
	# pinched (and modified) from Moshe Zadka
	def __init__(self, entitydefs=None):
		if entitydefs is not None:
			self.entitydefs = entitydefs
		self.base = None
		self.forms = []
		self._current_form = None
		self._select = None
		self._optgroup = None
		self._option = None
		self._textarea = None

	def do_base(self, attrs):
		for key, value in attrs:
			if key == "href":
				self.base = value

	def start_form(self, attrs):
		if self._current_form is not None:
			raise ParseError("nested FORMs")
		name = None
		action = None
		enctype = "application/x-www-form-urlencoded"
		method = "GET"
		d = {}
		for key, value in attrs:
			if key == "name":
				name = value
			elif key == "action":
				action = value
			elif key == "method":
				method = string.upper(value)
			elif key == "enctype":
				enctype = string.lower(value)
			d[key] = value
		controls = []
		self._current_form = (name, action, method, enctype), d, controls

	def end_form(self):
		if self._current_form is None:
			raise ParseError("end of FORM before start")
		self.forms.append(self._current_form)
		self._current_form = None

	def start_select(self, attrs):
		if self._current_form is None:
			raise ParseError("start of SELECT before start of FORM")
		if self._select is not None:
			raise ParseError("nested SELECTs")
		if self._textarea is not None:
			raise ParseError("SELECT inside TEXTAREA")
		d = {}
		for key, val in attrs:
			d[key] = val

		self._select = d

		self._append_select_control({"__select": d})

	def end_select(self):
		if self._current_form is None:
			raise ParseError("end of SELECT before start of FORM")
		if self._select is None:
			raise ParseError("end of SELECT before start")

		if self._option is not None:
			self._end_option()

		self._select = None

	def start_optgroup(self, attrs):
		if self._select is None:
			raise ParseError("OPTGROUP outside of SELECT")
		d = {}
		for key, val in attrs:
			d[key] = val

		self._optgroup = d

	def end_optgroup(self):
		if self._optgroup is None:
			raise ParseError("end of OPTGROUP before start")
		self._optgroup = None

	def _start_option(self, attrs):
		if self._select is None:
			raise ParseError("OPTION outside of SELECT")
		if self._option is not None:
			self._end_option()

		d = {}
		for key, val in attrs:
			d[key] = val

		self._option = {}
		self._option.update(d)
		if (self._optgroup and self._optgroup.has_key("disabled") and
			not self._option.has_key("disabled")):
			self._option["disabled"] = None

	def _end_option(self):
		if self._option is None:
			raise ParseError("end of OPTION before start")

		contents = string.strip(self._option.get("contents", ""))
		self._option["contents"] = contents
		if not self._option.has_key("value"):
			self._option["value"] = contents
		if not self._option.has_key("label"):
			self._option["label"] = contents
		# stuff dict of SELECT HTML attrs into a special private key
		#  (gets deleted again later)
		self._option["__select"] = self._select
		self._append_select_control(self._option)
		self._option = None

	def _append_select_control(self, attrs):
		controls = self._current_form[2]
		name = self._select.get("name")
		controls.append(("select", name, attrs))

	def start_textarea(self, attrs):
		if self._current_form is None:
			raise ParseError("start of TEXTAREA before start of FORM")
		if self._textarea is not None:
			raise ParseError("nested TEXTAREAs")
		if self._select is not None:
			raise ParseError("TEXTAREA inside SELECT")
		d = {}
		for key, val in attrs:
			d[key] = val

		self._textarea = d

	def end_textarea(self):
		if self._current_form is None:
			raise ParseError("end of TEXTAREA before start of FORM")
		if self._textarea is None:
			raise ParseError("end of TEXTAREA before start")
		controls = self._current_form[2]
		name = self._textarea.get("name")
		controls.append(("textarea", name, self._textarea))
		self._textarea = None

	def handle_data(self, data):
		if self._option is not None:
			# self._option is a dictionary of the OPTION element's HTML
			# attributes, but it has two special keys, one of which is the
			# special "contents" key contains text between OPTION tags (the
			# other is the "__select" key: see the end_option method)
			map = self._option
			key = "contents"
		elif self._textarea is not None:
			map = self._textarea
			key = "value"
		else:
			return

		if not map.has_key(key):
			map[key] = data
		else:
			map[key] = map[key] + data

	def do_button(self, attrs):
		if self._current_form is None:
			raise ParseError("start of BUTTON before start of FORM")
		d = {}
		d["type"] = "submit"  # default
		for key, val in attrs:
			d[key] = val
		controls = self._current_form[2]

		type = d["type"]
		name = d.get("name")
		# we don't want to lose information, so use a type string that
		# doesn't clash with INPUT TYPE={SUBMIT,RESET,BUTTON}
		# eg. type for BUTTON/RESET is "resetbutton"
		#	  (type for INPUT/RESET is "reset")
		type = type+"button"
		controls.append((type, name, d))

	def do_input(self, attrs):
		if self._current_form is None:
			raise ParseError("start of INPUT before start of FORM")
		d = {}
		d["type"] = "text"	# default
		for key, val in attrs:
			d[key] = val
		controls = self._current_form[2]

		type = d["type"]
		name = d.get("name")
		controls.append((type, name, d))

	def do_isindex(self, attrs):
		if self._current_form is None:
			raise ParseError("start of ISINDEX before start of FORM")
		d = {}
		for key, val in attrs:
			d[key] = val
		controls = self._current_form[2]

		# isindex doesn't have type or name HTML attributes
		controls.append(("isindex", None, d))

