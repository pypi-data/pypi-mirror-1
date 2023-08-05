
# fileControl.py::refactored from JJLee's ClientForm
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

import string
from mechanoid.misc.Common import Common
from ScalarControl import ScalarControl

class FileControl(ScalarControl):
	"""File upload with INPUT TYPE=FILE.

	The value attribute of a FileControl is always None.  Use add_file instead.

	Additional public method: add_file

	"""

	def __init__(self, type, name, attrs):
		ScalarControl.__init__(self, type, name, attrs)
		self._value = None
		self._upload_data = []
		self.common = Common()

	def is_of_kind(self, kind): return kind == "file"

	def __setattr__(self, name, value):
		if name in ("value", "name", "type"):
			raise AttributeError("%s attribute is readonly" % name)
		else:
			self.__dict__[name] = value

	def add_file(self, file_object, content_type=None, filename=None):
		if not hasattr(file_object, "read"):
			raise TypeError("file-like object must have read method")
		if content_type is not None and not self.common.isstringlike(content_type):
			raise TypeError("content type must be None or string-like")
		if filename is not None and not self.common.isstringlike(filename):
			raise TypeError("filename must be None or string-like")
		if content_type is None:
			content_type = "application/octet-stream"
		self._upload_data.append((file_object, content_type, filename))

	def pairs(self):
		# XXX should it be successful even if unnamed?
		if self.name is None or self.disabled:
			return []
		return [(self.name, "")]

	def _write_mime_data(self, mw):
		# called by HTMLForm
		if len(self._upload_data) == 1:
			# single file
			file_object, content_type, filename = self._upload_data[0]
			mw2 = mw.nextpart()
			fn_part = filename and ('; filename="%s"' % filename) or ''
			disp = 'form-data; name="%s"%s' % (self.name, fn_part)
			mw2.addheader("Content-disposition", disp, prefix=1)
			fh = mw2.startbody(content_type, prefix=0)
			fh.write(file_object.read())
		elif len(self._upload_data) != 0:
			# multiple files
			mw2 = mw.nextpart()
			disp = 'form-data; name="%s"' % self.name
			mw2.addheader("Content-disposition", disp, prefix=1)
			fh = mw2.startmultipartbody("mixed", prefix=0)
			for file_object, content_type, filename in self._upload_data:
				mw3 = mw2.nextpart()
				fn_part = filename and ('; filename="%s"' % filename) or ''
				disp = 'file%s' % fn_part
				mw3.addheader("Content-disposition", disp, prefix=1)
				fh2 = mw3.startbody(content_type, prefix=0)
				fh2.write(file_object.read())
			mw2.lastpart()

	def __str__(self):
		name = self.name
		if name is None: name = "<None>"

		if not self._upload_data:
			value = "<No files added>"
		else:
			value = []
			for file, ctype, filename in self._upload_data:
				if filename is None:
					value.append("<Unnamed file>")
				else:
					value.append(filename)
			value = string.join(value, ", ")

		info = []
		if self.disabled: info.append("disabled")
		if self.readonly: info.append("readonly")
		info = string.join(info, ", ")
		if info: info = " (%s)" % info

		return "<%s(%s=%s)%s>" % (self.__class__.__name__, name, value, info)


