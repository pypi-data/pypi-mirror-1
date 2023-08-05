
# IsIndexControl.py::refactored from JJLee's ClientForm
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

import urllib, urllib2, string
from urlparse import urljoin
from ScalarControl import ScalarControl

class IsIndexControl(ScalarControl):
	"""ISINDEX control.

	ISINDEX is the odd-one-out of HTML form controls.  In fact, it isn't really
	part of regular HTML forms at all, and predates it.	 You're only allowed
	one ISINDEX per HTML document.	ISINDEX and regular form submission are
	mutually exclusive -- either submit a form, or the ISINDEX.

	Having said this, since ISINDEX controls may appear in forms (which is
	probably bad HTML), ParseFile / ParseResponse will include them in the
	HTMLForm instances it returns.	You can set the ISINDEX's value, as with
	any other control (but note that ISINDEX controls have no name, so you'll
	need to use the type argument of set_value!).  When you submit the form,
	the ISINDEX will not be successful (ie., no data will get returned to the
	server as a result of its presence), unless you click on the ISINDEX
	control, in which case the ISINDEX gets submitted instead of the form:

	form.set_value("my isindex value", type="isindex")
	urllib2.urlopen(form.click(type="isindex"))

	ISINDEX elements outside of FORMs are ignored.	If you want to submit one
	by hand, do it like so:

	url = urlparse.urljoin(page_uri, "?"+urllib.quote_plus("my isindex value"))
	result = urllib2.urlopen(url)

	"""
	def __init__(self, type, name, attrs):
		ScalarControl.__init__(self, type, name, attrs)
		if self._value is None:
			self._value = ""

	def is_of_kind(self, kind): return kind in ["text", "clickable"]

	def pairs(self):
		return []

	def _click(self, form, coord, return_type):
		# Relative URL for ISINDEX submission: instead of "foo=bar+baz",
		# want "bar+baz".
		# This doesn't seem to be specified in HTML 4.01 spec. (ISINDEX is
		# deprecated in 4.01, but it should still say how to submit it).
		# Submission of ISINDEX is explained in the HTML 3.2 spec, though.
		url = urljoin(form.action, "?"+urllib.quote_plus(self.value))
		req_data = url, None, []

		if return_type == "pairs":
			return []
		elif return_type == "request_data":
			return req_data
		else:
			return urllib2.Request(url)

	def __str__(self):
		value = self.value
		if value is None: value = "<None>"

		infos = []
		if self.disabled: infos.append("disabled")
		if self.readonly: infos.append("readonly")
		info = string.join(infos, ", ")
		if info: info = " (%s)" % info

		return "<%s(%s)%s>" % (self.__class__.__name__, value, info)


