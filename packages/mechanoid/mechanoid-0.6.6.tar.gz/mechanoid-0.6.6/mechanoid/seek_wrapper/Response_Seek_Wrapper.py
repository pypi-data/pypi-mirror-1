
# Response_Seek_Wrapper.py::refactored from JJLee's _Util
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
# Copyright 2004 Richard Harris (mechanoid fork of mechanize - see README)
# Copyright 2002-2003 John J Lee <jjl@pobox.com>

from Seek_Wrapper import Seek_Wrapper
from EOFFile import EOFFile

class Response_Seek_Wrapper(Seek_Wrapper):
	# XXX this is tampering with the wrapped class :-((

	# Implementation inheritance: this is NOT a proper subclass of
	# seek_wrapper.  This class can only wrap response objects of
	# urllib2.  It closes the socket while avoiding unnecessarily
	# clobbering methods.

	def close(self):
		if not isinstance(self.wrapped.fp, EOFFile):
			self.wrapped.fp.close()
			self.wrapped.fp = EOFFile()
