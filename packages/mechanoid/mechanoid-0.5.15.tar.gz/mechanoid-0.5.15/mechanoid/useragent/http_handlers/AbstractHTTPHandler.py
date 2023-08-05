
# AbstractHTTPHandler.py::refactored from JJLee's _urllib2_support
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
# Copyright 2004 Richard Harris (mechanoid fork under GNU GPL)
# Copyright 2002-2003 John J. Lee <jjl@pobox.com>
#

"""

Base class for HTTP handlers

jjl::Note the absence of redirect and header-adding code and the lack of
other clutter that would be here without Processors.

"""
import string, socket, urllib, urllib2

class AbstractHTTPHandler(urllib2.BaseHandler):
	processor_order = 500

	def __init__(self):
		self.__debuglevel = 0
		return

	def do_open(self, http_class, req):
		"""
		Determines GET or POST from req, opens
		connection and returns response.

		"""
		host = req.get_host()
		if not host:
			raise urllib2.URLError('no host given')

		h = http_class(host) # will parse host:port
		h.set_debuglevel(self.__debuglevel)

		if req.has_data():
			h.putrequest('POST', req.get_selector())
		else:
			h.putrequest('GET', req.get_selector())

		headers = [req.headers, req.unredirected_hdrs]
		for header in headers:
			for key in header.keys():
				h.putheader(key, header[key])
			
		# httplib will attempt to connect() here.  Be prepared
		# to convert a socket error to a urllib2.URLError.

		try:
			h.endheaders()
		except socket.error, err:
			raise urllib2.URLError(err)

		if req.has_data():
			h.send(req.get_data())

		code, msg, hdrs = h.getreply()
		fp = h.getfile()

		response = urllib.addinfourl(fp, hdrs, req.get_full_url())
		response.code = code
		response.msg = msg

		return response

	def do_request_(self, request):
		"""
		Sets up Content* headers for POST request as
		well as other headers and returns request object.

		"""
		host = request.get_host()
		if not host:
			raise urllib2.URLError('no host given')

		if request.has_data():	# POST
			data = request.get_data()
			if not request.has_header('Content-type'):
				request.add_unredirected_header(
					'Content-type',
					'application/x-www-form-urlencoded')
			if not request.has_header('Content-length'):
				request.add_unredirected_header(
					'Content-length', '%d' % len(data))

		scheme, sel = urllib.splittype(request.get_selector())
		sel_host, sel_path = urllib.splithost(sel)

		if not request.has_header('Host'):
			request.add_unredirected_header('Host', sel_host or host)

		for name, value in self.parent.addheaders:
			name = string.capitalize(name)
			if not request.has_header(name):
				request.add_unredirected_header(name, value)

		return request

	def set_http_debuglevel(self, level):
		"""
		Sets debuglevel on HTTP open()

		"""
		self.__debuglevel = level
		return
