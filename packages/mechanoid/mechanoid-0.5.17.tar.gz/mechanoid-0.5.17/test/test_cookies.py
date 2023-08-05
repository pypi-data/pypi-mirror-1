# -*- coding: utf-8 -*-
"""Tests for ClientCookie._ClientCookie."""

import urllib2, re, os, string, StringIO, mimetools, time
from time import localtime
from unittest import TestCase
from mechanoid.misc.Common import Common
common = Common()

class FakeResponse:
	def __init__(self, headers=[], url=None):
		"""
		headers: list of RFC822-style 'Key: value' strings
		"""
		f = StringIO.StringIO(string.join(headers, "\n"))
		self._headers = mimetools.Message(f)
		self._url = url
	def info(self): return self._headers
	def url(): return self._url

def interact_2965(cookiejar, url, *set_cookie_hdrs):
	return _interact(cookiejar, url, set_cookie_hdrs, "Set-Cookie2")

def interact_netscape(cookiejar, url, *set_cookie_hdrs):
	return _interact(cookiejar, url, set_cookie_hdrs, "Set-Cookie")

def _interact(cookiejar, url, set_cookie_hdrs, hdr_name):
	"""Perform a single request / response cycle, returning Cookie: header."""
	from mechanoid.misc.Request import Request
	req = Request(url)
	cookiejar.add_cookie_header(req)
	cookie_hdr = req.get_header("Cookie", "")
	headers = []
	for hdr in set_cookie_hdrs:
		headers.append("%s: %s" % (hdr_name, hdr))
	res = FakeResponse(headers, url)
	cookiejar.extract_cookies(res, req)
	return cookie_hdr


class CookieTests(TestCase):
	# XXX
	# IP addresses like 50 (single number, no dot) and domain-matching
	#  functions (and is_HDN)?	See draft RFC 2965 errata.
	# Strictness switches
	# is_third_party()
	# unverifiability / third_party blocking
	# Netscape cookies work the same as RFC 2965 with regard to port.
	# Set-Cookie with negative max age.
	# If turn RFC 2965 handling off, Set-Cookie2 cookies should not clobber
	#  Set-Cookie cookies.
	# Cookie2 should be sent if *any* cookies are not V1 (ie. V0 OR V2 etc.).
	# Cookies (V1 and V0) with no expiry date should be set to be discarded.
	# RFC 2965 Quoting:
	#  Should accept unquoted cookie-attribute values?	check errata draft.
	#	Which are required on the way in and out?
	#  Should always return quoted cookie-attribute values?
	# Proper testing of when RFC 2965 clobbers Netscape (waiting for errata).
	# Path-match on return (same for V0 and V1).
	# RFC 2965 acceptance and returning rules
	#  Set-Cookie2 without version attribute is rejected.

	# Netscape peculiarities list from Ronald Tschalar.
	# The first two still need tests, the rest are covered.
## - Quoting: only quotes around the expires value are recognized as such
##	 (and yes, some folks quote the expires value); quotes around any other
##	 value are treated as part of the value.
## - White space: white space around names and values is ignored
## - Default path: if no path parameter is given, the path defaults to the
##	 path in the request-uri up to, but not including, the last '/'. Note
##	 that this is entirely different from what the spec says.
## - Commas and other delimiters: Netscape just parses until the next ';'.
##	 This means it will allow commas etc inside values (and yes, both
##	 commas and equals are commonly appear in the cookie value). This also
##	 means that if you fold multiple Set-Cookie header fields into one,
##	 comma-separated list, it'll be a headache to parse (at least my head
##	 starts hurting everytime I think of that code).
## - Expires: You'll get all sorts of date formats in the expires,
##	 including emtpy expires attributes ("expires="). Be as flexible as you
##	 can, and certainly don't expect the weekday to be there; if you can't
##	 parse it, just ignore it and pretend it's a session cookie.
## - Domain-matching: Netscape uses the 2-dot rule for _all_ domains, not
##	 just the 7 special TLD's listed in their spec. And folks rely on
##	 that...

	def test_ns_parser(self):
		from mechanoid.cookiejar.CookieJar import CookieJar
		

		common = Common()
		c = CookieJar()
		interact_netscape(c, "http://www.acme.com/",
						  'spam=eggs; DoMain=.acme.com; port; blArgh="feep"')
		interact_netscape(c, "http://www.acme.com/", 'ni=ni; port=80,8080')
		interact_netscape(c, "http://www.acme.com:80/", 'nini=ni')
		interact_netscape(c, "http://www.acme.com:80/", 'foo=bar; expires=')
		interact_netscape(c, "http://www.acme.com:80/", 'spam=eggs; '
						  'expires="Foo Bar 25 33:22:11 3022"')

		cookie = c.cookies[".acme.com"]["/"]["spam"]
		assert cookie.domain == ".acme.com"
		assert cookie.domain_specified
		assert cookie.port == common.DEFAULT_HTTP_PORT
		assert not cookie.port_specified
		# case is preserved
		assert cookie.rest.has_key("blArgh") and not cookie.rest.has_key("blargh")

		cookie = c.cookies["www.acme.com"]["/"]["ni"]
		assert cookie.domain == "www.acme.com"
		assert not cookie.domain_specified
		assert cookie.port == "80,8080"
		assert cookie.port_specified

		cookie = c.cookies["www.acme.com"]["/"]["nini"]
		assert cookie.port is None
		assert not cookie.port_specified

		# invalid expires should not cause cookie to be dropped
		foo = c.cookies["www.acme.com"]["/"]["foo"]
		spam = c.cookies["www.acme.com"]["/"]["foo"]
		assert foo.expires is None
		assert spam.expires is None

		# XXX RFC 2965 expiry rules (some apply to V0 too)

	def test_default_path(self):
		from mechanoid.cookiejar.CookieJar import CookieJar

		# RFC 2965

		c = CookieJar()
		interact_2965(c, "http://www.acme.com/", 'spam="bar"; Version="1"')
		assert c.cookies["www.acme.com"].has_key("/")

		c = CookieJar()
		interact_2965(c, "http://www.acme.com/blah", 'eggs="bar"; Version="1"')
		assert c.cookies["www.acme.com"].has_key("/")
  
		c = CookieJar()
		interact_2965(c, "http://www.acme.com/blah/rhubarb",
					  'eggs="bar"; Version="1"')
		assert c.cookies["www.acme.com"].has_key("/blah/")

		c = CookieJar()
		interact_2965(c, "http://www.acme.com/blah/rhubarb/",
					  'eggs="bar"; Version="1"')
		assert c.cookies["www.acme.com"].has_key("/blah/rhubarb/")

		# Netscape

		c = CookieJar()
		interact_netscape(c, "http://www.acme.com/", 'spam="bar"')
		assert c.cookies["www.acme.com"].has_key("/")

		c = CookieJar()
		interact_netscape(c, "http://www.acme.com/blah", 'eggs="bar"')
		assert c.cookies["www.acme.com"].has_key("/")
  
		c = CookieJar()
		interact_netscape(c, "http://www.acme.com/blah/rhubarb", 'eggs="bar"')
		assert c.cookies["www.acme.com"].has_key("/blah")

		c = CookieJar()
		interact_netscape(c, "http://www.acme.com/blah/rhubarb/", 'eggs="bar"')
		assert c.cookies["www.acme.com"].has_key("/blah/rhubarb")

	def test_escape_path(self):
		
		common = Common()
		cases = [
			# quoted safe
			("/foo%2f/bar", "/foo%2F/bar"),
			("/foo%2F/bar", "/foo%2F/bar"),
			# quoted %
			("/foo%%/bar", "/foo%%/bar"),
			# quoted unsafe
			("/fo%19o/bar", "/fo%19o/bar"),
			("/fo%7do/bar", "/fo%7Do/bar"),
			# unquoted safe
			("/foo/bar&", "/foo/bar&"),
			("/foo//bar", "/foo//bar"),
			("\176/foo/bar", "\176/foo/bar"),
			# unquoted unsafe
			("/foo\031/bar", "/foo%19/bar"),
			("/\175foo/bar", "/%7Dfoo/bar"),
			]
