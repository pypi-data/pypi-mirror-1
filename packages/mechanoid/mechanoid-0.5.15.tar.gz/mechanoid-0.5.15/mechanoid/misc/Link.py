
# mechanoid.misc.Link.py::refactored from JJLee's mechanize
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
# Copyright 2004 Richard Harris (mechanoid fork of mechanize - see README)
# Copyright 2003-2004 John J. Lee <jjl@pobox.com> (mechanize based on Perl's WWW::Mechanize)
# Copyright 2003 Andy Lester (original Perl code)
#
import urlparse

class Link:
	def __init__(self, base_url, url, text, tag, attrs):
		assert None not in [url, tag, attrs]
		self.base_url = base_url
		self.absolute_url = urlparse.urljoin(base_url, url)
		self.url, self.text, self.tag, self.attrs = url, text, tag, attrs

	def __eq__(self, other):
		try:
			for name in "url", "text", "tag", "attrs":
				if getattr(self, name) != getattr(other, name):
					return False
		except AttributeError:
			return False
		return True

	def __repr__(self):
		return "Link(base_url=%r, url=%r, text=%r, tag=%r, attrs=%r)" % (
			self.base_url, self.url, self.text, self.tag, self.attrs)

