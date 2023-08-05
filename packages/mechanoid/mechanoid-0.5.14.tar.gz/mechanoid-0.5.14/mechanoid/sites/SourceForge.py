
# www.sourceforge.net site class for mechanoid
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
import lib_rharris

class SourceForge:
	HOST = "https://sourceforge.net/account/login.php"
	QRS = "https://sourceforge.net/project/admin/qrs.php?package_id=&group_id="
	ADS="https://sourceforge.net/people/createjob.php?group_id="
	RESPONSE = os.path.expandvars("$HOME/sourceforge_debug.html")
	RETRIES = 5
	TYPE_IDS = {
		".deb":"1000",
		".rpm":"2000",
		".zip":"3000",
		".bz2":"3001",
		".gz":"3002",
		"Source .zip":"5000",
		"Source .bz2":"5001",
		"Source .gz":"5002",
		"Source .rpm":"5100",
		"Other Source File":"5900",
		".jpg":"8000",
		"text":"8001",
		"html":"8002",
		"pdf":"8003",
		"Other":"9999",
		".sit":"3003",
		".nbz":"3004",
		".exe (DOS)":"2500",
		".exe (16-bit Windows)":"2501",
		".exe (32-bit Windows)":"2502",
		".exe (OS/2)":"2600",
		".dmg":"3005",
		".jar":"2601",
		"Source Patch/Diff":"5901",
		".prc (PalmOS)":"2700",
		".iso":"3006",
		"Source .Z":"5003",
		".bin (MacBinary)":"2650",
		".ps (PostScript)":"8004",
		".msi (Windows installer)":"2503",
		"Other Binary Package":"4000",
		}
	PROCESSOR_IDS = {
		"i386":"1000",
		"IA64":"6000",
		"Alpha":"7000",
		"Any":"8000",
		"PPC":"2000",
		"MIPS":"3000",
		"Sparc":"4000",
		"UltraSparc":"5000",
		"Other":"9999",
		"Platform-Independent":"8500",
		"ARM":"3001",
		"SH3":"3002",
		"AMD64":"6001",
		"PPC64":"2001",
		}
	CATEGORY_IDS = {
		"Developer":"1",
		"Project Manager":"2",
		"Unix Admin":"3",
		"Doc Writer":"4",
		"Tester":"5",
		"Support Manager":"6",
		"Graphic Designer":"7",
		"DBA":"105",
		"Content Writer":"9",
		"Packager":"10",
		"Analysis":"11",
		"Advisor":"12",
		"Distributor":"13",
		"Content Management":"14",
		"Requirements":"15",
		"Web Designer":"16",
		"Porter":"17",
		"Translator":"8",
		"User Interface":"103",
		"Support":"104",
		}

	def __init__(self, browser, debug, verbose):
		self.lib = lib_rharris.lib_rharris()
		self.b = browser
		self.debug = debug
		self.verbose = verbose
		self.retries = 0
		self.base = ""
		self.delete = ""
		self.to_delete = []
		return
	
	def __log(self, msg):
		sys.stderr.write("SourceForge::Error: "+msg+"\n")
		f = open(os.path.expandvars("$HOME/sourceforge.error"),'a')
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

	def debug_response(self, response):
		self.b.debug_response(response, self.RESPONSE)
		return

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
			login = n.authenticators("sourceforge")
		except:
			self.usage()
		try:	
			self.b.select_form(nr=2)
		except:
			self.b.debug_forms()
			raise
		self.b["form_loginname"] = login[0]
		self.b["form_pw"] = login[2]
		if self.verbose: print "Logging into "+self.HOST+" as "+login[0]
		response = self.b.submit()
		if self.debug: self.b.debug_response(response, self.RESPONSE)
		return response

			
	def qrs(self, project):
		if (self.verbose): print "Connecting to Quick Release System"
		try:
			response = self.__get_response(self.QRS+project)
		except:
			print "Failed to reach QRS."
			raise
		return response
			
	def jobs(self, project):
		if (self.verbose): print "Connecting to Project Jobs Page"
		try:
			response = self.__get_response(self.ADS+project)
		except:
			print "Failed to reach jobs page."
			raise
		return response

