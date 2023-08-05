
# HTTPProcessors_HeadParser.py::refactored from JJLee's _urllib2_support
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
# Copyright 2002-2003 John J. Lee <jjl@pobox.com>
#

import HTMLParser
from mechanoid.misc.Errors import EndOfHeadError

class AbstractHeadParser:
	# only these elements are allowed in or before HEAD of document
	head_elems = ("html", "head", "title", "base",
				  "script", "style", "meta", "link", "object")

	def __init__(self):
		self.http_equiv = []

	def start_meta(self, attrs):
		http_equiv = content = None
		for key, value in attrs:
			if key == "http-equiv":
				http_equiv = value
			elif key == "content":
				content = value
		if http_equiv is not None:
			self.http_equiv.append((http_equiv, content))

	def end_head(self):
		raise EndOfHeadError()

# use HTMLParser if we have it (it does XHTML), htmllib otherwise
class HeadParser(AbstractHeadParser, HTMLParser.HTMLParser):
	# Definition of entities -- derived classes may override
	entitydefs = {'lt': '<', 'gt': '>', 'amp': '&', 'quot': '"', 'apos': '\''}

	def __init__(self):
		HTMLParser.HTMLParser.__init__(self)
		AbstractHeadParser.__init__(self)

	def handle_starttag(self, tag, attrs):
		if tag not in self.head_elems:
			raise EndOfHeadError()
		try:
			method = getattr(self, 'start_' + tag)
		except AttributeError:
			try:
				method = getattr(self, 'do_' + tag)
			except AttributeError:
				pass # unknown tag
			else:
				method(attrs)
		else:
			method(attrs)

	def handle_endtag(self, tag):
		if tag not in self.head_elems:
			raise EndOfHeadError()
		try:
			method = getattr(self, 'end_' + tag)
		except AttributeError:
			pass # unknown tag
		else:
			method()

	# handle_charref, handle_entityref and default entitydefs are taken
	# from sgmllib
	def handle_charref(self, name):
		try:
			n = int(name)
		except ValueError:
			self.unknown_charref(name)
			return
		if not 0 <= n <= 255:
			self.unknown_charref(name)
			return
		self.handle_data(chr(n))

	def handle_entityref(self, name):
		table = self.entitydefs
		if name in table:
			self.handle_data(table[name])
		else:
			self.unknown_entityref(name)
			return

	def unknown_entityref(self, ref):
		self.handle_data("&%s;" % ref)

	def unknown_charref(self, ref):
		self.handle_data("&#%s;" % ref)