# XXXX causes SyntaxError with 1.5.2
##		   try:
##			   unicode
##		   except NameError:
##			   pass
##		   else:
##			   cases.append(
##			   # unicode
##			   (u"/foo/bar\uabcd", "/foo/bar%EA%AF%8D")	 # UTF-8 encoded
##			   )
		for arg, result in cases:
			self.assert_(common.escape_path(arg) == result)

	def test_request_path(self):
		from urllib2 import Request
		
		common = Common()
		# with parameters
		req = Request("http://www.example.com/rheum/rhaponicum;"
					  "foo=bar;sing=song?apples=pears&spam=eggs#ni")
		self.assert_(common.request_path(req) == "/rheum/rhaponicum;"
					 "foo=bar;sing=song?apples=pears&spam=eggs#ni")
		# without parameters
		req = Request("http://www.example.com/rheum/rhaponicum?"
					  "apples=pears&spam=eggs#ni")
		self.assert_(common.request_path(req) == "/rheum/rhaponicum?"
					 "apples=pears&spam=eggs#ni")
		# missing final slash
		req = Request("http://www.example.com")
		self.assert_(common.request_path(req) == "/")

	def test_request_port(self):
		from mechanoid.misc.Request import Request
		
		common = Common()
		req = Request("http://www.acme.com:1234/",
					  headers={"Host": "www.acme.com:4321"})
		assert common.request_port(req) == "1234"
		req = Request("http://www.acme.com/",
					  headers={"Host": "www.acme.com:4321"})
		assert common.request_port(req) == common.DEFAULT_HTTP_PORT

	def test_request_host(self):
		from mechanoid.misc.Request import Request
		
		common = Common()
		# this request is illegal (RFC2616, 14.2.3)
		req = Request("http://1.1.1.1/",
					  headers={"Host": "www.acme.com:80"})
		# libwww-perl wants this response, but that seems wrong (RFC 2616,
		# section 5.2, point 1., and RFC 2965 section 1, paragraph 3)
		#assert request_host(req) == "www.acme.com"
		assert common.request_host(req) == "1.1.1.1"
		req = Request("http://www.acme.com/",
					  headers={"Host": "irrelevant.com"})
		assert common.request_host(req) == "www.acme.com"
		# not actually sure this one is valid Request object, so maybe should
		# remove test for no host in url in request_host function?
		req = Request("/resource.html",
					  headers={"Host": "www.acme.com"})
		assert common.request_host(req) == "www.acme.com"
		# port shouldn't be in request-host
		req = Request("http://www.acme.com:2345/resource.html",
					  headers={"Host": "www.acme.com:5432"})
		assert common.request_host(req) == "www.acme.com"

	def test_is_HDN(self):
		
		common = Common()
		assert common.is_HDN("foo.bar.com")
		assert common.is_HDN("1foo2.3bar4.5com")
		assert not common.is_HDN("192.168.1.1")
		assert not common.is_HDN("")
		assert not common.is_HDN(".")
		assert not common.is_HDN(".foo.bar.com")
		assert not common.is_HDN("..foo")
		assert not common.is_HDN("foo.")

	def test_reach(self):
		
		common = Common()
		assert common.reach("www.acme.com") == ".acme.com"
		assert common.reach("acme.com") == "acme.com"
		assert common.reach("acme.local") == ".local"
		assert common.reach(".local") == ".local"
		assert common.reach(".com") == ".com"
		assert common.reach(".") == "."
		assert common.reach("") == ""
		assert common.reach("192.168.0.1") == "192.168.0.1"

	def test_domain_match(self):
		
		common = Common()
		assert common.domain_match("192.168.1.1", "192.168.1.1")
		assert not common.domain_match("192.168.1.1", ".168.1.1")
		assert common.domain_match("x.y.com", "x.Y.com")
		assert common.domain_match("x.y.com", ".Y.com")
		assert not common.domain_match("x.y.com", "Y.com")
		assert common.domain_match("a.b.c.com", ".c.com")
		assert not common.domain_match(".c.com", "a.b.c.com")
		assert common.domain_match("example.local", ".local")
		assert not common.domain_match("blah.blah", "")
		assert not common.domain_match("", ".rhubarb.rhubarb")
		assert common.domain_match("", "")

		assert common.user_domain_match("acme.com", "acme.com")
		assert not common.user_domain_match("acme.com", ".acme.com")
		assert common.user_domain_match("rhubarb.acme.com", ".acme.com")
		assert common.user_domain_match("www.rhubarb.acme.com", ".acme.com")
		assert common.user_domain_match("x.y.com", "x.Y.com")
		assert common.user_domain_match("x.y.com", ".Y.com")
		assert not common.user_domain_match("x.y.com", "Y.com")
		assert common.user_domain_match("y.com", "Y.com")
		assert not common.user_domain_match(".y.com", "Y.com")
		assert common.user_domain_match(".y.com", ".Y.com")
		assert common.user_domain_match("x.y.com", ".com")
		assert not common.user_domain_match("x.y.com", "com")
		assert not common.user_domain_match("x.y.com", "m")
		assert not common.user_domain_match("x.y.com", ".m")
		assert not common.user_domain_match("x.y.com", "")
		assert not common.user_domain_match("x.y.com", ".")
		assert common.user_domain_match("192.168.1.1", "192.168.1.1")
		# not both HDNs, so must string-compare equal to match
		assert not common.user_domain_match("192.168.1.1", ".168.1.1")
		assert not common.user_domain_match("192.168.1.1", ".")
		# empty string is a special case
		assert not common.user_domain_match("192.168.1.1", "")

	def test_wrong_domain(self):
		"""Cookies whose ERH does not domain-match the domain are rejected.

		ERH = effective request-host.

		"""
		# XXX far from complete
		from mechanoid.cookiejar.CookieJar import CookieJar
		c = CookieJar()
		interact_2965(c, "http://www.nasty.com/", 'foo=bar; domain=friendly.org; Version="1"')
		assert len(c) == 0

	def test_two_component_domain_ns(self):
		# Netscape: .www.bar.com, www.bar.com, .bar.com, bar.com, no domain should
		#  all get accepted, as should .acme.com, acme.com and no domain for
		#  2-component domains like acme.com.
		from mechanoid.cookiejar.CookieJar import CookieJar
		from mechanoid.cookiejar.DefaultCookiePolicy import DefaultCookiePolicy

		c = CookieJar()

		# two-component V0 domain is OK
		interact_netscape(c, "http://foo.net/", 'ns=bar')
		assert len(c) == 1
		assert c.cookies["foo.net"]["/"]["ns"].value == "bar"
		assert interact_netscape(c, "http://foo.net/") == "ns=bar"
		# *will* be returned to any other domain (unlike RFC 2965)...
		assert interact_netscape(c, "http://www.foo.net/") == "ns=bar"
		# ...unless requested otherwise
		c.policy.strict_ns_domain = DefaultCookiePolicy.DomainStrictNonDomain
		assert interact_netscape(c, "http://www.foo.net/") == ""

		# unlike RFC 2965, even explicit two-component domain is OK,
		# because .foo.net matches foo.net
		interact_netscape(c, "http://foo.net/foo/",
						  'spam1=eggs; domain=foo.net')
		# even if starts with a dot -- in NS rules, .foo.net matches foo.net!
		interact_netscape(c, "http://foo.net/foo/bar/",
						  'spam2=eggs; domain=.foo.net')
		assert len(c) == 3
		assert c.cookies[".foo.net"]["/foo"]["spam1"].value == "eggs"
		assert c.cookies[".foo.net"]["/foo/bar"]["spam2"].value == "eggs"
		assert interact_netscape(c, "http://foo.net/foo/bar/") == \
			   "spam2=eggs; spam1=eggs; ns=bar"

		# top-level domain is too general
		interact_netscape(c, "http://foo.net/", 'nini="ni"; domain=.net')
		assert len(c) == 3

