
# HTMLForm.py::refactored from JJLee's ClientForm
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

import sys, urllib, urllib2, string, copy, types
from mechanoid.misc.Common import Common
from mechanoid.misc.Errors import ControlNotFoundError
from cStringIO import StringIO
from MimeWriter import MimeWriter
from  html_controls import *

class HTMLForm:
	"""
	Represents a single HTML <form> ... </form> element.

	A form consists of a sequence of controls that usually have names,
	and which can take on various values.  The values of the various
	types of controls represent variously: text, zero-or-one-of-many or
	many-of-many choices, and files to be uploaded. Some controls can be
	clicked on to submit the form, and clickable controls' values
	sometimes include the coordinates of the click.

	Forms can be filled in with data to be returned to the server, and
	then submitted, using the click method to generate a request object
	suitable for passing to urllib2.urlopen.

	import ClientForm
	forms = ClientForm.ParseFile(html, base_uri)
	form = forms[0]

	form["query"] = "Python"
	form.set("lots", "nr_results")

	response = urllib2.urlopen(form.click())

	Usually, HTMLForm instances are not created directly.  Instead, the
	ParseFile or ParseResponse factory functions are used. If you do
	construct HTMLForm objects yourself, note that an HTMLForm instance
	is only properly initialised after the fixup method has been called
	(ParseFile and ParseResponse do this for you).	See
	ListControl.__doc__ for the reason this is required.

	Indexing a form (form["control_name"]) returns the named Control's
	value attribute. Assignment to a form index (form["control_name"] =
	something) is equivalent to assignment to the named Control's value
	attribute.	If you need to be more specific than just supplying the
	control's name, use the set_value and get_value methods.

	ListControl values are lists of item names.	 The list item's name is
	the value of the corresponding HTML element's "value" attribute.

	Example:

	  <INPUT type="CHECKBOX" name="cheeses" value="leicester"></INPUT>
	  <INPUT type="CHECKBOX" name="cheeses" value="cheddar"></INPUT>

	defines a CHECKBOX control with name "cheeses" which has two items,
	named "leicester" and "cheddar".

	Another example:

	  <SELECT name="more_cheeses">
		<OPTION>1</OPTION>
		<OPTION value="2" label="CHEDDAR">cheddar</OPTION>
	  </SELECT>

	defines a SELECT control with name "more_cheeses" which has two
	items, named "1" and "2" (because the OPTION element's value HTML
	attribute defaults to the element contents).

	To set, clear or toggle individual list items, use the set and
	toggle methods.	 To set the whole value, do as for any other
	control:use indexing or the set_/get_value methods.

	Example:

	# select *only* the item named "cheddar"
	form["cheeses"] = ["cheddar"]
	# select "cheddar", leave other items unaffected
	form.set("cheddar", "cheeses")

	Some controls (RADIO and SELECT without the multiple attribute) can
	only have zero or one items selected at a time. Some controls
	(CHECKBOX and SELECT with the multiple attribute) can have multiple
	items selected at a time.  To set the whole value of a ListControl,
	assign a sequence to a form index:

	form["cheeses"] = ["cheddar", "leicester"]

	If the ListControl is not multiple-selection, the assigned list must
	be of length one.

	To check whether a control has an item, or whether an item is
	selected, respectively:

	"cheddar" in form.possible_items("cheeses")
	"cheddar" in form["cheeses"]  # (or "cheddar" in form.get_value("cheeses"))

	Note that some list items may be disabled (see below).

	Note the following mistake:

	form[control_name] = control_value
	assert form[control_name] == control_value	# not necessarily true

	The reason for this is that form[control_name] always gives the list
	items in the order they were listed in the HTML.

	List items (hence list values, too) can be referred to in terms of
	list item labels rather than list item names.  Currently, this is
	only possible for SELECT controls (this is a bug).	To use this
	feature, use the by_label arguments to the various HTMLForm
	methods. Note that only *item* names (hence ListControl values
	also), not *control* names, can be referred to by label.

	The question of default values of OPTION contents, labels and values
	is somewhat complicated: see SelectControl.__doc__ and
	ListControl.get_item_attrs.__doc__ if you think you need to know.

	Controls can be disabled or readonly.  In either case, the control's
	value cannot be changed until you clear those flags (see example
	below).	 Disabled is the state typically represented by browsers by
	`greying out' a control.  Disabled controls are not `successful' --
	they don't cause data to get returned to the server. Readonly
	controls usually appear in browsers as read-only text boxes.
	Readonly controls are successful.  List items can also be disabled.
	Attempts to select disabled items (with form[name] = value, or using
	the ListControl.set method, for example) fail.	Attempts to clear
	disabled items are allowed.

	If a lot of controls are readonly, it can be useful to do this:

	form.set_all_readonly(False)

	When you want to do several things with a single control, or want to
	do less common things, like changing which controls and items are
	disabled, you can get at a particular control:

	control = form.find_control("cheeses")
	control.disabled = False
	control.readonly = False
	control.set_item_disabled(False, "gruyere")
	control.set("gruyere")

	Most methods on HTMLForm just delegate to the contained controls, so
	see the docstrings of the various Control classes for further
	documentation.	Most of these delegating methods take name, type,
	kind, id and nr arguments to specify the control to be operated on:
	see HTMLForm.find_control.__doc__.

	ControlNotFoundError (subclass of ValueError) is raised if the
	specified control can't be found.  This includes occasions where a
	non-ListControl is found, but the method (set, for example) requires
	a ListControl.	ItemNotFoundError (subclass of ValueError) is raised
	if a list item can't be found.	ItemCountError (subclass of
	ValueError) is raised if an attempt is made to select more than one
	item and the control doesn't allow that, or set/get_single are
	called and the control contains more than one item.	 AttributeError
	is raised if a control or item is readonly or disabled and an
	attempt is made to alter its value.

	XXX CheckBoxControl and RadioControl don't yet support item access
	by label.

	Security note: Remember that any passwords you store in HTMLForm
	instances will be saved to disk in the clear if you pickle them
	(directly or indirectly).  The simplest solution to this is to avoid
	pickling HTMLForm objects.	You could also pickle before filling in
	any password, or just set the password to "" before pickling.


	Public attributes:

	action: full (absolute URI) form action
	method: "GET" or "POST"
	enctype: form transfer encoding MIME type
	name: name of form (None if no name was specified)
	attrs: dictionary mapping original HTML form attributes to their values

	controls: list of Control instances; do not alter this list
	 (instead, call form.new_control to make a Control and add it to the
	 form, or control.add_to_form if you already have a Control
	 instance)


	Methods for form filling:
	-------------------------

	Most of the these methods have very similar arguments. See
	HTMLForm.find_control.__doc__ for details of the name, type, kind
	and nr arguments. See above for a description of by_label.

	def find_control(self, name=None, type=None, kind=None,
					 id=None, predicate=None, nr=None)

	get_value(name=None, type=None, kind=None, id=None, nr=None,
			  by_label=False)

	set_value(value, name=None, type=None, kind=None, id=None,
			  nr=None, by_label=False)

	set_all_readonly(readonly)


	Methods applying only to ListControls:

	possible_items(name=None, type=None, kind=None, id=None, nr=None,
				   by_label=False)

	set(selected, item_name, name=None, type=None, kind=None, id=None,
		nr=None, by_label=False)

	toggle(item_name, name=None, type=None, id=None, nr=None,
		   by_label=False)

	set_single(selected, name=None, type=None, kind=None, id=None,
			   nr=None, by_label=False)

	toggle_single(name=None, type=None, kind=None, id=None, nr=None,
				  by_label=False)


	Method applying only to FileControls:

	add_file(file_object, content_type="application/octet-stream",
			 filename=None, name=None, id=None, nr=None)


	Methods applying only to clickable controls:

	click(name=None, type=None, id=None, nr=0, coord=(1,1))

	"""
	
	type2class = {
		"text": TextControl,
		"password": PasswordControl,
		"hidden": HiddenControl,
		"textarea": TextareaControl,

		"isindex": IsIndexControl,

		"file": FileControl,

		"button": IgnoreControl,
		"buttonbutton": IgnoreControl,
		"reset": IgnoreControl,
		"resetbutton": IgnoreControl,

		"submit": SubmitControl,
		"submitbutton": SubmitButtonControl,
		"image": ImageControl,

		"radio": RadioControl,
		"checkbox": CheckboxControl,
		"select": SelectControl,
		}

	#---------------------------------------------------
	# Initialisation.  Use ParseResponse / ParseFile instead.

	def __init__(self, action, method="GET",
				 enctype="application/x-www-form-urlencoded",
				 name=None, attrs=None):
		"""
		In the usual case, use ParseResponse (or ParseFile) to create new
		HTMLForm objects.

		action: full (absolute URI) form action
		method: "GET" or "POST"
		enctype: form transfer encoding MIME type
		name: name of form
		attrs: dictionary mapping original HTML form attributes to their values

		"""
		self.action = action
		self.method = method
		self.enctype = enctype
		self.name = name
		if attrs is not None:
			self.attrs = attrs.copy()
		else:
			self.attrs = {}
		self.controls = []
		self.common = Common()

	def new_control(self, type, name, attrs,
					ignore_unknown=False, select_default=False):
		"""
		Adds a new control to the form.

		This is usually called by ParseFile and ParseResponse. Don't
		call it youself unless you're building your own Control
		instances.

		Note that controls representing lists of items are built up from
		controls holding only a single list item.  See
		ListControl.__doc__ for further information.

		type: type of control (see Control.__doc__ for a list)

		attrs: HTML attributes of control

		ignore_unknown: if true, use a dummy Control instance for
			controls of unknown type; otherwise, raise ValueError

		select_default: for RADIO and multiple-selection SELECT
			controls, pick the first item as the default if no
			'selected' HTML attribute is present (this defaulting
			happens when the HTMLForm.fixup method is called)

		"""
		type = string.lower(type)
		klass = self.type2class.get(type)
		if klass is None:
			if ignore_unknown:
				klass = IgnoreControl
			else:
				raise ValueError("Unknown control type '%s'" % type)

		a = attrs.copy()
		if issubclass(klass, ListControl):
			control = klass(type, name, a, select_default)
		else:
			control = klass(type, name, a)
		control.add_to_form(self)

	def fixup(self):
		"""
		Normalise form after all controls have been added.

		This is usually called by ParseFile and ParseResponse. Don't
		call it youself unless you're building your own Control
		instances.

		This method should only be called once, after all controls have
		been added to the form.

		"""
		for control in self.controls:
			control.fixup()
		return	

	#---------------------------------------------------

	def __str__(self):
		header = "%s %s %s" % (self.method, self.action, self.enctype)
		rep = [header]
		for control in self.controls:
			rep.append("  %s" % str(control))
		return "<%s>" % string.join(rep, "\n")

	#---------------------------------------------------
	# Form-filling methods.

	def __getitem__(self, name):
		return self.find_control(name).value

	def __setitem__(self, name, value):
		control = self.find_control(name)
		try:
			control.value = value
		except AttributeError, e:
			raise ValueError(str(e))

	def get_value(self, name=None, type=None, kind=None,
				  id=None, nr=None, by_label=False):
		"""
		Return value of control.

		If only name and value arguments are supplied, this is
		equivalent to form[name]

		"""
		c = self.find_control(name, type, kind, id, nr=nr)
		if by_label:
			try:
				meth = c.get_value_by_label
			except AttributeError:
				raise NotImplementedError(
					"control '%s' does not yet support by_label" % c.name)
			else:
				return meth()
		else:
			return c.value

	def set_value(self, value, name=None, type=None, kind=None, id=None,
				  nr=None, by_label=False):
		"""
		Set value of control.

		If only name and value arguments are supplied, this is
		equivalent to form[name] = value

		"""
		c = self.find_control(name, type, kind, id, nr=nr)
		if by_label:
			try:
				meth = c.set_value_by_label
			except AttributeError:
				raise NotImplementedError(
					"control '%s' does not yet support by_label" % c.name)
			else:
				meth(value)
		else:
			c.value = value

	def set_all_readonly(self, readonly):
		for control in self.controls:
			control.readonly = bool(readonly)

	#---------------------------------------------------
	# Form-filling methods applying only to ListControls.

	def possible_items(self, name=None, type=None, kind=None, id=None,
					   nr=None, by_label=False):
		"""
		Return a list of all values that the specified control can take.

		"""
		c = self.__find_list_control(name, type, kind, id, nr)
		return c.possible_items(by_label)

	def set(self, selected, item_name, name=None, type=None, kind=None,
			id=None, nr=None, by_label=False):
		"""
		Select / deselect named list item.

		selected: boolean selected state

		"""
		self.__find_list_control(name, type, kind, id, nr).set(
			selected, item_name, by_label)

	def toggle(self, item_name, name=None, type=None, kind=None, id=None,
			   nr=None, by_label=False):
		"""
		Toggle selected state of named list item.

		"""
		self.__find_list_control(name, type, kind, id, nr).toggle(
			item_name, by_label)

	def set_single(self, selected, name=None, type=None, kind=None,
				   id=None, nr=None, by_label=False):
		"""
		Select / deselect list item in a control having only one item.

		If the control has multiple list items, ItemCountError is raised.

		This is a convenience method; you don't need to know the item's
		name -- the item name in these single-item controls is usually
		something meaningless like "1" or "on".

		For example, if a checkbox has a single item named "on", the
		following two calls are equivalent:

		control.toggle("on")
		control.toggle_single()

		"""
		self.__find_list_control(name, type, kind, id, nr).set_single(
			selected, by_label)

	def toggle_single(self, name=None, type=None, kind=None, id=None, nr=None,
					  by_label=False):
		"""
		Toggle selected state of list item in control having only one item.

		The rest is as for HTMLForm.set_single.__doc__.

		"""
		self.__find_list_control(name, type, kind, id, nr).toggle_single(
			by_label)

	#---------------------------------------------------
	# Form-filling method applying only to FileControls.

	def add_file(self, file_object, content_type=None, filename=None,
				 name=None, id=None, nr=None):
		"""
		Add a file to be uploaded.

		file_object: file-like object (with read method) from which to
			read data to upload

		content_type: MIME content type of data to upload

		filename: filename to pass to server

		If filename is None, no filename is sent to the server.

		If content_type is None, the content type is guessed based on the
		filename and the data from read from the file object.

		XXX At the moment, guessed content type is always
		application/octet-stream.  Use sndhdr, imghdr modules.	Should
		also try to guess HTML, XML, and plain text.

		Note the following useful HTML attributes of file upload
		controls (see HTML 4.01 spec, section 17):

		accept: comma-separated list of content types that the server
			will handle correctly; you can use this to filter out
			non-conforming files

		size: XXX IIRC, this is indicative of whether form wants
			multiple or single files

		maxlength: XXX hint of max content length in bytes?

		"""
		self.find_control(name, "file", id=id, nr=nr).add_file(
			file_object, content_type, filename)

    #---------------------------------------------------
	# Form submission method, applying only to clickable controls.

	def click(self, name=None, type=None, id=None, nr=0, coord=(1,1)):
		"""
		Return request that would result from clicking on a control.

		The request object is a urllib2.Request instance, which you can
		pass to urllib2.urlopen (or ClientCookie.urlopen).

		Only some control types (INPUT/SUBMIT & BUTTON/SUBMIT buttons
		and IMAGEs) can be clicked.

		Will click on the first clickable control, subject to the name,
		type and nr arguments (as for find_control).  If no name, type,
		id or number is specified and there are no clickable controls, a
		request will be returned for the form in its current,
		un-clicked, state.

		IndexError is raised if any of name, type, id or nr is specified
		but no matching control is found. ValueError is raised if the
		HTMLForm has an enctype attribute that is not recognised.

		You can optionally specify a coordinate to click at, which only
		makes a difference if you clicked on an image.

		"""
		return self.__click(name, type, id, nr, coord, "request")

    #---------------------------------------------------

	def find_control(self, name=None, type=None, kind=None, id=None,
					 predicate=None, nr=None):
		"""
		Locate and return some specific control within the form.

		At least one of the name, type, kind, predicate and nr arguments
		must be supplied.  If no matching control is found,
		ControlNotFoundError is raised.

		If name is specified, then the control must have the indicated
		name.

		If type is specified then the control must have the specified
		type (in addition to the types possible for <input> HTML tags:
		"text", "password", "hidden", "submit", "image", "button",
		"radio", "checkbox", "file" we also have "reset",
		"buttonbutton", "submitbutton", "resetbutton", "textarea",
		"select" and "isindex").

		If kind is specified, then the control must fall into the
		specified group, each of which satisfies a particular
		interface. The types are "text", "list", "multilist",
		"singlelist", "clickable" and "file".

		If id is specified, then the control must have the indicated id.

		If predicate is specified, then the control must match that
		function.  The predicate function is passed the control as its
		single argument, and should return a boolean value indicating
		whether the control matched.

		nr, if supplied, is the sequence number of the control (where 0
		is the first).  Note that control 0 is the first control
		matching all the other arguments (if supplied); it is not
		necessarily the first control in the form.

		"""
		if ((name is None) and (type is None) and (kind is None) and
			(id is None) and (predicate is None) and (nr is None)):
			raise ValueError(
				"at least one argument must be supplied to specify control")
		if nr is None: nr = 0
		return self.__find_control(name, type, kind, id, predicate, nr)

	def has_control(self, name=None, type=None, kind=None, id=None,
					 predicate=None):
		if ((name is None) and (type is None) and (kind is None) and
			(id is None) and (predicate is None) and (nr is None)):
			raise ValueError(
				"at least one argument must be supplied to specify control")
		nr = 0
		control = self.__find_control(name, type, kind, id, predicate, nr)
		if name is not None and name != control.name:
			return 0
		if type is not None and type != control.type:
			return 0
		if kind is not None and not control.is_of_kind(kind):
			return 0
		if id is not None and id != control.id:
			return 0
		if predicate and not predicate(control):
			return 0
		return 1

	def switch_click(self, return_type):
		"""
		This is called by HTMLForm and clickable Controls to hide
		switching on return_type.
		
		"""
		if return_type == "pairs":
			return self.__pairs()
		elif return_type == "request_data":
			return self.__request_data()
		else:
			req_data = self.__request_data()
			req = urllib2.Request(req_data[0], req_data[1])
			for key, val in req_data[2]:
				req.add_header(key, val)
			return req

    #---------------------------------------------------
	# Private methods.

	def __find_list_control(self, name=None, type=None, kind=None,
						   id=None, nr=None):
		if ((name is None) and (type is None) and (kind is None) and
			(id is None) and (nr is None)):
			raise ValueError(
				"at least one argument must be supplied to specify control")
		if nr is None: nr = 0
		return self.__find_control(name, type, kind, id, self.__is_listcontrol, nr)

	def __find_control(self, name, type, kind, id, predicate, nr):
		if (name is not None) and not self.common.isstringlike(name):
			raise TypeError("control name must be string-like")
		if (type is not None) and not self.common.isstringlike(type):
			raise TypeError("control type must be string-like")
		if (kind is not None) and not self.common.isstringlike(kind):
			raise TypeError("control kind must be string-like")
		if (id is not None) and not self.common.isstringlike(id):
			raise TypeError("control id must be string-like")
		if (predicate is not None) and not callable(predicate):
			raise TypeError("control predicate must be callable")
		if nr < 0: raise ValueError("control number must be a positive integer")

		orig_nr = nr

		for control in self.controls:
			if name is not None and name != control.name:
				continue
			if type is not None and type != control.type:
				continue
			if kind is not None and not control.is_of_kind(kind):
				continue
			if id is not None and id != control.id:
				continue
			if predicate and not predicate(control):
				continue
			if nr:
				nr = nr - 1
				continue
			return control

		description = []
		if name is not None: description.append("name '%s'" % name)
		if type is not None: description.append("type '%s'" % type)
		if kind is not None: description.append("kind '%s'" % kind)
		if id is not None: description.append("id '%s'" % id)
		if predicate is not None:
			description.append("predicate %s" % predicate)
		if orig_nr: description.append("nr %d" % orig_nr)
		description = string.join(description, ", ")
		raise ControlNotFoundError("no control matching "+description)

	def __click(self, name, type, id, nr, coord, return_type):
		try:
			control = self.__find_control(name, type, "clickable", id, None, nr)
		except ControlNotFoundError:
			if ((name is not None) or (type is not None) or (id is not None) or
				(nr != 0)):
				raise
			# no clickable controls, but no control was explicitly requested,
			# so return state without clicking any control
			return self.switch_click(return_type)
		else:
			return control._click(self, coord, return_type)

	# Return sequence of (key, value) pairs suitable for urlencoding.
	def __pairs(self):
		pairs = []
		for control in self.controls:
			pairs.extend(control.pairs())
		return pairs

	def __urlencode(self, query, doseq=False):
		"""
		Encode a sequence of two-element tuples or dictionary into a URL
		query \ string.	 If any values in the query arg are sequences
		and doseq is true, each sequence element is converted to a
		separate parameter.	 If the query arg is a sequence of
		two-element tuples, the order of the parameters in the output
		will match the order of parameters in the input.

		This version of urlencode is from my Python 1.5.2 back-port of
		the Python 2.1 CVS maintenance branch of urllib. It will accept
		a sequence of pairs instead of a mapping -- the 2.0 version only
		accepts a mapping.  used in class HTMLForm

		"""
		if hasattr(query,"items"):
			# mapping objects
			query = query.items()
		else:
			try:
				# non-sequence items should not work with len()
				x = len(query)
				# non-empty strings will fail this
				if len(query) and type(query[0]) != types.TupleType:
					raise TypeError()
				# zero-length sequences of all types will get here and succeed,
				# but that's a minor nit - since the original implementation
				# allowed empty dicts that type of behavior probably should be
				# preserved for consistency
			except TypeError:
				ty,va,tb = sys.exc_info()
				raise TypeError(
					"not a valid non-string sequence or mapping object", tb)

		l = []
		if not doseq:
			# preserve old behavior
			for k, v in query:
				k = urllib.quote_plus(str(k))
				v = urllib.quote_plus(str(v))
				l.append(k + '=' + v)
		else:
			for k, v in query:
				k = urllib.quote_plus(str(k))
				if type(v) == types.StringType:
					v = urllib.quote_plus(v)
					l.append(k + '=' + v)
				elif type(v) == types.UnicodeType:
					# XXX Is there a reasonable way to convert to ASCII?
					# encode generates a string, but "replace" or "ignore"
					# lose information and "strict" can raise UnicodeError
					v = urllib.quote_plus(v.encode("ASCII","replace"))
					l.append(k + '=' + v)
				else:
					try:
						# is this a sufficient test for sequence-ness?
						x = len(v)
					except TypeError:
						# not a sequence
						v = urllib.quote_plus(str(v))
						l.append(k + '=' + v)
					else:
						# loop over the sequence
						for elt in v:
							l.append(k + '=' + urllib.quote_plus(str(elt)))
		return string.join(l, '&')

	# Return a tuple (url, data, headers).
	def __request_data(self):
		method = string.upper(self.method)
		if method == "GET":
			if self.enctype != "application/x-www-form-urlencoded":
				raise ValueError(
					"unknown GET form encoding type '%s'" % self.enctype)
			if "?" in self.action:
				fmt = "%s&%s"
			else:
				fmt = "%s?%s"
			uri = fmt % (self.action, self.__urlencode(self.__pairs()))
			return uri, None, []
		elif method == "POST":
			if self.enctype == "application/x-www-form-urlencoded":
				return (self.action, self.__urlencode(self.__pairs()),
						[("Content-type", self.enctype)])
			elif self.enctype == "multipart/form-data":
				data = StringIO()
				http_hdrs = []
				mw = MimeWriter(data, http_hdrs)
				f = mw.startmultipartbody("form-data", add_to_http_hdrs=True,
										  prefix=0)
				for control in self.controls:
					control._write_mime_data(mw)
				mw.lastpart()
				return self.action, data.getvalue(), http_hdrs
			else:
				raise ValueError(
					"unknown POST form encoding type '%s'" % self.enctype)
		else:
			raise ValueError("Unknown method '%s'" % method)

	def __is_listcontrol(self, control):
		return control.is_of_kind("list")
