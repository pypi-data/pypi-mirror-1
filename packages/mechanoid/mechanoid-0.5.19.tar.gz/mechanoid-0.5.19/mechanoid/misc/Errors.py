
# mechanoid.misc.Errors.py::refactored from JJLee's original classes
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
# Copyright 2004 Richard Harris
# Copyright 2003-2004 John J. Lee <jjl@pobox.com>
#

# mechanoid.Browser
class BrowserStateError(Exception): pass
class LinkNotFoundError(Exception): pass
class FormNotFoundError(Exception): pass

# HTTPProcessors, HTTPProcessors_HeadParser
class EndOfHeadError(Exception): pass

# PullParser
class NoMoreTokensError(Exception): pass

# _ClientForm_FormParser
class ParseError(Exception): pass

# _ClientForm_HTMLControls
class ControlNotFoundError(ValueError): pass
class ItemNotFoundError(ValueError): pass
class ItemCountError(ValueError): pass