##		   # Netscape protocol doesn't allow non-special top level domains (such
##		   # as co.uk) in the domain attribute unless there are at least three
##		   # dots in it.
		# Oh yes it does!  Real implementations don't check this, and real
		# cookies (of course) rely on that behaviour.
		interact_netscape(c, "http://foo.co.uk", 'nasty=trick; domain=.co.uk')
##		   assert len(c) == 2
		assert len(c) == 4

	def test_two_component_domain_rfc2965(self):
		from mechanoid.cookiejar.CookieJar import CookieJar

		c = CookieJar()

		# two-component V1 domain is OK
		interact_2965(c, "http://foo.net/", 'foo=bar; Version="1"')
		assert len(c) == 1
		assert c.cookies["foo.net"]["/"]["foo"].value == "bar"
		assert interact_2965(c, "http://foo.net/") == "$Version=1; foo=bar"
		# won't be returned to any other domain (because domain was implied)
		assert interact_2965(c, "http://www.foo.net/") == ""

		# unless domain is given explicitly, because then it must be
		# rewritten to start with a dot: foo.net --> .foo.net, which does
		# not domain-match foo.net
		interact_2965(c, "http://foo.net/foo",
					  'spam=eggs; domain=foo.net; path=/foo; Version="1"')
		assert len(c) == 1
		assert interact_2965(c, "http://foo.net/foo") == "$Version=1; foo=bar"

		# explicit foo.net from three-component domain www.foo.net *does* get
		# set, because .foo.net domain-matches .foo.net
		interact_2965(c, "http://www.foo.net/foo/",
					  'spam=eggs; domain=foo.net; Version="1"')
		assert c.cookies[".foo.net"]["/foo/"]["spam"].value == "eggs"
		assert len(c) == 2
		assert interact_2965(c, "http://foo.net/foo/") == "$Version=1; foo=bar"
		assert interact_2965(c, "http://www.foo.net/foo/") == \
			   '$Version=1; spam=eggs; $Domain="foo.net"'

		# top-level domain is too general
		interact_2965(c, "http://foo.net/",
					  'ni="ni"; domain=".net"; Version="1"')
		assert len(c) == 2

		# RFC 2965 doesn't require blocking this
		interact_2965(c, "http://foo.co.uk/",
					  'nasty=trick; domain=.co.uk; Version="1"')
		assert len(c) == 3

	def test_domain_allow(self):
		from mechanoid.cookiejar.CookieJar import CookieJar
		from mechanoid.cookiejar.DefaultCookiePolicy import DefaultCookiePolicy
		from mechanoid.misc.Request import Request

		c = CookieJar(policy=DefaultCookiePolicy(
			blocked_domains=["acme.com"],
			allowed_domains=["www.acme.com"]))

		req = Request("http://acme.com/")
		headers = ["Set-Cookie: CUSTOMER=WILE_E_COYOTE; path=/"]
		res = FakeResponse(headers, "http://acme.com/")
		c.extract_cookies(res, req)
		assert len(c) == 0

		req = Request("http://www.acme.com/")
		res = FakeResponse(headers, "http://www.acme.com/")
		c.extract_cookies(res, req)
		assert len(c) == 1

		req = Request("http://www.coyote.com/")
		res = FakeResponse(headers, "http://www.coyote.com/")
		c.extract_cookies(res, req)
		assert len(c) == 1

		# set a cookie with non-allowed domain...
		req = Request("http://www.coyote.com/")
		res = FakeResponse(headers, "http://www.coyote.com/")
		cookies = c.make_cookies(res, req)
		c.set_cookie(cookies[0])
		assert len(c) == 2
		# ... and check is doesn't get returned
		c.add_cookie_header(req)
		assert not req.has_header("Cookie")

	def test_domain_block(self):
		from mechanoid.cookiejar.CookieJar import CookieJar
		from mechanoid.cookiejar.DefaultCookiePolicy import DefaultCookiePolicy
		from mechanoid.misc.Request import Request

		c = CookieJar(policy=DefaultCookiePolicy(
			blocked_domains=[".acme.com"]))
		headers = ["Set-Cookie: CUSTOMER=WILE_E_COYOTE; path=/"]

		req = Request("http://www.acme.com/")
		res = FakeResponse(headers, "http://www.acme.com/")
		c.extract_cookies(res, req)
		assert len(c) == 0

		c.policy.set_blocked_domains(["acme.com"])
		c.extract_cookies(res, req)
		assert len(c) == 1

		c.clear()
		req = Request("http://www.roadrunner.net/")
		res = FakeResponse(headers, "http://www.roadrunner.net/")
		c.extract_cookies(res, req)
		assert len(c) == 1
		req = Request("http://www.roadrunner.net/")
		c.add_cookie_header(req)
		assert (req.has_header("Cookie") and
				req.has_header("Cookie2"))

		c.clear()
		c.policy.set_blocked_domains([".acme.com"])
		c.extract_cookies(res, req)
		assert len(c) == 1

		# set a cookie with blocked domain...
		req = Request("http://www.acme.com/")
		res = FakeResponse(headers, "http://www.acme.com/")
		cookies = c.make_cookies(res, req)
		c.set_cookie(cookies[0])
		assert len(c) == 2
		# ... and check is doesn't get returned
		c.add_cookie_header(req)
		assert not req.has_header("Cookie")

	def test_secure(self):
		from mechanoid.cookiejar.CookieJar import CookieJar
		from mechanoid.cookiejar.DefaultCookiePolicy import DefaultCookiePolicy

		for ns in True, False:
			for whitespace in " ", "":
				c = CookieJar()
				if ns:
					c.policy.rfc2965 = False
					int = interact_netscape
					vs = ""
				else:
					c.policy.rfc2965 = True
					int = interact_2965
					vs = "; Version=1"
				url = "http://www.acme.com/"
				int(c, url, "foo1=bar%s%s" % (vs, whitespace))
				int(c, url, "foo2=bar%s; secure%s" %  (vs, whitespace))
				assert not c.cookies["www.acme.com"]["/"]["foo1"].secure, \
					   "non-secure cookie registered secure"
				assert c.cookies["www.acme.com"]["/"]["foo2"].secure, \
					   "secure cookie registered non-secure"

	def test_quote_cookie_value(self):
		from mechanoid.cookiejar.CookieJar import CookieJar
		c = CookieJar()
		interact_2965(c, "http://www.acme.com/", r'foo=\b"a"r; Version=1')
		h = interact_2965(c, "http://www.acme.com/")
		assert h == r'$Version=1; foo=\\b\"a\"r'

	def test_missing_final_slash(self):
		# Missing slash from request URL's abs_path should be assumed present.
		from mechanoid.cookiejar.CookieJar import CookieJar
		from mechanoid.misc.Request import Request
		url = "http://www.acme.com"
		c = CookieJar()
		interact_2965(c, url, "foo=bar; Version=1")
		req = Request(url)
		assert len(c) == 1
		c.add_cookie_header(req)
		assert req.has_header("Cookie")

	def test_domain_mirror(self):
		from mechanoid.cookiejar.CookieJar import CookieJar

		c = CookieJar()
		url = "http://foo.bar.com/"
		interact_2965(c, url, "spam=eggs; Version=1")
		h = interact_2965(c, url)
		assert string.find("Domain", h) == -1, \
			   "absent domain returned with domain present"

		c = CookieJar()
		url = "http://foo.bar.com/"
		interact_2965(c, url, 'spam=eggs; Version=1; Domain=.bar.com')
		h = interact_2965(c, url)
		assert string.find(h, '$Domain=".bar.com"') != -1, \
			   "domain not returned"

		c = CookieJar()
		url = "http://foo.bar.com/"
		# note missing initial dot in Domain
		interact_2965(c, url, 'spam=eggs; Version=1; Domain=bar.com')
		h = interact_2965(c, url)
		assert string.find(h, '$Domain="bar.com"') != -1, \
			   "domain not returned"

	def test_path_mirror(self):
		from mechanoid.cookiejar.CookieJar import CookieJar

		c = CookieJar()
		url = "http://foo.bar.com/"
		interact_2965(c, url, "spam=eggs; Version=1")
		h = interact_2965(c, url)
		assert string.find("Path", h) == -1, \
			   "absent path returned with path present"

		c = CookieJar()
		url = "http://foo.bar.com/"
		interact_2965(c, url, 'spam=eggs; Version=1; Path=/')
		h = interact_2965(c, url)
		assert string.find(h, '$Path="/"') != -1, "path not returned"

	def test_port_mirror(self):
		from mechanoid.cookiejar.CookieJar import CookieJar

		c = CookieJar()
		url = "http://foo.bar.com/"
		interact_2965(c, url, "spam=eggs; Version=1")
		h = interact_2965(c, url)
		assert string.find("Port", h) == -1, \
			   "absent port returned with port present"

		c = CookieJar()
		url = "http://foo.bar.com/"
		interact_2965(c, url, "spam=eggs; Version=1; Port")
		h = interact_2965(c, url)
		assert re.search("\$Port([^=]|$)", h), \
			   "port with no value not returned with no value"

		c = CookieJar()
		url = "http://foo.bar.com/"
		interact_2965(c, url, 'spam=eggs; Version=1; Port="80"')
		h = interact_2965(c, url)
		assert string.find(h, '$Port="80"') != -1, \
			   "port with single value not returned with single value"

		c = CookieJar()
		url = "http://foo.bar.com/"
		interact_2965(c, url, 'spam=eggs; Version=1; Port="80,8080"')
		h = interact_2965(c, url)
		assert string.find(h, '$Port="80,8080"') != -1, \
			   "port with multiple values not returned with multiple values"

	def test_no_return_comment(self):
		from mechanoid.cookiejar.CookieJar import CookieJar

		c = CookieJar()
		url = "http://foo.bar.com/"
		interact_2965(c, url, 'spam=eggs; Version=1; '
					  'Comment="does anybody read these?"; '
					  'CommentURL="http://foo.bar.net/comment.html"')
		h = interact_2965(c, url)
		assert string.find("Comment", h) == -1, \
			   "Comment or CommentURL cookie-attributes returned to server"


	def test_Cookie_iterator(self):
		from mechanoid.cookiejar.CookieJar import CookieJar
		from mechanoid.cookiejar.Cookie import Cookie

		cs = CookieJar()
		# add some random cookies
		interact_2965(cs, "http://blah.spam.org/", 'foo=eggs; Version=1; '
					  'Comment="does anybody read these?"; '
					  'CommentURL="http://foo.bar.net/comment.html"')
		interact_netscape(cs, "http://www.acme.com/blah/", "spam=bar; secure")
		interact_2965(cs, "http://www.acme.com/blah/", "foo=bar; secure; Version=1")
		interact_2965(cs, "http://www.acme.com/blah/", "foo=bar; path=/; Version=1")
		interact_2965(cs, "http://www.sol.no",
					  r'bang=wallop; version=1; domain=".sol.no"; '
					  r'port="90,100, 80,8080"; '
					  r'max-age=100; Comment = "Just kidding! (\"|\\\\) "')

		versions = [1, 1, 1, 0, 1, 1]
		names = ["bang", "foo", "foo", "spam", "foo"]
		domains = [".sol.no", "blah.spam.org", "www.acme.com",
				   "www.acme.com", "www.acme.com"]
		paths = ["/", "/", "/", "/blah", "/blah/", "/"]

		# sequential iteration
		for i in range(3):
			i = 0
			for c in cs:
				assert isinstance(c, Cookie)
				assert c.version == versions[i]
				assert c.name == names[i]
				assert c.domain == domains[i]
				assert c.path == paths[i]
				i = i + 1

		self.assertRaises(IndexError, lambda cs=cs : cs[5])

		# can't skip
		cs[0]
		cs[1]
		self.assertRaises(IndexError, lambda cs=cs : cs[3])

		# can't go backwards
		cs[0]
		cs[1]
		cs[2]
		self.assertRaises(IndexError, lambda cs=cs : cs[1])

	def test_parse_ns_headers(self):
		from mechanoid.cookiejar.Header_Utils import Header_Utils
		h = Header_Utils()

		# missing domain value (invalid cookie)
		assert h.parse_ns_headers(["foo=bar; path=/; domain"]) == [
			[("foo", "bar"),
			 ("path", "/"), ("domain", None), ("version", "0")]]
		# invalid expires value
		assert h.parse_ns_headers(
			["foo=bar; expires=Foo Bar 12 33:22:11 2000"]) == \
			[[("foo", "bar"), ("expires", None), ("version", "0")]]
		# missing cookie name (valid cookie)
		assert h.parse_ns_headers(["foo"]) == [[(None, "foo"), ("version", "0")]]
		# shouldn't add version if header is empty
		assert h.parse_ns_headers([""]) == []

	def test_bad_cookie_header(self):

		def cookiejar_from_cookie_headers(headers):
			from mechanoid.cookiejar.CookieJar import CookieJar
			from mechanoid.misc.Request import Request
			c = CookieJar()
			req = Request("http://www.example.com/")
			r = FakeResponse(headers, "http://www.example.com/")
			c.extract_cookies(r, req)
			return c

		# none of these bad headers should cause an exception to be raised
		for headers in [
			["Set-Cookie: "],  # actually, nothing wrong with this
			["Set-Cookie2: "],	# ditto
			# missing domain value
			["Set-Cookie2: a=foo; path=/; Version=1; domain"],
			# bad max-age
			["Set-Cookie: b=foo; max-age=oops"],
			]:
			c = cookiejar_from_cookie_headers(headers)
			# these bad cookies shouldn't be set
			assert len(c) == 0

		# cookie with invalid expires is treated as session cookie
		headers = ["Set-Cookie: c=foo; expires=Foo Bar 12 33:22:11 2000"]
		c = cookiejar_from_cookie_headers(headers)
		cookie = c.cookies["www.example.com"]["/"]["c"]
		assert cookie.expires is None


