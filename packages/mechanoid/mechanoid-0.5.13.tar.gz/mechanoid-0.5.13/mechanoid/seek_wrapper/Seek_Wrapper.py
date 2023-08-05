
# Seek_Wrapper.py::refactored from JJLee's _Util
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
# Copyright 2004 Richard Harris (mechanoid fork of mechanize - see README)
# Copyright 2002-2003 John J Lee <jjl@pobox.com>


# JJL:XXX Andrew Dalke kindly sent me a similar class in response to my
# request on comp.lang.python, which I then proceeded to lose.	I wrote
# this class instead, but I think he's released his code publicly since,
# could pinch the tests from it, at least...
from StringIO import StringIO

class Seek_Wrapper:
	"""
	Adds a seek method to a file object. This is intended for seeking on
	readonly file-like objects.

	Wrapped file-like object must have a read method.  The readline
	method is only supported if that method is present on the wrapped
	object.	 The readlines method is always supported.	xreadlines and
	iteration are supported only for Python 2.2 and above.

	Public attribute: wrapped (the wrapped file object).

	WARNING: All other attributes of the wrapped object (ie. those that
	are not one of wrapped, read, readline, readlines, xreadlines,
	__iter__ and next) are passed through unaltered, which may or may
	not make sense for your particular file object.

	"""

	# General strategy is to check that cache is full enough, then delegate
	# everything to the cache (self._cache, which is a StringIO.StringIO
	# instance.	 

	# Invariant: the end of the cache is always at the same place as the
	# end of the wrapped file:
	# self.wrapped.tell() == len(self._cache.getvalue())

	def __init__(self, wrapped):
		self.wrapped = wrapped
		self.__have_readline = hasattr(self.wrapped, "readline")
		self.__cache = StringIO()

	def __getattr__(self, name): return getattr(self.wrapped, name)

	def seek(self, offset, whence=0):
		# make sure we have read all data up to the point we are seeking to
		pos = self.__cache.tell()
		if whence == 0:	 # absolute
			to_read = offset - pos
		elif whence == 1:  # relative to current position
			to_read = offset
		elif whence == 2:  # relative to end of *wrapped* file
			# since we don't know yet where the end of that file is, we must
			# read everything
			to_read = None
		if to_read is None or to_read >= 0:
			if to_read is None:
				self.__cache.write(self.wrapped.read())
			else:
				self.__cache.write(self.wrapped.read(to_read))
			self.__cache.seek(pos)

		return self.__cache.seek(offset, whence)

	def read(self, size=-1):
		pos = self.__cache.tell()

		self.__cache.seek(pos)

		end = len(self.__cache.getvalue())
		available = end - pos

		# enough data already cached?
		if size <= available and size != -1:
			return self.__cache.read(size)

		# no, so read sufficient data from wrapped file and cache it
		to_read = size - available
		assert to_read > 0 or size == -1
		self.__cache.seek(0, 2)
		if size == -1:
			self.__cache.write(self.wrapped.read())
		else:
			self.__cache.write(self.wrapped.read(to_read))
		self.__cache.seek(pos)

		return self.__cache.read(size)

	def readline(self, size=-1):
		if not self.__have_readline:
			raise NotImplementedError("No readline method on wrapped object.")

		# line we're about to read might not be complete in the cache, so
		# read another line first
		pos = self.__cache.tell()
		self.__cache.seek(0, 2)
		self.__cache.write(self.wrapped.readline())
		self.__cache.seek(pos)

		data = self.__cache.readline()
		if size != -1:
			r = data[:size]
			self.__cache.seek(pos+size)
		else:
			r = data
		return r

	def readlines(self, sizehint=-1):
		pos = self.__cache.tell()
		self.__cache.seek(0, 2)
		self.__cache.write(self.wrapped.read())
		self.__cache.seek(pos)
		return self.__cache.readlines(sizehint)

	def __iter__(self): return self
	def next(self):
		line = self.readline()
		if line == "": raise StopIteration
		return line

	xreadlines = __iter__

	def __repr__(self):
		return ("<%s at %s whose wrapped object = %s>" %
				(self.__class__.__name__, `id(self)`, `self.wrapped`))

	def close(self):
		self._cache = None
		self.read = None
		self.readline = None
		self.readlines = None
		self.seek = None
		if self.wrapped: self.wrapped.close()
		self.wrapped = None

