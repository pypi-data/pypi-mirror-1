
# www.freshmeat.net site class for mechanoid
# truenolejano@yahoo.com
# http://cheeseshop.python.org

# Copyright (C) 2005 by Richard Harris
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


import os, sys, string, netrc, time, urllib, traceback

class FreshMeat:
	HOST = "http://freshmeat.net/my"
	RESPONSE = os.path.expandvars("$HOME/freshmeat_debug.html")
	RETRIES = 5

	def __init__(self, browser, debug, verbose):
		self.b = browser
		self.debug = debug
		self.verbose = verbose
		self.retries = 0
		self.base = ""
		self.delete = ""
		self.to_delete = []
		return
	
	def __log(self, msg):
		sys.stderr.write(msg+"\n")
		f = open(os.path.expandvars("$HOME/freshmeat.error"),'a')
		f.write(time.asctime())
		f.write(msg+"\n")
		info = sys.exc_info()
		traceback.print_tb(info[2], None, f)
		f.close()
		sys.exit()
		return

	def __get_response(self, url, data=None):
		response = None
		try:
			response = self.b.open(url, data)
			if self.debug: self.b.debug_response(response, self.RESPONSE)
		except:
			if (0): raise				# DEBUG SWITCH
			self.retries += 1
			if (self.retries < self.RETRIES):
				response = self.__get_response(url)
		return response

	#
	# PUBLIC METHODS
	#

	def go_to(self):
		if self.verbose: print "Connecting to "+self.HOST
		try:
			response = self.__get_response(self.HOST)
			if self.debug: self.b.debug_response(response, self.RESPONSE)
		except:
			self.__log( "\Error::Failed to reach "+ self.HOST)
			raise
		return response

	def log_in(self):
		n = netrc.netrc()
		try:
			login = n.authenticators("freshmeat")
		except:
			self.usage()
		self.b.select_form(nr=2)
		self.b["username"] = login[0]
		self.b["password"] = login[2]
		if self.verbose: print "Logging into "+self.HOST+" as "+login[0]
		response = self.b.submit()
		return response