class LWPCookieTests(TestCase):
	# Tests taken from libwww-perl, with a few modifications.

	def test_netscape_example_1(self):
		from mechanoid.cookiejar.CookieJar import CookieJar
		from mechanoid.misc.Request import Request


		#-------------------------------------------------------------------
		# First we check that it works for the original example at
		# http://www.netscape.com/newsref/std/cookie_spec.html

		# Client requests a document, and receives in the response:
		# 
		#		Set-Cookie: CUSTOMER=WILE_E_COYOTE; path=/; expires=Wednesday, 09-Nov-99 23:12:40 GMT
		# 
		# When client requests a URL in path "/" on this server, it sends:
		# 
		#		Cookie: CUSTOMER=WILE_E_COYOTE
		# 
		# Client requests a document, and receives in the response:
		# 
		#		Set-Cookie: PART_NUMBER=ROCKET_LAUNCHER_0001; path=/
		# 
		# When client requests a URL in path "/" on this server, it sends:
		# 
		#		Cookie: CUSTOMER=WILE_E_COYOTE; PART_NUMBER=ROCKET_LAUNCHER_0001
		# 
		# Client receives:
		# 
		#		Set-Cookie: SHIPPING=FEDEX; path=/fo
		# 
		# When client requests a URL in path "/" on this server, it sends:
		# 
		#		Cookie: CUSTOMER=WILE_E_COYOTE; PART_NUMBER=ROCKET_LAUNCHER_0001
		# 
		# When client requests a URL in path "/foo" on this server, it sends:
		# 
		#		Cookie: CUSTOMER=WILE_E_COYOTE; PART_NUMBER=ROCKET_LAUNCHER_0001; SHIPPING=FEDEX
		# 
		# The last Cookie is buggy, because both specifications say that the
		# most specific cookie must be sent first.	SHIPPING=FEDEX is the
		# most specific and should thus be first.

		year_plus_one = localtime(time.time())[0] + 1

		headers = []

		c = CookieJar()

		#req = Request("http://1.1.1.1/",
		#			   headers={"Host": "www.acme.com:80"})
		req = Request("http://www.acme.com:80/",
					  headers={"Host": "www.acme.com:80"})

		headers.append(
			"Set-Cookie: CUSTOMER=WILE_E_COYOTE; path=/ ; "
			"expires=Wednesday, 09-Nov-%d 23:12:40 GMT" % year_plus_one)
		res = FakeResponse(headers, "http://www.acme.com/")
		c.extract_cookies(res, req)

		req = Request("http://www.acme.com/")
		c.add_cookie_header(req)

		assert (req.get_header("Cookie") == "CUSTOMER=WILE_E_COYOTE" and
				req.get_header("Cookie2") == '$Version="1"')

		headers.append("Set-Cookie: PART_NUMBER=ROCKET_LAUNCHER_0001; path=/")
		res = FakeResponse(headers, "http://www.acme.com/")
		c.extract_cookies(res, req)

		req = Request("http://www.acme.com/foo/bar")
		c.add_cookie_header(req)

		h = req.get_header("Cookie")
		assert (string.find(h, "PART_NUMBER=ROCKET_LAUNCHER_0001") != -1 and
				string.find(h, "CUSTOMER=WILE_E_COYOTE") != -1)


		headers.append('Set-Cookie: SHIPPING=FEDEX; path=/foo')
		res = FakeResponse(headers, "http://www.acme.com")
		c.extract_cookies(res, req)

		req = Request("http://www.acme.com/")
		c.add_cookie_header(req)

		h = req.get_header("Cookie")
		assert (string.find(h, "PART_NUMBER=ROCKET_LAUNCHER_0001") != -1 and
				string.find(h, "CUSTOMER=WILE_E_COYOTE") != -1 and
				not string.find(h, "SHIPPING=FEDEX") != -1)


		req = Request("http://www.acme.com/foo/")
		c.add_cookie_header(req)

		h = req.get_header("Cookie")
		assert (string.find(h, "PART_NUMBER=ROCKET_LAUNCHER_0001") != -1 and
				string.find(h, "CUSTOMER=WILE_E_COYOTE") != -1 and
				common.startswith(h, "SHIPPING=FEDEX;"))

	def test_netscape_example_2(self):
		from mechanoid.cookiejar.CookieJar import CookieJar
		from mechanoid.misc.Request import Request

		# Second Example transaction sequence:
		# 
		# Assume all mappings from above have been cleared.
		# 
		# Client receives:
		# 
		#		Set-Cookie: PART_NUMBER=ROCKET_LAUNCHER_0001; path=/
		# 
		# When client requests a URL in path "/" on this server, it sends:
		# 
		#		Cookie: PART_NUMBER=ROCKET_LAUNCHER_0001
		# 
		# Client receives:
		# 
		#		Set-Cookie: PART_NUMBER=RIDING_ROCKET_0023; path=/ammo
		# 
		# When client requests a URL in path "/ammo" on this server, it sends:
		# 
		#		Cookie: PART_NUMBER=RIDING_ROCKET_0023; PART_NUMBER=ROCKET_LAUNCHER_0001
		# 
		#		NOTE: There are two name/value pairs named "PART_NUMBER" due to
		#		the inheritance of the "/" mapping in addition to the "/ammo" mapping. 

		c = CookieJar()
		headers = []

		req = Request("http://www.acme.com/")
		headers.append("Set-Cookie: PART_NUMBER=ROCKET_LAUNCHER_0001; path=/")
		res = FakeResponse(headers, "http://www.acme.com/")

		c.extract_cookies(res, req)

		req = Request("http://www.acme.com/")
		c.add_cookie_header(req)

		assert (req.get_header("Cookie") == "PART_NUMBER=ROCKET_LAUNCHER_0001")

		headers.append(
			"Set-Cookie: PART_NUMBER=RIDING_ROCKET_0023; path=/ammo")
		res = FakeResponse(headers, "http://www.acme.com/")
		c.extract_cookies(res, req)

		req = Request("http://www.acme.com/ammo")
		c.add_cookie_header(req)

		assert re.search(r"PART_NUMBER=RIDING_ROCKET_0023;\s*"
						 "PART_NUMBER=ROCKET_LAUNCHER_0001",
						 req.get_header("Cookie"))

	def test_ietf_example_1(self):
		from mechanoid.cookiejar.CookieJar import CookieJar
		#-------------------------------------------------------------------
		# Then we test with the examples from draft-ietf-http-state-man-mec-03.txt
		#
		# 5.  EXAMPLES

		c = CookieJar()

		# 
		# 5.1  Example 1
		# 
		# Most detail of request and response headers has been omitted.	 Assume
		# the user agent has no stored cookies.
		# 
		#	1.	User Agent -> Server
		# 
		#		POST /acme/login HTTP/1.1
		#		[form data]
		# 
		#		User identifies self via a form.
		# 
		#	2.	Server -> User Agent
		# 
		#		HTTP/1.1 200 OK
		#		Set-Cookie2: Customer="WILE_E_COYOTE"; Version="1"; Path="/acme"
		# 
		#		Cookie reflects user's identity.

		cookie = interact_2965(
			c, 'http://www.acme.com/acme/login',
			'Customer="WILE_E_COYOTE"; Version="1"; Path="/acme"')
		assert not cookie

		# 
		#	3.	User Agent -> Server
		# 
		#		POST /acme/pickitem HTTP/1.1
		#		Cookie: $Version="1"; Customer="WILE_E_COYOTE"; $Path="/acme"
		#		[form data]
		# 
		#		User selects an item for ``shopping basket.''
		# 
		#	4.	Server -> User Agent
		# 
		#		HTTP/1.1 200 OK
		#		Set-Cookie2: Part_Number="Rocket_Launcher_0001"; Version="1";
		#				Path="/acme"
		# 
		#		Shopping basket contains an item.

		cookie = interact_2965(c, 'http://www.acme.com/acme/pickitem',
							   'Part_Number="Rocket_Launcher_0001"; '
							   'Version="1"; Path="/acme"');
		assert re.search(
			r'^\$Version="?1"?; Customer="?WILE_E_COYOTE"?; \$Path="/acme"$',
			cookie)

		# 
		#	5.	User Agent -> Server
		# 
		#		POST /acme/shipping HTTP/1.1
		#		Cookie: $Version="1";
		#				Customer="WILE_E_COYOTE"; $Path="/acme";
		#				Part_Number="Rocket_Launcher_0001"; $Path="/acme"
		#		[form data]
		# 
		#		User selects shipping method from form.
		# 
		#	6.	Server -> User Agent
		# 
		#		HTTP/1.1 200 OK
		#		Set-Cookie2: Shipping="FedEx"; Version="1"; Path="/acme"
		# 
		#		New cookie reflects shipping method.

		cookie = interact_2965(c, "http://www.acme.com/acme/shipping",
							   'Shipping="FedEx"; Version="1"; Path="/acme"')

		assert (re.search(r'^\$Version="?1"?;', cookie) and
				re.search(r'Part_Number="?Rocket_Launcher_0001"?;'
						  '\s*\$Path="\/acme"', cookie) and
				re.search(r'Customer="?WILE_E_COYOTE"?;\s*\$Path="\/acme"',
						  cookie))

		# 
		#	7.	User Agent -> Server
		# 
		#		POST /acme/process HTTP/1.1
		#		Cookie: $Version="1";
		#				Customer="WILE_E_COYOTE"; $Path="/acme";
		#				Part_Number="Rocket_Launcher_0001"; $Path="/acme";
		#				Shipping="FedEx"; $Path="/acme"
		#		[form data]
		# 
		#		User chooses to process order.
		# 
		#	8.	Server -> User Agent
		# 
		#		HTTP/1.1 200 OK
		# 
		#		Transaction is complete.

		cookie = interact_2965(c, "http://www.acme.com/acme/process")
		assert (re.search(r'Shipping="?FedEx"?;\s*\$Path="\/acme"', cookie) and
				string.find(cookie, "WILE_E_COYOTE") != -1)

		# 
		# The user agent makes a series of requests on the origin server, after
		# each of which it receives a new cookie.  All the cookies have the same
		# Path attribute and (default) domain.	Because the request URLs all have
		# /acme as a prefix, and that matches the Path attribute, each request
		# contains all the cookies received so far.

	def test_ietf_example_2(self):
		from mechanoid.cookiejar.CookieJar import CookieJar

		# 5.2  Example 2
		# 
		# This example illustrates the effect of the Path attribute.  All detail
		# of request and response headers has been omitted.	 Assume the user agent
		# has no stored cookies.

		c = CookieJar()

		# Imagine the user agent has received, in response to earlier requests,
		# the response headers
		# 
		# Set-Cookie2: Part_Number="Rocket_Launcher_0001"; Version="1";
		#		  Path="/acme"
		# 
		# and
		# 
		# Set-Cookie2: Part_Number="Riding_Rocket_0023"; Version="1";
		#		  Path="/acme/ammo"

		interact_2965(
			c, "http://www.acme.com/acme/ammo/specific",
			'Part_Number="Rocket_Launcher_0001"; Version="1"; Path="/acme"',
			'Part_Number="Riding_Rocket_0023"; Version="1"; Path="/acme/ammo"')

		# A subsequent request by the user agent to the (same) server for URLs of
		# the form /acme/ammo/...  would include the following request header:
		# 
		# Cookie: $Version="1";
		#		  Part_Number="Riding_Rocket_0023"; $Path="/acme/ammo";
		#		  Part_Number="Rocket_Launcher_0001"; $Path="/acme"
		# 
		# Note that the NAME=VALUE pair for the cookie with the more specific Path
		# attribute, /acme/ammo, comes before the one with the less specific Path
		# attribute, /acme.	 Further note that the same cookie name appears more
		# than once.

		cookie = interact_2965(c, "http://www.acme.com/acme/ammo/...")
		assert re.search(r"Riding_Rocket_0023.*Rocket_Launcher_0001", cookie)

		# A subsequent request by the user agent to the (same) server for a URL of
		# the form /acme/parts/ would include the following request header:
		# 
		# Cookie: $Version="1"; Part_Number="Rocket_Launcher_0001"; $Path="/acme"
		# 
		# Here, the second cookie's Path attribute /acme/ammo is not a prefix of
		# the request URL, /acme/parts/, so the cookie does not get forwarded to
		# the server.

		cookie = interact_2965(c, "http://www.acme.com/acme/parts/")
		assert (string.find(cookie, "Rocket_Launcher_0001") != -1 and
				not string.find(cookie, "Riding_Rocket_0023") != -1)

	def test_rejection(self):
		# Test rejection of Set-Cookie2 responses based on domain, path, port.
		from mechanoid.cookiejar.CookieJar import CookieJar

		c = CookieJar()

		max_age = "max-age=3600"

		# illegal domain (no embedded dots)
		cookie = interact_2965(c, "http://www.acme.com",
							   'foo=bar; domain=".com"; version=1')
		assert not c

		# legal domain
		cookie = interact_2965(c, "http://www.acme.com",
							   'ping=pong; domain="acme.com"; version=1')
		assert len(c) == 1

		# illegal domain (host prefix "www.a" contains a dot)
		cookie = interact_2965(c, "http://www.a.acme.com",
							   'whiz=bang; domain="acme.com"; version=1')
		assert len(c) == 1

		# legal domain
		cookie = interact_2965(c, "http://www.a.acme.com",
							   'wow=flutter; domain=".a.acme.com"; version=1')
		assert len(c) == 2

		# can't partially match an IP-address
		cookie = interact_2965(c, "http://125.125.125.125",
							   'zzzz=ping; domain="125.125.125"; version=1')
		assert len(c) == 2

		# illegal path (must be prefix of request path)
		cookie = interact_2965(c, "http://www.sol.no",
							   'blah=rhubarb; domain=".sol.no"; path="/foo"; '
							   'version=1')
		assert len(c) == 2

		# legal path
		cookie = interact_2965(c, "http://www.sol.no/foo/bar",
							   'bing=bong; domain=".sol.no"; path="/foo"; '
							   'version=1')
		assert len(c) == 3

		# illegal port (request-port not in list)
		cookie = interact_2965(c, "http://www.sol.no",
							   'whiz=ffft; domain=".sol.no"; port="90,100"; '
							   'version=1')
		assert len(c) == 3

		# legal port
		cookie = interact_2965(
			c, "http://www.sol.no",
			r'bang=wallop; version=1; domain=".sol.no"; '
			r'port="90,100, 80,8080"; '
			r'max-age=100; Comment = "Just kidding! (\"|\\\\) "')
		assert len(c) == 4

		# port attribute without any value (current port)
		cookie = interact_2965(c, "http://www.sol.no",
							   'foo9=bar; version=1; domain=".sol.no"; port; '
							   'max-age=100;')
		assert len(c) == 5

		# encoded path
		# LWP has this test, but unescaping allowed path characters seems
		# like a bad idea, so I think this should fail:
