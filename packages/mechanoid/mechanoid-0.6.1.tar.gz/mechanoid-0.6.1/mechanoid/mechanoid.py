
# mechanoid.py::refactored from JJLee's mechanize
# The continuing story of stateful programmatic WWW navigation
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
# Copyright 2003-2004 John J. Lee <jjl@pobox.com> (mechanize based on Perl's WWW::Mechanize)
# Copyright 2003 Andy Lester (original Perl code)
#

import os, re, urlparse
from clientform.ClientForm import ClientForm
from http_processors.HTTPProcessors import HTTPRequestUpgradeProcessor
from misc.Common import Common
from misc.Errors import BrowserStateError, FormNotFoundError, LinkNotFoundError, NoMoreTokensError
from misc.Link import Link
from misc.OpenerDirector import OpenerDirector
from misc.Request import Request
from seek_wrapper.Response_Seek_Wrapper import Response_Seek_Wrapper
from pullparser.PullParser import PullParser
from useragent.UserAgent import UserAgent

class Browser(UserAgent):
	"""Browser-like class with support for history, forms and links.

	BrowserStateError is raised whenever the browser is in the wrong state to
	complete the requested operation - eg., when .back() is called when the
	browser history is empty, or when .follow_link() is called when the current
	response does not contain HTML data.

	Public attributes:

	request: last request (mechanoid.misc.Request or urllib2.Request)

	response: last response (as return value of urllib2.urlopen())

	form: currently selected form (see .select_form())

	default_encoding: character encoding used for encoding numeric
	character references when matching link text, if no encoding is
	found in the reponse (you should turn on HTTP-EQUIV handling if you
	want the best chance of getting this right without resorting to this
	default)

	"""
	URLTAGS = {
		"a": "href",
		"area": "href",
		"frame": "src",
		"iframe": "src",
	}

	NOT_HTML = "Current page is not HTML."
	NO_DOC   = "No document is loaded."
	KEYWDS   = "Call this method with keywords, not args."

	def __init__(self, default_encoding="latin-1"):
		self.debug = 0
		self.default_encoding = default_encoding
		self.request = self.response = None
		self.form = None
		self.__history = []	# LIFO
		self.__forms = None
		self.__links = None
		self.clientform = ClientForm()
		self.common = Common()
		self.pwd = "" # for local files
		self.last_scheme = ("http") # default
		self.last_host = ""
		self.last_action = ""
		self.handle_referer = True
		UserAgent.__init__(self)  # do this last to avoid __getattr__ problems

	def __getattr__(self, name):
		# jjl::pass through ClientForm / DOMForm methods and attributes
		# XXX This negates self's attributes by assuming we only care about the form.
		# We need to "try" the form first and then check self on "except".
		# So the hacks in OpenerDirector.add_handler have to be rationalized.
		if self.form is not None:
			try:
				return getattr(self.form, name)
			except AttributeError: pass
		raise AttributeError("%s instance has no attribute %s "
							 "Perhaps you forgot to .select_form()?" %
							 (self.__class__, name))

	#
	# Private methods
	#

	def __add_referer_header(self, request):
		# reasons not to add header
		if self.request is None:
			return request
		try:
			scheme = request.get_type()
		except: # rh::fall back on "http" rather than error-out
			scheme = "http"
		if scheme not in ["http", "https"]:
			return request
		# add referer header
		request = HTTPRequestUpgradeProcessor().http_request(request)
		previous_scheme = self.request.get_type()
		if (self.handle_referer and
			(previous_scheme in ["http", "https"]) and 
			not ((previous_scheme == "https") and (scheme != "https"))):
			request.add_unredirected_header("Referer", self.request.get_full_url())
		return request

	def __encoding(self, response):
		# HTTPEquivProcessor may be in use, so both HTTP and HTTP-EQUIV
		# headers may be in the response.
		ct_headers = response.info().getheaders("content-type")
		if not ct_headers:
			return self.default_encoding
		# Sometimes servers return multiple HTTP headers: take the first
		http_ct = ct_headers[0]
		for k, v in self.common.split_header_words([http_ct])[0]:
			if k == "charset":
				return v
		# No HTTP-specified encoding, so look in META HTTP-EQUIV headers,
		# which, if present, will be last
		if len(ct_headers) > 1:
			equiv_ct = ct_headers[-1]
			for k, v in self.common.split_header_words([equiv_ct])[0]:
				if k == "charset":
					return v
		return self.default_encoding

	def __find_links(self, single,
					text=None, text_regex=None,
					name=None, name_regex=None,
					url=None, url_regex=None,
					tag=None,
					predicate=None,
					nr=0
					):
		if not self.__is_html():
			raise BrowserStateError(self.NOT_HTML)
		links = []
		orig_nr = nr
		for link in self.__links:
			if url is not None and url != link.url:
				continue
			if url_regex is not None and not url_regex.search(link.url):
				continue
			if (text is not None and
				(link.text is None or text != link.text)):
				continue
			if (text_regex is not None and
				(link.text is None or not text_regex.search(link.text))):
				continue
			if name is not None and name != dict(link.attrs).get("name"):
				continue
			if name_regex is not None:
				link_name = dict(link.attrs).get("name")
				if link_name is None or not name_regex.search(link_name):
					continue
			if tag is not None and tag != link.tag:
				continue
			if predicate is not None and not predicate(link):
				continue
			if nr:
				nr -= 1
				continue
			if single:
				return link
			else:
				links.append(link)
				nr = orig_nr
		if not links:
			raise LinkNotFoundError()
		return links

	def __is_html(self):
		if self.response is None:
			raise BrowserStateError(self.NO_DOC)
		ct = self.response.info().getheaders("content-type")
		return ct and ct[0].startswith("text/html")

	def __open(self, url, data=None, update_history=True):
		"""sets self.request and self.response, returns self.response"""
		# update history
		if (self.request is not None) and (update_history):
				self.__history.append((self.request, self.response))

		# validate incoming url
		scheme = ""
		try:
			url.get_full_url
		except AttributeError:
			# string URL -- convert to absolute URL if required
			scheme, netloc = urlparse.urlparse(url)[:2]
			if (scheme == ""): # relative URL
				if os.path.exists(url):
					scheme = "file"
					netloc = ""
					url = "file://"+url
				elif (self.response is None):
					raise BrowserStateError("Incomplete URL")
				else:
					url = urlparse.urljoin(self.response.geturl(), url)
		else:
			scheme, netloc, action = urlparse.urlparse(url.get_full_url())[:3]
			if (action.find("cgi-bin") != -1):
				self.last_action = "cgi-bin"
			elif (action.find("cgibin") != -1):
				self.last_action = "cgibin"
			else:
				self.lact_action = ""
		if (self.last_scheme == "file"):
			url = self.pwd + urlparse.urlparse(url.get_full_url())[2]
		if (self.debug): print "url "+`url`
		
 
		# self.request assigned even if OpenerDirector.open fails
		self.request = self.get_request(url, data)
		self.request.add_header("accept","*/*")
		self.request.add_header("accept-language","en")
