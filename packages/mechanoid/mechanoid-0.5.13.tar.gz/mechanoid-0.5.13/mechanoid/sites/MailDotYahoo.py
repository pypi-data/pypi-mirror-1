
# mail.yahoo.com site class for mechanoid
# goosequill@users.sourceforge.net
# http://goosequill.sourceforge.net

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


import os, sys, netrc, time, urllib, traceback
import lib_rharris

class MailDotYahoo:
	DEL="&DEL=Delete"
	HOST = "mail.yahoo.com"
	RESPONSE = os.path.expandvars("$HOME/maildotyahoo_debug.html")
	RETRIES = 5

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
		sys.stderr.write(msg+"\n")
		f = open(os.path.expandvars("$HOME/mail.yahoo.error"),'a')
		f.write(time.asctime())
		f.write(msg+"\n")
		info = sys.exc_info()
		traceback.print_tb(info[2], None, f)
		f.close()
		sys.exit()
		return

	def __get_param(self, url, p):
		tmp = url.split("?")[1]
		tmp = tmp.split("&")
		d = {}
		for entry in tmp:
			set = entry.split("=")
			d[set[0]] = set[1]
		try:
			param = d[p]
		except:
			param = None
		return param

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
			response = self.__get_response("http://"+self.HOST)
		except:
			self.__log( "\nError::Failed to reach "+ self.HOST)
			raise
		return response

	def log_in(self):

		# load non-javascript user page
		def is_js(response):
			lines = response.readlines()
			for line in lines:
				if (line.find('/ym/login?nojs=1') != -1):
					return 1
				elif (line.find('</head>') != -1):
					break
			return 0

		def get_data(response):
			found = ""
			lines = response.readlines()
			for line in lines:
				if (line.find("Switch back to the old version") != -1):
					found = line
					break
			found = found.split("?")[-1]
			found = found.split('"')[0]
			tokens = found.split("&")
			dict = {}
			for token in tokens:
				duo = token.split("=")
				dict[duo[0]] = duo[1]
			return dict	

		# log_in main
		self.params, self.options = self.lib.get_args()
		if ("passwd" in self.options):
			passwd = self.options[self.options.index("passwd") + 1]
			user = self.options[self.options.index("user") + 1]
			login = (user, "yahoo", passwd)
		else:	
			n = netrc.netrc()
			try:
				login = n.authenticators(self.HOST)
			except:
				self.__log( "\nsend_yahoo::Read of ~/.netrc failed. Exiting...")
				if self.debug: raise
		if (0): self.b.debug_forms()	# DEBUG SWITCH
		forms = self.b.forms()
		for i in range(0, len(self.b.forms())):
			try:
				if forms[i].has_control("passwd"):
					self.b.select_form(nr=i)
					self.b["login"] = login[0]
					self.b["passwd"] = login[2]
					break
			except:
				continue				# XXX HTMLForm.__find_control throws exception
		try:	
			if self.verbose: print "Logging into "+self.HOST+" as "+login[0]
			response = self.b.submit()
			if self.debug: self.b.debug_response(response, self.RESPONSE)
		except:
			self.__log( "\nsend_yahoo::Failed to log in.")
			if (self.debug): raise
		# follow redirect
		if self.verbose: print "Redirected to User Page"
		response = self.b.follow_link(text="click here")
		if self.debug: self.b.debug_response(response, self.RESPONSE)
		if (is_js(response)):
			if self.verbose: print "Requesting non-javascript page."
			host = self.b.request.get_host()
			response = self.__get_response("http://"+host+"/ym/login?nojs=1")
			if self.debug: self.b.debug_response(response, self.RESPONSE)
			data = urllib.urlencode(get_data(response))
			url = "http://"+ self.b.request.get_host() + "/ym/BetaSwitcher"
			response = self.__get_response(url, data)
			if self.debug: self.b.debug_response(response, self.RESPONSE)
		return response

	#
	# Sending Email
	#
	
	def compose(self):
		if self.verbose: print "Requesting Compose-Email page"
		response = self.b.follow_link(text="Compose")
		if self.debug: self.b.debug_response(response, self.RESPONSE)
		return response

 	def send_mail(self, to, cc, bcc, subject, text):
		self.b.select_form(nr=0)
		self.b["To"] = to
		self.b["Cc"] = cc
		self.b["Bcc"] = bcc
		self.b["Subj"] = subject
		self.b["Body"] = text
		response = self.b.submit(name="SEND")
		if self.debug: self.b.debug_response(response, self.RESPONSE)
		return response
		
	def check_response(self, response):
		error = 0
		lines = response.readlines()
		for line in lines:
			if (line.find("there was a problem") != -1):
				error = 1
				break
		if (error):
			if self.debug: self.b.debug_response(response, self.RESPONSE)
			self.__log("\nsend_yahoo::Email to "+to+" was not sent.\n")
		else:
			if (self.debug): print "Response OK"
		return

	#
	# Fetching Email
	#
	
	def __fix_msg(self, response):

		def format(msg):

			def indices(line):
				line = line.strip()
				c = line.find(":")
				s = line.find(" ")
				if (c == -1): s = -1
				return c, s
				
			new = []
			last = boundary = ""
			headers = 1
			one = 0
			for line in msg:
				line = line.replace("&nbsp;"," ") 
				test = line.strip()
				if not ((last == "") and (test == last)):  # remove multiple newlns
					# --- all lines ---
					line = line.replace("&lt;","<")
					line = line.replace("&gt;",">")
					line = line.replace("&#34;","\"")
					# --- header lines ---
					if (headers): 
						line = line.strip()
						# Yahoo's From line
						if (line.find("X-Apparently-To:") != -1):
							line = "X-Apparently-To:"+ line.split("X-Apparently-To:")[1]
							one = 1
						if (line.find("Yahoo! DomainKeys has confirmed") != -1):
							line = line.split("Yahoo!")[0]
						c, s = indices(line)	
						if (c < s) or one:
							new.append(line) # only mime header lines
							one = 0
							if (line.find("Content-Length:") == 0): headers = 0
					# --- body lines ---	
					else:	
						# Mime boundary	
						if ((line.find("-") == 0) and
							(line.find(" ") == -1) and
							(len(line) > 3) and
							(boundary == "")):
							boundary = (line.replace("-","")).strip()
						line = line.replace("\n","")
						new.append(line)
					last = line
			if (boundary != ""):
				for i in range(0, len(new)):
					if ((new[i].find("Content-Type:") == 0) and
						(new[i].find("multipart/mixed") == -1)):
						new[i] = 'Content-Type: multipart/mixed; boundary="'+boundary+'"'
						break
			return new

		def from_line(new):

			def __date():
				dt = time.asctime()
				dt = dt.replace("  "," ")
				return dt

			def __address(new, str):
				ad = ""
				for line in new:
					if (line.find(str) != -1):
						ad = line.replace(str,"")
						if (ad.find("Yahoo! DomainKeys has confirmed") != -1):
							ad = ad.split("Yahoo!")[0]
						if (ad.find("\"") != -1):
							ad = ad.split("\"")[2]
						ad = ad.strip()	
						ad = ad.replace("<","")
						ad = ad.replace(">","")
						break
				return ad	

			dt = __date()
			ad = __address(new, "From:")
			if (ad == ""):
				ad = self.__address(new, "Reply-to:")
			if (ad == ""):
				ad = self.__address(new, "Return-Path:")
			if (ad == ""):
				ad = "goosequill@users.sourceforge.net"
			return "From "+ad+" "+dt

		# fix_msg main
		msg = self.lib.strip_html(response.read())
		msg = msg.split("\n")
		new = format(msg)
		new = [from_line(new)]+new
		if (self.verbose): print "  "+new[0]
		new = "\n".join(new)+"\n\n"	
		return new

	def inbox(self):

		def set_delete(response):
			data = self.lib.html_canonical(response)
			lines = data.readlines()
			index = self.lib.find_line(lines,"<form")
			form = lines[index].replace(">","")
			form = form.replace("\"","")
			tmp = self.lib.tokens(form)[1:]
			for i in tmp:
				if (i.find("action") != -1):
					url = i.split("=",1)[1]
					self.delete = url + self.DEL
					break
			crumb = self.lib.find_line(lines,".crumb")
			crumb = lines[crumb].replace("\"","")
			crumb = crumb.replace(">"," ")
			tmp = self.lib.tokens(crumb)
			for i in tmp:
				if (i.find("value") != -1):
					c = i.split("=",1)[1]
					self.delete = self.delete + "&.crumb="+c

		if self.verbose: print "Requesting Inbox page"
		response = self.b.follow_link(text="Go to Inbox")
		if self.debug: self.b.debug_response(response, self.RESPONSE)
		if (self.delete == ""):
			set_delete(response)
		# load messages
		self.messages = []
		for link in self.b.links():
			if ((link.url.find("ShowLetter") != -1) and
				(link.url.find("toc=1") == -1)
				):
				if (self.base == ""):
					self.base = link.base_url.split("/ym")[0]
				url = self.base+link.url+"&PRINT=1&Nhead=f"
				self.messages.append(url)
				if (0): print url		# DEBUG SWITCH
		return response

	def fetch_mail(self, mbox, dir):

		def append(new):
			f = open(mbox,'a')
			f.write(new)
			f.close()

		def attachments():
			a = []
			for link in self.b.links():
				if (link.url.find("download=1") != -1):
					base = link.base_url.split("/ym")[0]
					url = base+link.url
					a.append(url)
			return a

		def download(attached):
			for link in attached:
				fname = self.__get_param(link,"filename")
				fname = fname.replace("%5f","-")
				dnld = 1
				if (self.verbose):
					choice = "?"
					while (choice not in ["n","y"]):
						choice = raw_input("Download "+fname+"(y/n):")
					if (choice == "n"):
						self.to_delete.remove(self.__get_param(link,"MsgId"))
						dnld = 0
				if (dnld):
					response = self.__get_response(link)
					if (response == None):
						if (self.verbose):
							print "**  Failed to download "+fname+" **"
						self.to_delete.remove(self.__get_param(link,"MsgId"))
					else:
						f = open(dir+os.sep+fname,'w')
						f.write(response.read())
						f.close()

		def delete():
			
			def check_response(response):
				error = 0
				if (response == None): error = 1
				else:	
					lines = response.readlines()
					for line in lines:
						if (line.find("there was a problem") != -1):
							error = 1
							break
				if (error): print "Error in deleting messages."

			# delete main	
			count = len(self.to_delete)
			if (count > 0):
				if self.verbose: print "Deleting "+`count`+" Messages"
				d = self.base+self.delete
				for mid in self.to_delete:
					d += "&Mid="+mid
				tmp = d.split("?")
				url = tmp[0]
				data = tmp[1]
				response = self.__get_response(url, data)
				check_response(response)

		# fetch_mail main
		count = len(self.messages)
		if self.verbose: print "Downloading "+`count`+" Messages"
		for url in self.messages:
			response = self.__get_response(url)
			if (response == None):
				print "**  Failed to retrieve message. **"
				continue
			self.to_delete.append(self.__get_param(url,"MsgId"))
			new = self.__fix_msg(response)
			append(new)
			download(attachments())
		delete()	
		return
