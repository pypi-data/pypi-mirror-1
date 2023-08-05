
# PullParser.py::refactored from JJLee's pullparser
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
# Copyright 2003-2004 John J. Lee <jjl@pobox.com> (pullparser.py)
# Copyright 1998-2001 Gisle Aas (original libwww-perl code under Perl Artistic License)
#

"""
A simple "pull API" for HTML parsing, after Perl's HTML::TokeParser.

Examples

1) This program extracts all links from a document.	 It will print one
line for each link, containing the URL and the textual description
between the <A>...</A> tags:

import PullParser, sys

f = file(sys.argv[1])
p = PullParser.PullParser(f)
for token in p.tags("a"):
	if token.type == "endtag": continue
	url = dict(token.attrs).get("href", "-")
	text = p.get_compressed_text(endat=("endtag", "a"))
	print "%s\t%s" % (url, text)

2) This program extracts the <TITLE> from the document:

import PullParser, sys
f = file(sys.argv[1])
p = PullParser.PullParser(f)
if p.get_tag("title"):
	title = p.get_compressed_text()
	print "Title: %s" % title

"""
from __future__ import generators		# allows us to run on pre 2.3
import re
import Token
from HTMLParser import HTMLParser
from exceptions import StopIteration
from htmlentitydefs import entitydefs
from mechanoid.misc.Consts import CHUNK
from mechanoid.misc.Errors import NoMoreTokensError