##		self.request.add_header("accept-encoding","gzip")
		self.request.add_header("connections","Keep-Alive")
		host = self.request.get_host()
		self.response = OpenerDirector.open(self, self.request, data)
		if not hasattr(self.response, "seek"):
			self.response = Response_Seek_Wrapper(self.response)
		self.__parse_html(self.response)

		# state preserved for subsequent relative calls
		if (scheme != ""): self.last_scheme = scheme
		if (host != None): self.last_host = host
		if (scheme == "file"):
			self.pwd = self.__pwd(url)
			if (self.debug): print "pwd "+self.pwd
		return self.response

	def __parse_html(self, response):
		self.form = None
		if not self.__is_html():
			return
		# set ._forms
		self.__forms = self.clientform.ParseResponse(response)
		response.seek(0)
		# set  ._links
		base = response.geturl()
		p = PullParser(response, encoding=self.__encoding(response))
		self.__links = []
		for token in p.tags(*(self.URLTAGS.keys()+["base"])):
			if token.data == "base":
				base = dict(token.attrs).get("href")
				continue
			if token.type == "endtag":
				continue
			attrs = dict(token.attrs)
			tag = token.data
			text = None
			url = attrs.get(self.URLTAGS[tag])
			if tag == "a":
				if token.type != "startendtag":
					text = p.get_compressed_text(("endtag", tag))
			if not url:
				continue
			link = Link(base, url, text, tag, token.attrs)
			self.__links.append(link)
		response.seek(0)
		return

	def __pwd(self, url):
		pwd = os.path.dirname(url)
		if (pwd.find("/") != -1): sep = "/"
		else: sep = os.sep
		while (pwd.find("..") != -1):
			tokens = pwd.split(sep)
			i = tokens.index("..")
			newtokens = tokens[:i-1]+tokens[i+1:]
			pwd = sep.join(newtokens)
		return pwd	

	#
	# Public methods
	#

	def back(self, n=1):
		"""
		Go back n steps in history, and return response object.
		n: go back this number of steps (default 1 step)

		"""
		if (self.__history == []):
			raise BrowserStateError("Browser has no history.")
		while n:
			try:
				last_req = self.request
				last_res = self.response
				self.request, self.response = self.__history.pop()
			except IndexError:
				self.request = last_req
				self.response = last_res
			n -= 1
		if self.response is not None:
			self.__parse_html(self.response)
		return self.response

	def click(self, *args, **kwds):
		"""
		Return request that would result from clicking on a control.

		The request object is a urllib2.Request instance, which you can
		pass to urllib2.urlopen or mechanoid.cookiejar.CookieJar.urlopen.

		Only some control types (INPUT/SUBMIT & BUTTON/SUBMIT buttons
		and IMAGEs) can be clicked. And this method will click on the
		first clickable control, subject to the name, type and nr
		arguments (as for find_control).  If no name, type, id or number
		is specified and there are no clickable controls, a request will
		be returned for the form in its current, un-clicked, state.

		IndexError is raised if any of name, type, id or nr is specified
		but no matching control is found. ValueError is raised if the
		HTMLForm has an enctype attribute that is not recognised.

		You can optionally specify a coordinate to click at, which only
		makes a difference if you clicked on an image.

		"""
		if not self.__is_html():
			raise BrowserStateError(self.NOT_HTML)
		request = self.form.click(*args, **kwds)
		request = self.__add_referer_header(request)
		return request

	def click_link(self, link=None, **kwds):
		"""
		Return request that would result from clicking on a hyperlink.

		Find a link and return a Request object for it.  Arguments are
		as for self.find_link(), except that a link may be supplied as
		the first argument.

		"""
		if not self.__is_html():
			raise BrowserStateError(self.NOT_HTML)
		if not link:
			link = self.find_link(**kwds)
		elif kwds:
			raise ValueError("Pass either a link or keyword arguments, not both.")
		# rh::fix failure of urls "some.html" and "/some.html"
		if ((link.absolute_url.find("cgi-bin") == -1) or
			(link.absolute_url.find("cgibin") == -1)):
			last_host = self.last_host+"/"+self.last_action
		else:
			last_host = self.last_host
		if ((link.absolute_url.find("/") == 0) or
			(link.absolute_url.find(":") == -1)):
			link.absolute_url = self.last_scheme+"://"+last_host+"/"+link.absolute_url
		request = Request(link.absolute_url)
		self.last_host = request.get_host() # rh::update last_host
		request = self.__add_referer_header(request)
		return request

	def close(self):
		"""
		Neutralize browser's state

		"""
		UserAgent.close(self)
		self.__history = self.__forms = self.__links = None
		self.request = self.response = None
		return

	def debug_forms(self):
		print "Mechanoid - forms"
		for form in self.forms():
			print form
		return	

	def debug_links(self):
		print "Mechanoid - links"
		for link in self.links():
			print link
		return	

	def debug_response(self, response, fname=None):
		"""
		Prints a response object's read().
		Writes to fname or stdout.
		
		"""
		response.seek(0)
		content = response.read()
		if (fname == None):
			print "Mechanoid - response"
			print content
		else:
			f = open(fname, 'w')
			f.write(content)
			f.close()
		response.seek(0)
		return	

	def find_link(self, *args, **kwds):
		"""
		Find a link in current page.  Links are returned as
		mechanoid.misc.Link objects.

		Return third link that .search()-matches the regexp "python" (by
		".search()-matches", I mean that the regular expression method
		.search() is used, rather than .match()).

		    find_link(text_regex=re.compile("python"), nr=2)

		Return first http link in the current page that points to
		somewhere on python.org whose link text (after tags have been
		removed) is exactly "monty python" have been removed).

		    find_link(text="monty python", url_regex=re.compile("http.*python.org"))

		Return first link with exactly three HTML attributes.

		    find_link(predicate=lambda link: len(link.attrs) == 3)

		Links include anchors (<a>), image maps (<area>), and frames
		(<frame>, <iframe>).

		All arguments must be passed by keyword, not position. Zero or
		more arguments may be supplied. In order to find a link, all
		arguments supplied must match.

		If a matching link is not found, mechanize.LinkNotFoundError is
		raised.

		text: link text between link tags: eg. <a href="blah">this
		bit</a> (as returned by PullParser.get_compressed_text(),
		ie. without tags but with opening tags "textified" as per the
		PullParser docs) must compare equal to this argument, if
		supplied

		text_regex: link text between tag (as defined above) must match
		the regular expression object passed as this argument, if
		supplied

		name, name_regex: as for text and text_regex, but matched
		against the name HTML attribute of the link tag

		url, url_regex: as for text and text_regex, but matched against
		the URL of the link tag (note this matches against Link.url,
		which is a relative or absolute URL according to how it was
		written in the HTML)

		tag: element name of opening tag, eg. "a" predicate: a function
		taking a Link object as its single argument, returning a boolean
		result, indicating whether the links

		nr: matches the nth link that matches all other criteria (default 0)

		"""
		if args:
			raise ValueError(self.KEYWDS)
		return self.__find_links(True, **kwds)

	def follow_link(self, link=None, **kwds):
		"""
		Find a link and .open() it. Arguments are as for
		self.click_link().

		"""
		return self.__open(self.click_link(link, **kwds)) # self.response

	def forms(self):
		"""
		Return list of current page's forms.  The returned form objects
		implement the mechanoid.clientform.HTMLForm interface.

		"""
		if not self.__is_html():
			raise BrowserStateError(self.NOT_HTML)
		return self.__forms

	def geturl(self):
		"""
		Get URL of current document.

		"""
		if self.response is None:
			raise BrowserStateError(self.NO_DOC)
		return self.response.geturl()

	def links(self, *args, **kwds):
		"""
		Return list of current page's links. The returned link objects
		implement the mechanoid.misc.Link interface.

		"""
		if not self.__is_html():
			raise BrowserStateError(self.NOT_HTML)
		if args:
			raise ValueError(self.KEYWDS)
		if kwds:
			return self.__find_links(False, **kwds)
		return self.__links

	def open(self, url, data=None):
		"""
		Open a remote document.

		"""
		return self.__open(url, data)

	def reload(self):
		"""
		Reload current document, and return response object.

		"""
		if self.request is None:
			raise BrowserStateError(self.NO_DOC)
		return self.__open(self.request, update_history=False) # self.response

	def select_form(self, name=None, predicate=None, nr=None):
		"""
		Select an HTML form for input.

		This is like giving a form the "input focus" in a browser.
		If a form is selected, the object supports the HTMLForm
		interface, so you can call methods like .set_value(), .set(),
		and .click().

		At least one of the name, predicate and nr arguments must be
		supplied.  If no matching form is found,
		mechanoid.misc.Errors.FormNotFoundError is raised.

		name: form must have the indicated name.

		predicate: form must match that function. The predicate function
		is passed the HTMLForm as its single argument, and should return
		a boolean value indicating whether the form matched.

		nr: sequence number of the form (where 0 is the first).  Note
		that control 0 is the first form matching all the other
		arguments (if supplied); it is not necessarily the first control
		in the form.

		"""
		if not self.__is_html():
			raise BrowserStateError(self.NOT_HTML)
		if (name is None) and (predicate is None) and (nr is None):
			raise ValueError(
				"You must specify form by name, predicate, and/or number.")

		orig_nr = nr
		for form in self.__forms:
			if name is not None and name != form.name:
				continue
			if predicate is not None and not predicate(form):
				continue
			if nr:
				nr -= 1
				continue
			self.form = form  # success
			break
		else: # failure (reached if break not executed)
			description = []
			if name is not None:
				description.append("name '%s'" % name)
			if predicate is not None:
				description.append("predicate %s" % predicate)
			if orig_nr is not None:
				description.append("nr %d" % orig_nr)
			description = ", ".join(description)
			raise FormNotFoundError("No form matching "+description)

	def submit(self, *args, **kwds):
		"""
		Submit current form.  Arguments are as for self.click()

		"""
		return self.__open(self.click(*args, **kwds)) # self.response

	def title(self):
		"""
		Return title, or None if there is no title element in the
		document.  Tags are stripped or textified as described in docs
		for PullParser.get_text() method.

		"""
		if not self.__is_html():
			raise BrowserStateError(self.NOT_HTML)
		p = PullParser(self.response,
					   encoding=self.__encoding(self.response))
		try:
			p.get_tag("title")
		except NoMoreTokensError:
			title = None
		else:
			title = p.get_text()
		return title
