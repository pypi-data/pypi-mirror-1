
# ClientForm.py::refactored from JJLee's ClientForm
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

"""
HTML form handling for web clients.

ClientForm is a Python module for handling HTML forms on the client
side, useful for parsing HTML forms, filling them in and returning the
completed forms to the server.	It has developed from a port of Gisle
Aas' Perl module HTML::Form, from the libwww-perl library, but the
interface is not the same.

The most useful docstring is the one for HTMLForm.

RFC 1866: HTML 2.0
RFC 1867: Form-based File Upload in HTML
RFC 2388: Returning Values from Forms: multipart/form-data
HTML 3.2 Specification, W3C Recommendation 14 January 1997 (for ISINDEX)
HTML 4.01 Specification, W3C Recommendation 24 December 1999

"""
import string, StringIO
from HTMLForm import HTMLForm
from urlparse import urljoin
from mechanoid.misc.Errors import ParseError
from mechanoid.misc.Common import Common
from formparser.FormParser import FormParser


class ClientForm:

	def __init__(self):
		self.lib = Common()
		return

	def ParseResponse(self, response, select_default=False):
		"""
		Parse HTTP response and return a list of HTMLForm instances.

		The return value of urllib2.urlopen can be conveniently passed
		to this function as the response parameter.

		ClientForm.ParseError is raised on parse errors.

		response: file-like object (supporting read() method) with a
			method geturl(), returning the URI of the HTTP response

		select_default: for multiple-selection SELECT controls and RADIO
			controls, pick the first item as the default if none are
			selected in the HTML form_parser_class: class to instantiate
			and use to pass

		Pass a true value for select_default if you want the behaviour
		specified by RFC 1866 (the HTML 2.0 standard), which is to
		select the first item in a RADIO or multiple-selection SELECT
		control if none were selected in the HTML.	Most browsers
		(including Microsoft Internet Explorer (IE) and Netscape
		Navigator) instead leave all items unselected in these
		cases. The W3C HTML 4.0 standard leaves this behaviour undefined
		in the case of multiple-selection SELECT controls, but insists
		that at least one RADIO button should be checked at all times,
		in contradiction to browser behaviour.

		"""
		return self.ParseFile(response, response.geturl(), select_default)

	def ParseFile(self, file, base_uri, select_default=False):
		"""
		Parse HTML and return a list of HTMLForm instances.

		ClientForm.ParseError is raised on parse errors.

		file: file-like object (supporting read() method) containing
			HTML with zero or more forms to be parsed

		base_uri: the URI of the document (note that the base URI used
			to submit the form will be that given in the BASE element if
			present, not that of the document)

		For the other arguments and further details, see
		ParseResponse.__doc__.

		"""
		fp = FormParser()
		tmp = self.lib.html_canonical(file)
		tmp = self.lib.form_only(tmp)
		data = tmp.read()

## SELF CODE BEGIN
		if (0):
			import os
			f = open(os.path.expandvars("$HOME/clientform.html"),'w')
			f.write(data)
			f.close()
## SELF CODE END
		
		try:
			fp.feed(data)
		except ParseError, e:
			e.base_uri = base_uri

		if fp.base is not None:
			base_uri = fp.base
		forms = []
		for (name, action, method, enctype), attrs, controls in fp.forms:
			if action is None:
				action = base_uri
			else:
				action = urljoin(base_uri, action)
			form = HTMLForm(action, method, enctype, name, attrs)
			for type, name, attr in controls:
				form.new_control(type, name, attr, select_default=select_default)
			forms.append(form)
		for form in forms:
			form.fixup()
		return forms
