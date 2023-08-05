
# CookieJar.py::refactored from JJLee's ClientCookie
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
# Copyright 2002-2003 John J Lee <jjl@pobox.com>
# Copyright 1997-1999 Gisle Aas (original libwww-perl code)
# Copyright 2002-2003 Johnny Lee (original MSIE Perl code)
#

import re, time, copy, string, sys, threading
from mechanoid.misc.Consts import IPV4_RE
from mechanoid.misc.Common import Common
from Absent import Absent
from Cookie import Cookie
from DefaultCookiePolicy import DefaultCookiePolicy
from Header_Utils import Header_Utils
from MappingIterator import MappingIterator

class CookieJar:
	"""Collection of HTTP cookies.

	The major methods are extract_cookies and add_cookie_header; these are all
	you are likely to need.	 In fact, you probably don't even need to know
	about this class: use the cookie-aware extensions to the urllib2 callables
	provided by this module: urlopen in particular (and perhaps also
	build_opener, install_opener, HTTPCookieProcessor, HTTPRefererProcessor,
	HTTPRefreshHandler, HTTPEquivProcessor, SeekableProcessor, etc.).

	CookieJar supports the iterator protocol.  Iteration also works in 1.5.2:

	for cookie in cookiejar:
		# do something with cookie

	Methods:

	CookieJar(filename=None, delayload=False, policy=None)
	add_cookie_header(request, unverifiable=False)
	extract_cookies(response, request, unverifiable=False)
	make_cookies(response, request)
	set_cookie_if_ok(cookie, request, unverifiable=False)
	set_cookie(cookie)
	save(filename=None, ignore_discard=False, ignore_expires=False)
	load(filename=None, ignore_discard=False, ignore_expires=False)
	revert(filename=None, ignore_discard=False, ignore_expires=False)
	clear(domain=None, path=None, name=None)
	clear_session_cookies()
	clear_expired_cookies()
	as_lwp_str(skip_discard=False, skip_expires=False)


	Public attributes

	filename: filename for loading and saving cookies
	policy: CookiePolicy object

	Public readable attributes

	delayload: request that cookies are lazily loaded from disk; this is only
	 a hint since this only affects performance, not behaviour (unless the
	 cookies on disk are changing); a CookieJar object may ignore it (in fact,
	 only MSIECookieJar lazily loads cookies at the moment)
	cookies: a three-level dictionary [domain][path][key] containing Cookie
	 instances; you almost certainly don't need to use this

	"""
	DEBUG = 0
	non_word_re = re.compile(r"\W")
	quote_re = re.compile(r"([\"\\])")
	strict_domain_re = re.compile(r"\.?[^.]*")
	domain_re = re.compile(r"[^.]*")
	dots_re = re.compile(r"^\.+")
	magic_re = r"^\#LWP-Cookies-(\d+\.\d+)"
	iso_re = re.compile(
		"""^
		(\d{4})              # year
		[-\/]?
		(\d\d?)              # numerical month
		[-\/]?
		(\d\d?)              # day
		(?:
		(?:\s+|[-:Tt])  # separator before clock
		(\d\d?):?(\d\d)    # hour:min
		(?::?(\d\d(?:\.\d*)?))?  # optional seconds (and fractional)
		)?                    # optional clock
		\s*
		([-+]?\d\d?:?(:?\d\d)?
		|Z|z)?               # timezone  (Z is "zero meridian", i.e. GMT)
		\s*$""", re.X)

	MISSING_FILENAME_TEXT = ("a filename was not supplied (nor was the CookieJar "
							 "instance initialized with one)")

	def __init__(self, filename=None, delayload=False, policy=None):
		"""
		See CookieJar.__doc__ for argument documentation.

		Cookies are NOT loaded from the named file until either the load or
		revert method is called.

		"""
		self.filename = filename
		self.delayload = delayload
		self.hdr_util = Header_Utils()

		if policy is None:
			policy = DefaultCookiePolicy()
		self.policy = policy

		self._cookies_lock = threading.RLock()
		self.cookies = {}

		# for __getitem__ iteration in pre-2.2 Pythons
		self._prev_getitem_index = 0
		self.common = Common()

	def iso2time(self, text):
		"""
		As for http2time, but parses the ISO 8601 formats:

		1994-02-03 14:15:29 -0100    -- ISO 8601 format
		1994-02-03 14:15:29          -- zone is optional
		1994-02-03                   -- only date
		1994-02-03T14:15:29          -- Use T as separator
		19940203T141529Z             -- ISO 8601 compact format
		19940203                     -- only date

		"""
		# clean up
		text = string.lstrip(text)
		# tz is time zone specifier string
		day, mon, yr, hr, min, sec, tz = [None]*7
		# loose regexp parse
		m = self.iso_re.search(text)
		if m is not None:
			# XXX there's an extra bit of the timezone I'm ignoring here: is
			#   this the right thing to do?
			yr, mon, day, hr, min, sec, tz, _ = m.groups()
		else:
			return None  # bad format
		return self.common.str2time(day, mon, yr, hr, min, sec, tz)

	def time2isoz(self, t=None):
		"""Return a string representing time in seconds since epoch, t.

		If the function is called without an argument, it will use the current
		time.

		The format of the returned string is like "YYYY-MM-DD hh:mm:ssZ",
		representing Universal Time (UTC, aka GMT).  An example of this format is:

		1994-11-24 08:49:37Z

		"""
		if t is None: t = time.time()
		year, mon, mday, hour, min, sec = time.gmtime(t)[:6]
		return "%04d-%02d-%02d %02d:%02d:%02dZ" % (
			year, mon, mday, hour, min, sec)

	def _cookies_for_domain(self, domain, request, unverifiable):
		"""Return a list of cookies to be returned to server."""
		if (self.DEBUG):
			print("Checking %s for cookies to return", domain)
		if not self.policy.domain_return_ok(domain, request, unverifiable):
			return []

		cookies_by_path = self.cookies.get(domain)
		if cookies_by_path is None:
			return []

		cookies = []
		for path in cookies_by_path.keys():
			if not self.policy.path_return_ok(path, request, unverifiable):
				continue
			for name, cookie in cookies_by_path[path].items():
				if not self.policy.return_ok(cookie, request, unverifiable):
					if (self.DEBUG):
						print("	  not returning cookie")
					continue
				if (self.DEBUG):
					print("	  it's a match")
				cookies.append(cookie)

		return cookies

	def _cookie_attrs(self, cookies):
		"""Return a list of cookie-attributes to be returned to server.

		like ['foo="bar"; $Path="/"', ...]

		The $Version attribute is also added when appropriate (currently only
		once per request).

		"""
		# add cookies in order of most specific (ie. longest) path first
		def decreasing_size(a, b): return cmp(len(b.path), len(a.path))
		cookies.sort(decreasing_size)

		version_set = False

		attrs = []
		for cookie in cookies:
			# set version of Cookie header
			# XXX
			# What should it be if multiple matching Set-Cookie headers have
			#  different versions themselves?
			# Answer: there is no answer; was supposed to be settled by
			#  RFC 2965 errata, but that may never appear...
			version = cookie.version
			if not version_set:
				version_set = True
				if version > 0:
					attrs.append("$Version=%s" % version)

			# quote cookie value if necessary
			# (not for Netscape protocol, which already has any quotes
			#  intact, due to the poorly-specified Netscape Cookie: syntax)
			if self.non_word_re.search(cookie.value) and version > 0:
				value = self.quote_re.sub(r"\\\1", cookie.value)
			else:
				value = cookie.value

			# add cookie-attributes to be returned in Cookie header
			if cookie.name is None:
				attrs.append(value)
			else:
				attrs.append("%s=%s" % (cookie.name, value))
			if version > 0:
				if cookie.path_specified:
					attrs.append('$Path="%s"' % cookie.path)
				if self.common.startswith(cookie.domain, "."):
					domain = cookie.domain
					if (not cookie.domain_initial_dot and
						self.common.startswith(domain, ".")):
						domain = domain[1:]
					attrs.append('$Domain="%s"' % domain)
				if cookie.port is not None:
					p = "$Port"
					if cookie.port_specified:
						p = p + ('="%s"' % cookie.port)
					attrs.append(p)

		return attrs

	def add_cookie_header(self, request, unverifiable=False):
		"""Add correct Cookie: header to request (urllib2.Request object).

		The Cookie2 header is also added unless policy.hide_cookie2 is true.

		The request object (usually a urllib2.Request instance) must support
		the methods get_full_url, get_host, get_type, has_header, get_header,
		iter_headers and add_unredirected_header, as documented by urllib2, and
		the attributes headers (a mapping containing the request's HTTP
		headers) and port (the port number).  Actually, RequestUpgradeProcessor
		will automatically upgrade your Request object to one with has_header,
		get_header, iter_headers and add_unredirected_header, if it lacks those
		methods, for compatibility with pre-2.4 versions of urllib2.

		If unverifiable is true, it will be assumed that the transaction is
		unverifiable as defined by RFC 2965, and appropriate action will be
		taken.

		"""
		if (self.DEBUG):
			print("add_cookie_header")
		self._cookies_lock.acquire()

		self.policy._now = self._now = int(time.time())

		req_host, erhn = self.common.eff_request_host(request)
		strict_non_domain = \
			   self.policy.strict_ns_domain & self.policy.DomainStrictNonDomain

		cookies = []

		domain = erhn
		# First check origin server effective host name for an exact match.
		cookies.extend(self._cookies_for_domain(domain, request, unverifiable))
		# Then, start with effective request-host with initial dot prepended
		# (for Netscape cookies with explicitly-set Domain cookie-attributes)
		# -- eg. .foo.bar.baz.com and check all possible derived domain strings
		# (.bar.baz.com, bar.baz.com, .baz.com) for cookies.
		# This isn't too finicky about which domains to check, because we have
		# to cover both V0 and V1 cookies, and policy.return_ok will check the
		# domain in any case.
		if not IPV4_RE.search(req_host):
			# IP addresses must string-compare equal in order to domain-match
			# (IP address case will have been checked above as erhn == req_host
			# in that case).
			if domain != ".local":
				domain = "."+domain
			while string.find(domain, ".") >= 0:
				cookies.extend(self._cookies_for_domain(
					domain, request, unverifiable))
				if strict_non_domain:
					domain = self.strict_domain_re.sub("", domain, 1)
				else:
					# strip either initial dot only, or initial component only
					# .www.foo.com --> www.foo.com
					# www.foo.com --> .foo.com
					if self.common.startswith(domain, "."):
						domain = domain[1:]
						# we've already done the erhn
						if domain == erhn:
							domain = self.domain_re.sub("", domain, 1)
					else:
						domain = self.domain_re.sub("", domain, 1)

		attrs = self._cookie_attrs(cookies)
		if attrs:
			if not request.has_header("Cookie"):
				request.add_unredirected_header(
					"Cookie", string.join(attrs, "; "))

		# if necessary, advertise that we know RFC 2965
		if self.policy.rfc2965 and not self.policy.hide_cookie2:
			for cookie in cookies:
				if cookie.version != 1 and not request.has_header("Cookie2"):
					request.add_unredirected_header("Cookie2", '$Version="1"')
					break

		self._cookies_lock.release()

		self.clear_expired_cookies()

	def _normalized_cookie_tuples(self, attrs_set):
		"""Return list of tuples containing normalised cookie information.

		attrs_set is the list of lists of key,value pairs extracted from
		the Set-Cookie or Set-Cookie2 headers.

		Tuples are name, value, standard, rest, where name and value are the
		cookie name and value, standard is a dictionary containing the standard
		cookie-attributes (discard, secure, version, expires or max-age,
		domain, path and port) and rest is a dictionary containing the rest of
		the cookie-attributes.

		"""
		cookie_tuples = []

		boolean_attrs = "discard", "secure"
		value_attrs = ("version",
					   "expires", "max-age",
					   "domain", "path", "port",
					   "comment", "commenturl")

		for cookie_attrs in attrs_set:
			name, value = cookie_attrs[0]

			# Build dictionary of standard cookie-attributes (standard) and
			# dictionary of other cookie-attributes (rest).

			# Note: expiry time is normalised to seconds since epoch.  V0
			# cookies should have the Expires cookie-attribute, and V1 cookies
			# should have Max-Age, but since V1 includes RFC 2109 cookies (and
			# since V0 cookies may be a mish-mash of Netscape and RFC 2109), we
			# accept either (but prefer Max-Age).
			max_age_set = False

			bad_cookie = False

			standard = {}
			rest = {}
			for k, v in cookie_attrs[1:]:
				lc = string.lower(k)
				# don't lose case distinction for unknown fields
				if lc in value_attrs or lc in boolean_attrs:
					k = lc
				if k in boolean_attrs and v is None:
					# boolean cookie-attribute is present, but has no value
					# (like "discard", rather than "port=80")
					v = True
				if standard.has_key(k):
					# only first value is significant
					continue
				if k == "domain":
					if v is None:
						if (self.DEBUG):
							print("	  missing value for domain attribute")
						bad_cookie = True
						break
					# RFC 2965 section 3.3.3
					v = string.lower(v)
				if k == "expires":
					if max_age_set:
						# Prefer max-age to expires (like Mozilla)
						continue
					if v is None:
						if (self.DEBUG):
							print("	  missing or invalid value for expires "
								  "attribute: treating as session cookie")
						continue
				if k == "max-age":
					max_age_set = True
					try:
						v = int(v)
					except ValueError:
						if (self.DEBUG):
							print("	  missing or invalid (non-numeric) value for "
								  "max-age attribute")
						bad_cookie = True
						break
					# convert RFC 2965 Max-Age to seconds since epoch
					# XXX Strictly you're supposed to follow RFC 2616
					#	age-calculation rules.	Remember that zero Max-Age is a
					#	is a request to discard (old and new) cookie, though.
					k = "expires"
					v = self._now + v
				if (k in value_attrs) or (k in boolean_attrs):
					if (v is None and
						k not in ["port", "comment", "commenturl"]):
						if (self.DEBUG):
							print("	  missing value for %s attribute" % k)
						bad_cookie = True
						break
					standard[k] = v
				else:
					rest[k] = v

			if bad_cookie:
				continue

			cookie_tuples.append((name, value, standard, rest))

		return cookie_tuples

	def _cookie_from_cookie_tuple(self, tup, request):
		# standard is dict of standard cookie-attributes, rest is dict of the
		# rest of them
		name, value, standard, rest = tup

		domain = standard.get("domain", Absent)
		path = standard.get("path", Absent)
		port = standard.get("port", Absent)
		expires = standard.get("expires", Absent)

		# set the easy defaults
		version = standard.get("version", None)
		if version is not None: version = int(version)
		secure = standard.get("secure", False)
		# (discard is also set if expires is Absent)
		discard = standard.get("discard", False)
		comment = standard.get("comment", None)
		comment_url = standard.get("commenturl", None)

		# set default path
		if path is not Absent and path != "":
			path_specified = True
			path = self.common.escape_path(path)
		else:
			path_specified = False
			path = self.common.request_path(request)
			i = string.rfind(path, "/")
			if i != -1:
				if version == 0:
					# Netscape spec parts company from reality here
					path = path[:i]
				else:
					path = path[:i+1]
			if len(path) == 0: path = "/"

		# set default domain
		domain_specified = domain is not Absent
		# but first we have to remember whether it starts with a dot
		domain_initial_dot = False
		if domain_specified:
			domain_initial_dot = bool(self.common.startswith(domain, "."))
		if domain is Absent:
			req_host, erhn = self.common.eff_request_host(request)
			domain = erhn
		elif not self.common.startswith(domain, "."):
			domain = "."+domain

		# set default port
		port_specified = False
		if port is not Absent:
			if port is None:
				# Port attr present, but has no value: default to request port.
				# Cookie should then only be sent back on that port.
				port = self.common.request_port(request)
			else:
				port_specified = True
				port = re.sub(r"\s+", "", port)
		else:
			# No port attr present.	 Cookie can be sent back on any port.
			port = None

		# set default expires and discard
		if expires is Absent:
			expires = None
			discard = True
		elif expires <= self._now:
			# Expiry date in past is request to delete cookie.	This can't be
			# in DefaultCookiePolicy, because can't delete cookies there.
			try:
				del self.cookies[domain][path][name]
			except KeyError:
				pass
			if (self.DEBUG):
				print("Expiring cookie, domain='%s', path='%s', name='%s'",
					  domain, path, name)
			return None

		return Cookie(version,
					  name, value,
					  port, port_specified,
					  domain, domain_specified, domain_initial_dot,
					  path, path_specified,
					  secure,
					  expires,
					  discard,
					  comment,
					  comment_url,
					  rest)

	def _cookies_from_attrs_set(self, attrs_set, request):
		cookie_tuples = self._normalized_cookie_tuples(attrs_set)

		cookies = []
		for tup in cookie_tuples:
			cookie = self._cookie_from_cookie_tuple(tup, request)
			if cookie: cookies.append(cookie)
		return cookies

	def make_cookies(self, response, request):
		"""Return sequence of Cookie objects extracted from response object.

		See extract_cookies.__doc__ for the interfaces required of the
		response and request arguments.

		"""
		# get cookie-attributes for RFC 2965 and Netscape protocols
		headers = response.info()
		rfc2965_hdrs = self.common.getheaders(headers, "Set-Cookie2")
		ns_hdrs = self.common.getheaders(headers, "Set-Cookie")

		rfc2965 = self.policy.rfc2965
		netscape = self.policy.netscape

		if ((not rfc2965_hdrs and not ns_hdrs) or
			(not ns_hdrs and not rfc2965) or
			(not rfc2965_hdrs and not netscape) or
			(not netscape and not rfc2965)):
			return []  # no relevant cookie headers: quick exit

		try:
			cookies = self._cookies_from_attrs_set(
				self.hdr_util.split_header_words(rfc2965_hdrs), request)
		except:
			self.reraise_unmasked_exceptions()
			cookies = []

		if ns_hdrs and netscape:
			try:
				ns_cookies = self._cookies_from_attrs_set(
					self.hdr_util.parse_ns_headers(ns_hdrs), request)
			except:
				self.reraise_unmasked_exceptions()
				ns_cookies = []

			# Look for Netscape cookies (from Set-Cookie headers) that match
			# corresponding RFC 2965 cookies (from Set-Cookie2 headers).
			# For each match, keep the RFC 2965 cookie and ignore the Netscape
			# cookie (RFC 2965 section 9.1).  Actually, RFC 2109 cookies are
			# bundled in with the Netscape cookies for this purpose, which is
			# reasonable behaviour.
			if rfc2965:
				lookup = {}
				for cookie in cookies:
					lookup[(cookie.domain, cookie.path, cookie.name)] = None

				def no_matching_rfc2965(ns_cookie, lookup=lookup):
					key = ns_cookie.domain, ns_cookie.path, ns_cookie.name
					return not lookup.has_key(key)
				ns_cookies = filter(no_matching_rfc2965, ns_cookies)

			if ns_cookies:
				cookies.extend(ns_cookies)

		return cookies

	def set_cookie_if_ok(self, cookie, request, unverifiable=False):
		"""Set a cookie if policy says it's OK to do so.

		cookie: ClientCookie.Cookie instance
		request: see extract_cookies.__doc__ for the required interface
		unverifiable: see extract_cookies.__doc__

		"""
		self._cookies_lock.acquire()
		self.policy._now = self._now = int(time.time())

		if self.policy.set_ok(cookie, request, unverifiable):
			self.set_cookie(cookie)

		self._cookies_lock.release()

	def set_cookie(self, cookie):
		"""Set a cookie, without checking whether or not it should be set.

		cookie: ClientCookie.Cookie instance
		"""
		c = self.cookies
		self._cookies_lock.acquire()
		try:
			if not c.has_key(cookie.domain): c[cookie.domain] = {}
			c2 = c[cookie.domain]
			if not c2.has_key(cookie.path): c2[cookie.path] = {}
			c3 = c2[cookie.path]
			c3[cookie.name] = cookie
		finally:
			self._cookies_lock.release()

	def extract_cookies(self, response, request, unverifiable=False):
		"""Extract cookies from response, where allowable given the request.

		Look for allowable Set-Cookie: and Set-Cookie2: headers in the response
		object passed as argument.	Any of these headers that are found are
		used to update the state of the object (subject to the policy.set_ok
		method's approval).

		The response object (usually be the result of a call to
		ClientCookie.urlopen, or similar) should support an info method, which
		returns a mimetools.Message object (in fact, the 'mimetools.Message
		object' may be any object that provides a getallmatchingheaders
		method).

		The request object (usually a urllib2.Request instance) must support
		the methods get_full_url and get_host, as documented by urllib2, and
		the attributes headers (a mapping containing the request's HTTP
		headers) and port (the port number).  The request is used to set
		default values for cookie-attributes as well as for checking that the
		cookie is OK to be set.

		If unverifiable is true, it will be assumed that the transaction is
		unverifiable as defined by RFC 2965, and appropriate action will be
		taken.

		"""
		if (self.DEBUG):
			print("extract_cookies: %s", response.info())
		self._cookies_lock.acquire()
		self.policy._now = self._now = int(time.time())

		for cookie in self.make_cookies(response, request):
			if self.policy.set_ok(cookie, request, unverifiable):
				if (self.DEBUG):
					print(" setting cookie: %s", cookie)
				self.set_cookie(cookie)
		self._cookies_lock.release()

	def save(self, filename=None, ignore_discard=False, ignore_expires=False):
		"""Save cookies to a file.

		filename: name of file in which to save cookies
		ignore_discard: save even cookies set to be discarded
		ignore_expires: save even cookies that have expired

		The file is overwritten if it already exists, thus wiping all its
		cookies.  Saved cookies can be restored later using the load or revert
		methods.  If filename is not specified, self.filename is used; if
		self.filename is None, ValueError is raised.

		The CookieJar base class saves a sequence of "Set-Cookie3" lines.
		"Set-Cookie3" is the format used by the libwww-perl libary, not known
		to be compatible with any browser.	The MozillaCookieJar subclass can
		be used to save in a format compatible with the Mozilla/Netscape/lynx
		browsers.

		"""
		if filename is None:
			if self.filename is not None: filename = self.filename
			else: raise ValueError(self.MISSING_FILENAME_TEXT)

		f = open(filename, "w")
		try:
			# There really isn't an LWP Cookies 2.0 format, but this indicates
			# that there is extra information in here (domain_dot and
			# port_spec) while still being compatible with libwww-perl, I hope.
			f.write("#LWP-Cookies-2.0\n")
			f.write(self.as_lwp_str(not ignore_discard, not ignore_expires))
		finally:
			f.close()

	def load(self, filename=None, ignore_discard=False, ignore_expires=False):
		"""Load cookies from a file.

		Old cookies are kept unless overwritten by newly loaded ones.

		Arguments are as for .save().

		If filename is not specified, self.filename is used; if self.filename
		is None, ValueError is raised.	The named file must be in the format
		understood by the class, or IOError will be raised.	 This format will
		be identical to that written by the save method, unless the load format
		is not sufficiently well understood (as is the case for MSIECookieJar).

		Note for subclassers: if overridden versions of this method alter the
		object's state other than by calling self.set_cookie, you also need to
		override .revert().

		"""
		if filename is None:
			if self.filename is not None: filename = self.filename
			else: raise ValueError(self.MISSING_FILENAME_TEXT)

		f = open(filename)
		try:
			self._really_load(f, filename, ignore_discard, ignore_expires)
		finally:
			f.close()

	def _really_load(self, f, filename, ignore_discard, ignore_expires):
		magic = f.readline()
		if not re.search(self.magic_re, magic):
			msg = "%s does not seem to contain cookies" % filename
			raise IOError(msg)

		now = time.time()

		header = "Set-Cookie3:"
		boolean_attrs = ("port_spec", "path_spec", "domain_dot",
						 "secure", "discard")
		value_attrs = ("version",
					   "port", "path", "domain",
					   "expires",
					   "comment", "commenturl")

		try:
			while 1:
				line = f.readline()
				if line == "": break
				if not self.common.startswith(line, header):
					continue
				line = string.strip(line[len(header):])

				for data in self.hdr_util.split_header_words([line]):
					name, value = data[0]
					# name and value are an exception here, since a plain "foo"
					# (with no "=", unlike "bar=foo") means a cookie with no
					# name and value "foo".	 With all other cookie-attributes,
					# the situation is reversed: "foo" means an attribute named
					# "foo" with no value!
					if value is None:
						name, value = value, name
					standard = {}
					rest = {}
					for k in boolean_attrs:
						standard[k] = False
					for k, v in data[1:]:
						if k is not None:
							lc = string.lower(k)
						else:
							lc = None
						# don't lose case distinction for unknown fields
						if (lc in value_attrs) or (lc in boolean_attrs):
							k = lc
						if k in boolean_attrs:
							if v is None: v = True
							standard[k] = v
						elif k in value_attrs:
							standard[k] = v
						else:
							rest[k] = v

					h = standard.get
					expires = h("expires")
					discard = h("discard")
					if expires is not None:
						expires = self.iso2time(expires)
					if expires is None:
						discard = True
					domain = h("domain")
					domain_specified = self.common.startswith(domain, ".")
					c = Cookie(h("version"), name, value,
							   h("port"), h("port_spec"),
							   domain, domain_specified, h("domain_dot"),
							   h("path"), h("path_spec"),
							   h("secure"),
							   expires,
							   discard,
							   h("comment"),
							   h("commenturl"),
							   rest)
					if not ignore_discard and c.discard:
						continue
					if not ignore_expires and c.is_expired(now):
						continue
					self.set_cookie(c)
		except:
			self.reraise_unmasked_exceptions((IOError,))
			raise IOError("invalid Set-Cookie3 format file %s" % filename)

	def revert(self, filename=None,
			   ignore_discard=False, ignore_expires=False):
		"""Clear all cookies and reload cookies from a saved file.

		Raises IOError if reversion is not successful; the object's state will
		not be altered if this happens.

		"""
		if filename is None:
			if self.filename is not None: filename = self.filename
			else: raise ValueError(self.MISSING_FILENAME_TEXT)

		self._cookies_lock.acquire()

		old_state = copy.deepcopy(self.cookies)
		self.cookies = {}
		try:
			self.load(filename, ignore_discard, ignore_expires)
		except IOError:
			self.cookies = old_state
			raise

		self._cookies_lock.release()

	def clear(self, domain=None, path=None, name=None):
		"""Clear some cookies.

		Invoking this method without arguments will clear all cookies.	If
		given a single argument, only cookies belonging to that domain will be
		removed.  If given two arguments, cookies belonging to the specified
		path within that domain are removed.  If given three arguments, then
		the cookie with the specified name, path and domain is removed.

		Raises KeyError if no matching cookie exists.

		"""
		if name is not None:
			if (domain is None) or (path is None):
				raise ValueError(
					"domain and path must be given to remove a cookie by name")
			del self.cookies[domain][path][name]
		elif path is not None:
			if domain is None:
				raise ValueError(
					"domain must be given to remove cookies by path")
			del self.cookies[domain][path]
		elif domain is not None:
			del self.cookies[domain]
		else:
			self.cookies = {}

	def clear_session_cookies(self):
		"""Discard all session cookies.

		Discards all cookies held by object which had either no Max-Age or
		Expires cookie-attribute or an explicit Discard cookie-attribute, or
		which otherwise have ended up with a true discard attribute.  For
		interactive browsers, the end of a session usually corresponds to
		closing the browser window.

		Note that the save method won't save session cookies anyway, unless you
		ask otherwise by passing a true ignore_discard argument.

		"""
		self._cookies_lock.acquire()
		for cookie in self:
			if cookie.discard:
				del self.cookies[cookie.domain][cookie.path][cookie.name]
		self._cookies_lock.release()

	def clear_expired_cookies(self):
		"""Discard all expired cookies.

		You probably don't need to call this method: expired cookies are never
		sent back to the server (provided you're using DefaultCookiePolicy),
		this method is called by CookieJar itself every so often, and the save
		method won't save expired cookies anyway (unless you ask otherwise by
		passing a true ignore_expires argument).

		"""
		self._cookies_lock.acquire()
		now = time.time()
		for cookie in self:
			if cookie.is_expired(now):
				del self.cookies[cookie.domain][cookie.path][cookie.name]
		self._cookies_lock.release()

	def __getitem__(self, i):
		if i == 0:
			self._getitem_iterator = self.__iter__()
		elif self._prev_getitem_index != i-1: raise IndexError(
			"CookieJar.__getitem__ only supports sequential iteration")
		self._prev_getitem_index = i
		try:
			return self._getitem_iterator.next()
		except StopIteration:
			raise IndexError()

	def __iter__(self):
		return MappingIterator(self.cookies)

	def __len__(self):
		"""Return number of contained cookies."""
		i = 0
		for cookie in self: i = i + 1
		return i

	def __repr__(self):
		r = []
		for cookie in self: r.append(repr(cookie))
		return "<%s[%s]>" % (self.__class__, string.join(r, ", "))

	def __str__(self):
		r = []
		for cookie in self: r.append(str(cookie))
		return "<%s[%s]>" % (self.__class__, string.join(r, ", "))

	def as_lwp_str(self, skip_discard=False, skip_expired=False):
		"""Return cookies as a string of "\n"-separated "Set-Cookie3" headers.

		If skip_discard is true, it will not return lines for cookies with the
		Discard cookie-attribute.

		"""
		now = time.time()
		r = []
		for cookie in self:
			if skip_discard and cookie.discard:
				continue
			if skip_expired and cookie.is_expired(now):
				continue
			r.append("Set-Cookie3: %s" % self.lwp_cookie_str(cookie))
		return string.join(r+[""], "\n")

	def reraise_unmasked_exceptions(self, unmasked=()):
		# There are a few catch-all except: statements in this module, for
		# catching input that's bad in unexpected ways.
		# This function re-raises some exceptions we don't want to trap.
		unmasked = unmasked + (KeyboardInterrupt, SystemExit, MemoryError)
		etype = sys.exc_info()[0]
		if issubclass(etype, unmasked):
			raise
		# swallowed an exception
		import traceback
		traceback.print_exc()
		return

	def lwp_cookie_str(self, cookie):
		"""Return string representation of Cookie in an the LWP cookie file format.

		Actually, the format is slightly extended from that used by LWP's
		(libwww-perl's) HTTP::Cookies, to avoid losing some RFC 2965
		information not recorded by LWP.

		Used by the CookieJar base class for saving cookies to a file.

		"""
		tmp = [(cookie.name, cookie.value), ("path", cookie.path), ("domain", cookie.domain)]

		if cookie.port is not None: tmp.append(("port", cookie.port))
		if cookie.path_specified: tmp.append(("path_spec", None))
		if cookie.port_specified: tmp.append(("port_spec", None))
		if cookie.domain_initial_dot: tmp.append(("domain_dot", None))
		if cookie.secure: tmp.append(("secure", None))
		if cookie.expires: tmp.append(("expires", self.time2isoz(float(cookie.expires))))
		if cookie.discard: tmp.append(("discard", None))
		if cookie.comment: tmp.append(("comment", cookie.comment))
		if cookie.comment_url: tmp.append(("commenturl", cookie.comment_url))

		keys = cookie.rest.keys()
		keys.sort()
		for k in keys:
			tmp.append((k, str(cookie.rest[k])))

		tmp.append(("version", str(cookie.version)))

		return self.hdr_util.join_header_words([tmp])