##		   cookie = interact_2965(c, "http://www.sol.no/foo/",
##							 r'foo8=bar; version=1; path="/%66oo"')
		# but this is OK, because '<' is not an allowed HTTP URL path
		# character:
		cookie = interact_2965(c, "http://www.sol.no/<oo/",
							   r'foo8=bar; version=1; path="/%3coo"')
		assert len(c) == 6

		# save and restore
		filename = "lwp-cookies.txt"

		try:
			c.save(filename, ignore_discard=True)
			old = repr(c)

			c = CookieJar()
			c.load(filename, ignore_discard=True)
		finally:
			try: os.unlink(filename)
			except OSError: pass

		assert old == repr(c)

	def test_url_encoding(self):
		# Try some URL encodings of the PATHs.
		# (the behaviour here has changed from libwww-perl)
		from mechanoid.cookiejar.CookieJar import CookieJar

		c = CookieJar()
##		   interact_2965(c, "http://www.acme.com/foo%2f%25/%40%40%0Anew%E5/%E5",
##					"foo  =	  bar; version	  =	  1")

##		   cookie = interact_2965(c, "http://www.acme.com/foo%2f%25/@@%0anewå/æøå",
##							 'bar=baz; path="/foo/"; version=1');
		interact_2965(c, "http://www.acme.com/foo%2f%25/%3c%3c%0Anew%E5/%E5",
					  "foo	=	bar; version	=	1")

		cookie = interact_2965(
			c, "http://www.acme.com/foo%2f%25/<<%0anewå/æøå",
			'bar=baz; path="/foo/"; version=1');
		version_re = re.compile(r'^\$version=\"?1\"?', re.I)
		assert (string.find(cookie, "foo=bar") != -1 and
				version_re.search(cookie))