class PullParser(HTMLParser):
	COMPRESS_RE = re.compile(r"\s+")

	def __init__(self, fh, textify={"img": "alt", "applet": "alt"}, encoding="ascii"):
		"""
		fh: file-like object (only a .read() method is required) from
		which to read HTML to be parsed

		textify: mapping used by .get_text() and .get_compressed_text()
		methods to represent opening tags as text

		If the element name of an opening tag matches a key in the
		textify mapping then that tag is converted to text.	 The
		corresponding value is used to specify which tag attribute to
		obtain the text from.  textify maps from element names to
		either:

			- an HTML attribute name, in which case the HTML attribute
			value is used as its text value along with the element name
			in square brackets (eg."alt text goes here[IMG]", or, if the
			alt attribute were missing, just "[IMG]")

			- a callable object (eg. a function) which takes a Token and
			returns the string to be used as its text value

		If textify has no key for an element name, nothing is
		substituted for the opening tag.

		encoding: encoding used to encode numeric character references
		by .get_text() and .get_compressed_text() ("ascii" by default)
		
		"""
		HTMLParser.__init__(self)
		self._fh = fh
		self.textify = textify
		self.encoding = encoding
		self.entitydefs = entitydefs
		self._tokenstack = []  # FIFO
		return
		
	def __iter__(self):
		return self

	#
	# Private Methods
	#

	def __get_token(self, *tokentypes):
		while 1:
			while self._tokenstack:
				token = self._tokenstack.pop(0)
				if tokentypes:
					if token.type in tokentypes:
						return token
				else:
					return token
			data = self._fh.read(CHUNK)
			if not data:
				raise NoMoreTokensError()
			try:
				self.feed(data)
			except:
				pass
		return None
	
	# a clever and naughty way to vary the method of iteration		
	def __iter_until_exception(self, fn, exception, *args, **kwds):
		while 1:
			try:
				yield fn(*args, **kwds)
			except exception:
				raise StopIteration
		return

	def __unget_token(self, token):
		self._tokenstack.insert(0, token)
		return


	#
	# Public Methods
	#

	def next(self):
		"""
		__iter__ and next() allow iteration over a PullParser.
		See Python Tutorial 9.9 Iterators

		"""
		try:
			n = self.__get_token()
		except NoMoreTokensError:
			raise StopIteration()
		return n
	
	def get_tag(self, *names):
		"""
		Returns the next tag in names or simply the next tag.
		
		"""
		while 1:
			tok = self.__get_token()
			if tok.type not in ["starttag", "endtag", "startendtag"]:
				continue
			if names:
				if tok.data in names:
					return tok
			else:
				return tok

	def get_text(self, endat=None):
		"""
		Get some text.

		endat: stop reading text at this tag (the tag is included in the
		returned text); endtag is a tuple (type, name) where type is
		"starttag", "endtag" or "startendtag", and name is the element
		name of the tag (element names must be given in lower case)

		If endat is not given, get_text() will stop at the next opening
		or closing tag, or when there are no more tokens (no exception
		is raised).	 Note that get_text() includes the text
		representation (if any) of the opening tag, but pushes the
		opening tag back onto the stack.  As a result, if you want to
		call get_text() again, you need to call get_tag() first (unless
		you want an empty string returned when you next call
		get_text()).

		Entity references are translated using the entitydefs attribute
		(a mapping from names to characters like that provided by the
		standard module htmlentitydefs).  Named entity references that
		are not in this mapping are left unchanged.

		The textify attribute is used to translate opening tags into
		text: see the class docstring.

		"""
		text = []
		tok = None
		while 1:
			try:
				tok = self.__get_token()
			except NoMoreTokensError:
				# unget last token (not the one we just failed to get)
				if tok:
					self.__unget_token(tok)
				break
			if tok.type == "data":
				text.append(tok.data)
			elif tok.type == "entityref":
				name = tok.data
				if name in self.entitydefs:
					t = self.entitydefs[name]
				else:
					t = "&%s;" % name
				text.append(t)
			elif tok.type == "charref":
				name = tok.data
				try:
					t = unichr(int(name)).encode(self.encoding)
				except:	
					t = chr(int(name)).encode(self.encoding)
				text.append(t)
			elif tok.type in ["starttag", "endtag", "startendtag"]:
				tag_name = tok.data
				if tok.type in ["starttag", "startendtag"]:
					alt = self.textify.get(tag_name)
					if alt is not None:
						if callable(alt):
							text.append(alt(tok))
						elif tok.attrs is not None:
							for k, v in tok.attrs:
								if k == alt:
									text.append(v)
							text.append("[%s]" % tag_name.upper())
				if endat is None or endat == (tok.type, tag_name):
					self.__unget_token(tok)
					break
		text = "".join(text)		
		return text

	def get_compressed_text(self, *args, **kwds):
		"""
		As .get_text(), but collapses each group of contiguous
		whitespace to a single space character, and removes all initial
		and trailing whitespace.

		"""
		text = self.get_text(*args, **kwds)
		text = text.strip()
		return self.COMPRESS_RE.sub(" ", text)

	#
	# handle methods redefine HTMLParser parent class methods
	#

	def handle_startendtag(self, tag, attrs):
		self._tokenstack.append(Token.Token("startendtag", tag, attrs))

	def handle_starttag(self, tag, attrs):
		self._tokenstack.append(Token.Token("starttag", tag, attrs))

	def handle_endtag(self, tag):
		self._tokenstack.append(Token.Token("endtag", tag))

	def handle_charref(self, name):
		self._tokenstack.append(Token.Token("charref", name))

	def handle_entityref(self, name):
		self._tokenstack.append(Token.Token("entityref", name))

	def handle_data(self, data):
		self._tokenstack.append(Token.Token("data", data))

	def handle_comment(self, data):
		self._tokenstack.append(Token.Token("comment", data))

	def handle_decl(self, decl):
		self._tokenstack.append(Token.Token("decl", decl))

	def unknown_decl(self, data):
		self._tokenstack.append(Token.Token("decl", data))

	def handle_pi(self, data):
		self._tokenstack.append(Token.Token("pi", data))

	def tags(self, *names):
		return self.__iter_until_exception(self.get_tag, NoMoreTokensError, *names)

	def tokens(self, *tokentypes):
		return self.__iter_until_exception(self.__get_token, NoMoreTokensError, *tokentypes)

