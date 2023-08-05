
# _PullParser_Token.py::refactored from JJLee's pullparser
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
# Copyright 2003-2004 John J. Lee <jjl@pobox.com>
# Copyright 1998-2001 Gisle Aas (original libwww-perl code under Perl Artistic License)
#

"""

Data represention of an HTML tag, declaration, processing instruction,
etc.  Behaves as a tuple-like object (ie. iterable) and has attributes
.type, .data and .attrs.

>>> import _PullParser_Token
>>> t = _PullParser_Token._PullParser_Token("starttag", "a", [("href", "http://localhost/")])
>>> t == ("starttag", "a", [("href", "http://localhost/")])
True
>>> print t
_PullParser_Token('starttag', 'a', [('href', 'http://localhost/')])
>>> t.type == "starttag"
True
>>> t.data == "a"
True
>>> t.attrs == [("href", "http://localhost/")]
True

Public attributes

type: one of "starttag", "endtag", "startendtag", "charref",
    "entityref", "data", "comment", "decl", "pi", after the
    corresponding methods of HTMLParser.HTMLParser

data: For a tag, the tag name; otherwise, the relevant data carried by
    the tag, as a string

attrs: list of (name, value) pairs representing HTML attributes (or None
    if token does not represent an opening tag)

"""

class Token:

	def __init__(self, type, data, attrs=None):
		self.type = type
		self.data = data
		self.attrs = attrs
		return

	def __iter__(self):
		return self.type, self.data, self.attrs

	def __cmp__(self, other):
		type, data, attrs = other
		if (self.type == type and
			self.data == data and
			self.attrs == attrs):
			return 0
		else:
			return -1

	def __repr__(self):
		args = ", ".join(map(repr, [self.type, self.data, self.attrs]))
		return self.__class__.__name__+"(%s)" % args