##		   cookie = interact_2965(c, "http://www.acme.com/foo/%25/@@%0anewå/æøå")
		cookie = interact_2965(
			c, "http://www.acme.com/foo/%25/<<%0anewå/æøå")
		assert not cookie


	def test_netscape_misc(self):
		# Some additional Netscape cookies tests.
		from mechanoid.cookiejar.CookieJar import CookieJar
		from mechanoid.misc.Request import Request

		c = CookieJar()
		headers = []
		req = Request("http://foo.bar.acme.com/foo")

		# Netscape allows a host part that contains dots
		headers.append("Set-Cookie: Customer=WILE_E_COYOTE; domain=.acme.com")
		res = FakeResponse(headers, "http://www.acme.com/foo")
		c.extract_cookies(res, req)

		# and that the domain is the same as the host without adding a leading
		# dot to the domain.  Should not quote even if strange chars are used
		# in the cookie value.
		headers.append("Set-Cookie: PART_NUMBER=3,4; domain=foo.bar.acme.com")
		res = FakeResponse(headers, "http://www.acme.com/foo")
		c.extract_cookies(res, req)

		req = Request("http://foo.bar.acme.com/foo")
		c.add_cookie_header(req)
		assert (
			string.find(req.get_header("Cookie"), "PART_NUMBER=3,4") != -1 and
			string.find(req.get_header("Cookie"), "Customer=WILE_E_COYOTE") != -1)

	def test_intranet_domains(self):
		# Test handling of local intranet hostnames without a dot.
		from mechanoid.cookiejar.CookieJar import CookieJar

		c = CookieJar()
		interact_2965(c, "http://example/",
					  "foo1=bar; PORT; Discard; Version=1;")
		cookie = interact_2965(c, "http://example/",
							   'foo2=bar; domain=".local"; Version=1')
		assert not (string.find(cookie, "foo1=bar") == -1)

		interact_2965(c, "http://example/", 'foo3=bar; Version=1')
		cookie = interact_2965(c, "http://example/")
		assert not (string.find(cookie, "foo2=bar") == -1 or len(c) != 3)

	def test_empty_path(self):
		from mechanoid.cookiejar.CookieJar import CookieJar
		from mechanoid.misc.Request import Request

		# Test for empty path
		# Broken web-server ORION/1.3.38 returns to the client response like
		#
		#	Set-Cookie: JSESSIONID=ABCDERANDOM123; Path=
		#
		# ie. with Path set to nothing.
		# In this case, extract_cookies() must set cookie to / (root)
		c = CookieJar()
		headers = []

		req = Request("http://www.ants.com/")
		headers.append("Set-Cookie: JSESSIONID=ABCDERANDOM123; Path=")
		res = FakeResponse(headers, "http://www.ants.com/")
		c.extract_cookies(res, req)

		req = Request("http://www.ants.com/")
		c.add_cookie_header(req)

		assert (req.get_header("Cookie") == "JSESSIONID=ABCDERANDOM123" and
				req.get_header("Cookie2") == '$Version="1"')

		# missing path in the request URI
		req = Request("http://www.ants.com:8080")
		c.add_cookie_header(req)

		assert (req.get_header("Cookie") == "JSESSIONID=ABCDERANDOM123" and
				req.get_header("Cookie2") == '$Version="1"')


	def test_session_cookies(self):
		from mechanoid.cookiejar.CookieJar import CookieJar
		from mechanoid.misc.Request import Request

		year_plus_one = localtime(time.time())[0] + 1

		# Check session cookies are deleted properly by
		# CookieJar.clear_session_cookies method

		req = Request('http://www.perlmeister.com/scripts')
		headers = []
		headers.append("Set-Cookie: s1=session;Path=/scripts")
		headers.append("Set-Cookie: p1=perm; Domain=.perlmeister.com;"
					   "Path=/;expires=Fri, 02-Feb-%d 23:24:20 GMT" %
					   year_plus_one)
		headers.append("Set-Cookie: p2=perm;Path=/;expires=Fri, "
					   "02-Feb-%d 23:24:20 GMT" % year_plus_one)
		headers.append("Set-Cookie: s2=session;Path=/scripts;"
					   "Domain=.perlmeister.com")
		headers.append('Set-Cookie2: s3=session;Version=1;Discard;Path="/"')
		res = FakeResponse(headers, 'http://www.perlmeister.com/scripts')

		c = CookieJar()
		c.extract_cookies(res, req)
		# How many session/permanent cookies do we have?
		counter = {"session_after": 0,
				   "perm_after": 0,
				   "session_before": 0,
				   "perm_before": 0}
		for cookie in c:
			key = "%s_before" % cookie.value
			counter[key] = counter[key] + 1
		c.clear_session_cookies()
		# How many now?
		for cookie in c:
			key = "%s_after" % cookie.value
			counter[key] = counter[key] + 1

		assert not (
			# a permanent cookie got lost accidently
			counter["perm_after"] != counter["perm_before"] or
			# a session cookie hasn't been cleared
			counter["session_after"] != 0 or
			# we didn't have session cookies in the first place
			counter["session_before"] == 0)


if __name__ == "__main__":
	import unittest
	unittest.main()
