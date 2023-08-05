
# cookiejar.Header_Utils.py::refactored from JJLee's _urllib2_support
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
# Copyright 1997-1998, Gisle Aas
#

"""
Utility functions for HTTP header value parsing and construction.

"""

import re, string, time
from types import StringType, UnicodeType
from mechanoid.misc.Common import Common
from mechanoid.misc.Consts import MONTHS_LOWER
from calendar import timegm

class Header_Utils:
	
	def __init__(self):
		self.join_escape_re	 = re.compile(r"([\"\\])")
		self.strict_re       = re.compile(
			r"^[SMTWF][a-z][a-z], (\d\d) ([JFMASOND][a-z][a-z]) (\d\d\d\d) (\d\d):(\d\d):(\d\d) GMT$")
		self.wkday_re        = re.compile(
			r"^(?:Sun|Mon|Tue|Wed|Thu|Fri|Sat)[a-z]*,?\s*", re.I)
		self.loose_http_re   = re.compile(
			r"""^
			(\d\d?)			   # day
			(?:\s+|[-\/])
			(\w+)			   # month
			(?:\s+|[-\/])
			(\d+)			   # year
			(?:
			(?:\s+|:)	       # separator before clock
			(\d\d?):(\d\d)	   # hour:min
			(?::(\d\d))?	   # optional seconds
			)?				   # optional clock
			\s*
			([-+]?\d{2,4}|(?![APap][Mm]\b)[A-Za-z]+)? # timezone
			\s*
			(?:\(\w+\))?	   # ASCII representation of timezone in parens.
			\s*$""", re.X)
		self.common = Common()
		return

	def http2time(self, text):
		"""Returns time in seconds since epoch of time represented by a string.

		Return value is an integer.

		None is returned if the format of str is unrecognized, the time is outside
		the representable range, or the timezone string is not recognized.	If the
		string contains no timezone, UTC is assumed.

		The timezone in the string may be numerical (like "-0800" or "+0100") or a
		string timezone (like "UTC", "GMT", "BST" or "EST").  Currently, only the
		timezone strings equivalent to UTC (zero offset) are known to the function.

		The function loosely parses the following formats:

		Wed, 09 Feb 1994 22:23:32 GMT		-- HTTP format
		Tuesday, 08-Feb-94 14:15:29 GMT		-- old rfc850 HTTP format
		Tuesday, 08-Feb-1994 14:15:29 GMT	-- broken rfc850 HTTP format
		09 Feb 1994 22:23:32 GMT			-- HTTP format (no weekday)
		08-Feb-94 14:15:29 GMT				-- rfc850 format (no weekday)
		08-Feb-1994 14:15:29 GMT			-- broken rfc850 format (no weekday)

		The parser ignores leading and trailing whitespace.	 The time may be
		absent.

		If the year is given with only 2 digits, the function will select the
		century that makes the year closest to the current date.

		"""
		# fast exit for strictly conforming string
		m = self.strict_re.search(text)
		if m:
			g = m.groups()
			mon = MONTHS_LOWER.index(string.lower(g[1])) + 1
			tt = (int(g[2]), mon, int(g[0]),
				  int(g[3]), int(g[4]), float(g[5]))
			return self.common.my_timegm(tt)

		# No, we need some messy parsing...

		# clean up
		text = string.lstrip(text)
		text = self.wkday_re.sub("", text, 1)  # Useless weekday

		# tz is time zone specifier string
		day, mon, yr, hr, min, sec, tz = [None]*7

		# loose regexp parse
		m = self.loose_http_re.search(text)
		if m is not None:
			day, mon, yr, hr, min, sec, tz = m.groups()
		else:
			return None	 # bad format

		return self.common.str2time(day, mon, yr, hr, min, sec, tz)

	def split_header_words(self, header_values):
		result = self.common.split_header_words(header_values)
		return result

	def join_header_words(self, lists):
		"""Do the inverse of the conversion done by split_header_words.

		Takes a list of lists of (key, value) pairs and produces a single header
		value.	Attribute values are quoted if needed.

		>>> import Header_Utils
		>>> h = Header_Utils.Header_Utils()
		>>> h.join_header_words([[("text/plain", None), ("charset", "iso-8859/1")]])
		'text/plain; charset="iso-8859/1"'
		>>> h.join_header_words([[("text/plain", None)], [("charset", "iso-8859/1")]])
		'text/plain, charset="iso-8859/1"'

		"""
		headers = []
		for pairs in lists:
			attr = []
			for k, v in pairs:
				if v is not None:
					if not re.search(r"^\w+$", v):
						v = self.join_escape_re.sub(r"\\\1", v)	 # escape " and \
						v = '"%s"' % v
					if k is None:  # Netscape cookies may have no name
						k = v
					else:
						k = "%s=%s" % (k, v)
				attr.append(k)
			if attr: headers.append(string.join(attr, "; "))
		return string.join(headers, ", ")

	def parse_ns_headers(self, ns_headers):
		"""Ad-hoc parser for Netscape protocol cookie-attributes.

		The old Netscape cookie format for Set-Cookie can for instance contain
		an unquoted "," in the expires field, so we have to use this ad-hoc
		parser instead of split_header_words.

		XXX This may not make the best possible effort to parse all the crap
		that Netscape Cookie headers contain.  Ronald Tschalar's HTTPClient
		parser is probably better, so could do worse than following that if
		this ever gives any trouble.

		Currently, this is also used for parsing RFC 2109 cookies.

		"""
		known_attrs = ("expires", "domain", "path", "secure",
					   # RFC 2109 attrs (may turn up in Netscape cookies, too)
					   "port", "max-age")

		result = []
		for ns_header in ns_headers:
			pairs = []
			version_set = False
			for param in re.split(r";\s*", ns_header):
				param = string.rstrip(param)
				if param == "": continue
				if "=" not in param:
					if string.lower(param) in known_attrs:
						k, v = param, None
					else:
						# cookie with missing name
						k, v = None, param
				else:
					k, v = re.split(r"\s*=\s*", param, 1)
					k = string.lstrip(k)
				if k is not None:
					lc = string.lower(k)
					if lc in known_attrs:
						k = lc
					if k == "version":
						# This is an RFC 2109 cookie.  Will be treated as RFC 2965
						# cookie in rest of code.
						# Probably it should be parsed with split_header_words, but
						# that's too much hassle.
						version_set = True
					if k == "expires":
						# convert expires date to seconds since epoch
						if self.common.startswith(v, '"'): v = v[1:]
						if self.common.endswith(v, '"'): v = v[:-1]
						v = self.http2time(v)  # None if invalid
				pairs.append((k, v))

			if pairs:
				if not version_set:
					pairs.append(("version", "0"))
				result.append(pairs)

		return result



