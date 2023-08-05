
# _ClientForm_MimeWriter.py::refactored from JJLee's ClientForm
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
# Copyright 2002-2003 John J. Lee <jjl@pobox.com>  (BSD License)
# Copyright 1998-2000 Gisle Aas.
#

import mimetools, string

# XXX this class could be reduced to only what is used by other classes.
# And if we're going to keep it, shouldn't we grab choose_boundary from
# the deprecated mimetools as well?
class MimeWriter:

	"""Generic MIME writer.

	This cut-n-pasted MimeWriter from standard library is here so you
	can add to HTTP headers rather than message body when appropriate.
	It also uses \r\n in place of \n. This is nasty.

	Methods:

	__init__()
	addheader()
	flushheaders()
	startbody()
	startmultipartbody()
	nextpart()
	lastpart()

	A MIME writer is much more primitive than a MIME parser.  It
	doesn't seek around on the output file, and it doesn't use large
	amounts of buffer space, so you have to write the parts in the
	order they should occur on the output file.	 It does buffer the
	headers you add, allowing you to rearrange their order.

	General usage is:

	f = <open the output file>
	w = MimeWriter(f)
	...call w.addheader(key, value) 0 or more times...

	followed by either:

	f = w.startbody(content_type)
	...call f.write(data) for body data...

	or:

	w.startmultipartbody(subtype)
	for each part:
		subwriter = w.nextpart()
		...use the subwriter's methods to create the subpart...
	w.lastpart()

	The subwriter is another MimeWriter instance, and should be
	treated in the same way as the toplevel MimeWriter.	 This way,
	writing recursive body parts is easy.

	Warning: don't forget to call lastpart()!

	XXX There should be more state so calls made in the wrong order
	are detected.

	Some special cases:

	- startbody() just returns the file passed to the constructor;
	  but don't use this knowledge, as it may be changed.

	- startmultipartbody() actually returns a file as well;
	  this can be used to write the initial 'if you can read this your
	  mailer is not MIME-aware' message.

	- If you call flushheaders(), the headers accumulated so far are
	  written out (and forgotten); this is useful if you don't need a
	  body part at all, e.g. for a subpart of type message/rfc822
	  that's (mis)used to store some header-like information.

	- Passing a keyword argument 'prefix=<flag>' to addheader(),
	  start*body() affects where the header is inserted; 0 means
	  append at the end, 1 means insert at the start; default is
	  append for addheader(), but insert for start*body(), which use
	  it to determine where the Content-type header goes.

	"""

#sc# IGNORED METHOD
	def __init__(self, fp, http_hdrs=None):
		self._http_hdrs = http_hdrs
		self._fp = fp
		self._headers = []
		self._boundary = []
		self._first_part = True

#sc# Called by: startmultipartbody, 
	def __choose_boundary(self):
		b = mimetools.choose_boundary()
		string.replace(b, ".", "")
		return b

#sc# Called by: startbody, 
	def addheader(self, key, value, prefix=0,
				  add_to_http_hdrs=0):
		"""
		prefix is ignored if add_to_http_hdrs is true.
		"""
		lines = string.split(value, "\r\n")
		while lines and not lines[-1]: del lines[-1]
		while lines and not lines[0]: del lines[0]
		if add_to_http_hdrs:
			value = string.join(lines, "")
			self._http_hdrs.append((key, value))
		else:
			for i in range(1, len(lines)):
				lines[i] = "	" + string.strip(lines[i])
			value = string.join(lines, "\r\n") + "\r\n"
			line = key + ": " + value
			if prefix:
				self._headers.insert(0, line)
			else:
				self._headers.append(line)

#sc# Called by: startbody, 
	def flushheaders(self):
		self._fp.writelines(self._headers)
		self._headers = []

#sc# Called by: startmultipartbody, 
	def startbody(self, ctype=None, plist=[], prefix=1,
				  add_to_http_hdrs=0, content_type=1):
		"""
		prefix is ignored if add_to_http_hdrs is true.
		"""
		if content_type and ctype:
			for name, value in plist:
				ctype = ctype + ';\r\n %s=%s' % (name, value)
			self.addheader("Content-type", ctype, prefix=prefix,
						   add_to_http_hdrs=add_to_http_hdrs)
		self.flushheaders()
		if not add_to_http_hdrs: self._fp.write("\r\n")
		self._first_part = True
		return self._fp

#sc# WARNING::UNCALLED METHOD
	def startmultipartbody(self, subtype, boundary=None, plist=[], prefix=1,
						   add_to_http_hdrs=0, content_type=1):
		boundary = boundary or self.__choose_boundary()
		self._boundary.append(boundary)
		return self.startbody("multipart/" + subtype,
							  [("boundary", boundary)] + plist,
							  prefix=prefix,
							  add_to_http_hdrs=add_to_http_hdrs,
							  content_type=content_type)

#sc# Called by: lastpart, 
	def nextpart(self):
		boundary = self._boundary[-1]
		if self._first_part:
			self._first_part = False
		else:
			self._fp.write("\r\n")
		self._fp.write("--" + boundary + "\r\n")
		return self.__class__(self._fp)

#sc# WARNING::UNCALLED METHOD
	def lastpart(self):
		if self._first_part:
			self.nextpart()
		boundary = self._boundary.pop()
		self._fp.write("\r\n--" + boundary + "--\r\n")

