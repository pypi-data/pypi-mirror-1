
# OpenerDirector.py::refactored from JJLee's _urllib2_support
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

import string, urllib2
from Request import Request
from Common import Common

class OpenerDirector(urllib2.OpenerDirector):
	def __init__(self):
		urllib2.OpenerDirector.__init__(self)
		self.process_response = {}
		self.process_request = {}
		self.common = Common()
		return

	def __insort(self, a, x, lo=0, hi=None, lt=lambda x,y: x<y):
		if hi is None:
			hi = len(a)
		while lo < hi:
			mid = divmod((lo+hi), 2)[0]
			if lt(x, a[mid]): hi = mid
			else: lo = mid+1
		a.insert(lo, x)
		return

	# hacks below are to distinguish HTTPRedirectHandler from a Processor
	# because they both have redirect_request() method
	def add_handler(self, handler):
		added = False
		for meth in dir(handler):
			i = string.find(meth, "_")
			protocol = meth[:i]
			condition = meth[i+1:]
			if self.common.startswith(condition, "error"):
				j = string.find(meth[i+1:], "_") + i + 1
				kind = meth[j+1:]
				try:
					kind = int(kind)
				except ValueError:
					pass
				map = self.handle_error.get(protocol, {})
				self.handle_error[protocol] = map
				processor = False
			elif (condition == "open" and protocol != "do"):  # hack
				map = self.handle_open
				kind = protocol
				processor = False
			elif (condition in ["response", "request"] and protocol != "redirect"):	# hack
				map = getattr(self, "process_"+condition)
				kind = protocol
				processor = True
			else:
				continue
			if map.has_key(kind):
				if processor:
					#XXX But order is always 500 ???
					lt = lambda x,y: x.processor_order < y.processor_order
				else:
					lt = lambda x,y: x < y
				self.__insort(map[kind], handler, lt=lt)
			else:
				map[kind] = [handler]
			added = True
			continue
		if added:
			self.handlers.append(handler) #XXX was bisect.insort()
			handler.add_parent(self)
		return	

	def get_request(self, url_or_req, data):
		if self.common.isstringlike(url_or_req):
			req = Request(url_or_req, data)
		else: # already a urllib2.Request instance
			req = url_or_req
			if data is not None:
				req.add_data(data)
		return req

	def open(self, fullurl, data=None):
		req = self.get_request(fullurl, data)
		try:
			type_ = req.get_type()
		except:
			type_ = "http"	  
		# pre-process request
		meth_name = type_+"_request"
		# XXX should we allow a Processor to change the type
		# (URL scheme) of the request?
		for processor in self.process_request.get(type_, []):
			meth = getattr(processor, meth_name)
			req = meth(req)
		# get response
		try:
			response = urllib2.OpenerDirector.open(self, req, data)
		except:
			print "mechanoid error: "+req.get_full_url()
			raise
		# post-process response
		meth_name = type_+"_response"
		for processor in self.process_response.get(type_, []):
			meth = getattr(processor, meth_name)
			response = meth(req, response)
		return response

	def error(self, proto, *args):
		"""
		http[s] protocols are special-cased
		but are handled in the same way

		"""
		results = None
		if proto in ['http', 'https']:
			dict = self.handle_error['http'] 
			proto = args[2]
			meth_name = 'http_error_%s' % proto
			http_err = 1
			orig_args = args
		else:
			dict = self.handle_error
			meth_name = proto + '_error'
			http_err = 0
		args = (dict, proto, meth_name) + args
		result = apply(self._call_chain, args)
		if result:
			return result
		elif http_err:
			args = (dict, 'default', 'http_error_default') + orig_args
			results = apply(self._call_chain, args)
		return results
