
# cookiejar.DefaultCookiePolicy.py::refactored from JJLee's ClientCookie
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

import string, time
from CookiePolicy import CookiePolicy
from mechanoid.misc.Consts import IPV4_RE
from mechanoid.misc.Common import Common

class DefaultCookiePolicy(CookiePolicy):
	"""Implements the standard rules for accepting and returning cookies.

	Both RFC 2965 and Netscape cookies are covered.

	The easiest way to provide your own policy is to override this class and
	call its methods in your overriden implementations before adding your own
	additional checks.

	import ClientCookie
	class MyCookiePolicy(ClientCookie.DefaultCookiePolicy):
		def set_ok(self, cookie, request, unverifiable):
			if not ClientCookie.DefaultCookiePolicy.set_ok(
				self, cookie, request, unverifiable):
				return False
			if i_dont_want_to_store_this_cookie():
				return False
			return True

	In addition to the features required to implement the CookiePolicy
	interface, this class allows you to block and allow domains from setting
	and receiving cookies.	There are also some strictness switches that allow
	you to tighten up the rather loose Netscape protocol rules a little bit (at
	the cost of blocking some benign cookies).

	A domain blacklist and whitelist is provided (both off by default).	 Only
	domains not in the blacklist and present in the whitelist (if the whitelist
	is active) participate in cookie setting and returning.	 Use the
	blocked_domains constructor argument, and blocked_domains and
	set_blocked_domains methods (and the corresponding argument and methods for
	allowed_domains).  If you set a whitelist, you can turn it off again by
	setting it to None.

	Domains in block or allow lists that do not start with a dot must
	string-compare equal.  For example, "acme.com" matches a blacklist entry of
	"acme.com", but "www.acme.com" does not.  Domains that do start with a dot
	are matched by more specific domains too.  For example, both "www.acme.com"
	and "www.munitions.acme.com" match ".acme.com" (but "acme.com" itself does
	not).  IP addresses are an exception, and must match exactly.  For example,
	if blocked_domains contains "192.168.1.2" and ".168.1.2" 192.168.1.2 is
	blocked, but 193.168.1.2 is not.

	Additional Public Attributes:

	General strictness switches

	strict_domain: don't allow sites to set two-component domains with
	 country-code top-level domains like .co.uk, .gov.uk, .co.nz. etc.
	 This is far from perfect and isn't guaranteed to work!

	RFC 2965 protocol strictness switches

	strict_rfc2965_unverifiable: follow RFC 2965 rules on unverifiable
	 transactions (usually, an unverifiable transaction is one resulting from
	 a redirect or an image hosted on another site); if this is false, cookies
	 are NEVER blocked on the basis of verifiability

	Netscape protocol strictness switches

	strict_ns_unverifiable: apply RFC 2965 rules on unverifiable transactions
	 even to Netscape cookies
	strict_ns_domain: flags indicating how strict to be with domain-matching
	 rules for Netscape cookies:
	  DomainStrictNoDots: when setting cookies, host prefix must not contain a
	   dot (eg. www.foo.bar.com can't set a cookie for .bar.com, because
	   www.foo contains a dot)
	  DomainStrictNonDomain: cookies that did not explicitly specify a Domain
	   cookie-attribute can only be returned to a domain that string-compares
	   equal to the domain that set the cookie (eg. rockets.acme.com won't
	   be returned cookies from acme.com that had no Domain cookie-attribute)
	  DomainRFC2965Match: when setting cookies, require a full RFC 2965
	   domain-match
	  DomainLiberal and DomainStrict are the most useful combinations of the
	   above flags, for convenience
	strict_ns_set_initial_dollar: ignore cookies in Set-Cookie: headers that
	 have names starting with '$'
	strict_ns_set_path: don't allow setting cookies whose path doesn't
	 path-match request URI

	"""
	DEBUG = 0
	DomainStrictNoDots = 1
	DomainStrictNonDomain = 2
	DomainRFC2965Match = 4

	DomainLiberal = 0
	DomainStrict = DomainStrictNoDots|DomainStrictNonDomain

	def __init__(self,
				 blocked_domains=None, allowed_domains=None,
				 netscape=True, rfc2965=True,
				 hide_cookie2=False,
				 strict_domain=False,
				 strict_rfc2965_unverifiable=True,
				 strict_ns_unverifiable=False,
				 strict_ns_domain=DomainLiberal,
				 strict_ns_set_initial_dollar=False,
				 strict_ns_set_path=False):
		"""
		blocked_domains: sequence of domain names that we never accept cookies
		 from, nor return cookies to
		allowed_domains: if not None, this is a sequence of the only domains
		 for which we accept and return cookies

		For other arguments, see CookiePolicy.__doc__ and
		DefaultCookiePolicy.__doc__..

		"""
		self.netscape = netscape
		self.rfc2965 = rfc2965
		self.hide_cookie2 = hide_cookie2
		self.strict_domain = strict_domain
		self.strict_rfc2965_unverifiable = strict_rfc2965_unverifiable
		self.strict_ns_unverifiable = strict_ns_unverifiable
		self.strict_ns_domain = strict_ns_domain
		self.strict_ns_set_initial_dollar = strict_ns_set_initial_dollar
		self.strict_ns_set_path = strict_ns_set_path

		if blocked_domains is not None:
			self._blocked_domains = tuple(blocked_domains)
		else:
			self._blocked_domains = ()

		if allowed_domains is not None:
			allowed_domains = tuple(allowed_domains)
		self._allowed_domains = allowed_domains
		self._now = int(time.time())
		self.common = Common()
		
	def blocked_domains(self):
		"""Return the sequence of blocked domains (as a tuple)."""
		return self._blocked_domains
	def set_blocked_domains(self, blocked_domains):
		"""Set the sequence of blocked domains."""
		self._blocked_domains = tuple(blocked_domains)

	def is_blocked(self, domain):
		for blocked_domain in self._blocked_domains:
			if self.common.user_domain_match(domain, blocked_domain):
				return True
		return False

	def allowed_domains(self):
		"""Return None, or the sequence of allowed domains (as a tuple)."""
		return self._allowed_domains
	def set_allowed_domains(self, allowed_domains):
		"""Set the sequence of allowed domains, or None."""
		if allowed_domains is not None:
			allowed_domains = tuple(allowed_domains)
		self._allowed_domains = allowed_domains

	def is_not_allowed(self, domain):
		if self._allowed_domains is None:
			return False
		for allowed_domain in self._allowed_domains:
			if self.common.user_domain_match(domain, allowed_domain):
				return False
		return True

	def set_ok(self, cookie, request, unverifiable):
		"""
		If you override set_ok, be sure to call this method.  If it returns
		false, so should your subclass (assuming your subclass wants to be more
		strict about which cookies to accept).

		"""
		if (self.DEBUG):
			print(" - checking cookie %s=%s", cookie.name, cookie.value)

		assert cookie.value is not None

		for n in "version", "verifiability", "name", "path", "domain", "port":
			fn_name = "set_ok_"+n
			fn = getattr(self, fn_name)
			if not fn(cookie, request, unverifiable):
				return False
		return True

	def set_ok_version(self, cookie, request, unverifiable):
		if cookie.version is None:
			# Version is always set to 0 by parse_ns_headers if it's a Netscape
			# cookie, so this must be an invalid RFC 2965 cookie.
			if (self.DEBUG):
				print("	  Set-Cookie2 without version attribute (%s=%s)",
					  cookie.name, cookie.value)
			return False
		if cookie.version > 0 and not self.rfc2965:
			if (self.DEBUG):
				print("	  RFC 2965 cookies are switched off")
			return False
		elif cookie.version == 0 and not self.netscape:
			if (self.DEBUG):
				print("	  Netscape cookies are switched off")
			return False
		return True

	def set_ok_verifiability(self, cookie, request, unverifiable):
		if unverifiable and self.common.is_third_party(request):
			if cookie.version > 0 and self.strict_rfc2965_unverifiable:
				if (self.DEBUG):
					print("	  third-party RFC 2965 cookie during "
							 "unverifiable transaction")
				return False
			elif cookie.version == 0 and self.strict_ns_unverifiable:
				if (self.DEBUG):
					print("	  third-party Netscape cookie during "
						  "unverifiable transaction")
				return False
		return True

	def set_ok_name(self, cookie, request, unverifiable):
		# Try and stop servers setting V0 cookies designed to hack other
		# servers that know both V0 and V1 protocols.
		if (cookie.version == 0 and self.strict_ns_set_initial_dollar and
			(cookie.name is not None) and self.common.startswith(cookie.name, "$")):
			if (self.DEBUG):
				print("	  illegal name (starts with '$'): '%s'", cookie.name)
			return False
		return True

	def set_ok_path(self, cookie, request, unverifiable):
		if cookie.path_specified:
			req_path = self.common.request_path(request)
			if ((cookie.version > 0 or
				 (cookie.version == 0 and self.strict_ns_set_path)) and
				not self.common.startswith(req_path, cookie.path)):
				if (self.DEBUG):
					print("	  path attribute %s is not a prefix of request "
						  "path %s", cookie.path, req_path)
				return False
		return True

	def set_ok_domain(self, cookie, request, unverifiable):
		if self.is_blocked(cookie.domain):
			if (self.DEBUG):
				print("	  domain %s is in user block-list", cookie.domain)
			return False
		if self.is_not_allowed(cookie.domain):
			if (self.DEBUG):
				print("	  domain %s is not in user allow-list", cookie.domain)
			return False
		if cookie.domain_specified:
			req_host, erhn = self.common.eff_request_host(request)
			domain = cookie.domain
			if self.strict_domain and (string.count(domain, ".") >= 2):
				i = string.rfind(domain, ".")
				j = string.rfind(domain, ".", 0, i)
				if j == 0:	# domain like .foo.bar
					tld = domain[i+1:]
					sld = domain[j+1:i]
					if (string.lower(sld) in [
						"co", "ac",
						"com", "edu", "org", "net", "gov", "mil", "int"] and
						len(tld) == 2):
						# domain like .co.uk
						if (self.DEBUG):
							print("	  country-code second level domain %s", domain)
						return False
			if self.common.startswith(domain, "."):
				undotted_domain = domain[1:]
			else:
				undotted_domain = domain
			embedded_dots = (string.find(undotted_domain, ".") >= 0)
			if not embedded_dots and domain != ".local":
				if (self.DEBUG):
					print("	  non-local domain %s contains no embedded dot", domain)
				return False
			if cookie.version == 0:
				if (not self.common.endswith(erhn, domain) and
					(not self.common.startswith(erhn, ".") and
					 not self.common.endswith("."+erhn, domain))):
					if (self.DEBUG):
						print("	  effective request-host %s (even with added "
							  "initial dot) does not end end with %s",
							  erhn, domain)
					return False
			if (cookie.version > 0 or
				(self.strict_ns_domain & self.DomainRFC2965Match)):
				if not self.common.domain_match(erhn, domain):
					if (self.DEBUG):
						print("	  effective request-host %s does not domain-match "
							  "%s", erhn, domain)
					return False
			if (cookie.version > 0 or
				(self.strict_ns_domain & self.DomainStrictNoDots)):
				host_prefix = req_host[:-len(domain)]
				if (string.find(host_prefix, ".") >= 0 and
					not IPV4_RE.search(req_host)):
					if (self.DEBUG):
						print("	  host prefix %s for domain %s contains a dot",
							  host_prefix, domain)
					return False
		return True

	def set_ok_port(self, cookie, request, unverifiable):
		if cookie.port_specified:
			req_port = self.common.request_port(request)
			if req_port is None:
				req_port = "80"
			else:
				req_port = str(req_port)
			for p in string.split(cookie.port, ","):
				try:
					int(p)
				except ValueError:
					if (self.DEBUG):
						print("	  bad port %s (not numeric)", p)
					return False
				if p == req_port:
					break
			else:
				if (self.DEBUG):
					print("	  request port (%s) not found in %s",
						  req_port, cookie.port)
				return False
		return True

	def return_ok(self, cookie, request, unverifiable):
		"""
		If you override return_ok, be sure to call this method.	 If it returns
		false, so should your subclass.

		"""
		# Path has already been checked by path_return_ok, and domain blocking
		# done by domain_return_ok.
		if (self.DEBUG):
			print(" - checking cookie %s=%s", cookie.name, cookie.value)

		for n in "version", "verifiability", "secure", "expires", "port", "domain":
			fn_name = "return_ok_"+n
			fn = getattr(self, fn_name)
			if not fn(cookie, request, unverifiable):
				return False
		return True

	def return_ok_version(self, cookie, request, unverifiable):
		if cookie.version > 0 and not self.rfc2965:
			if (self.DEBUG):
				print("	  RFC 2965 cookies are switched off")
			return False
		elif cookie.version == 0 and not self.netscape:
			if (self.DEBUG):
				print("	  Netscape cookies are switched off")
			return False
		return True

	def return_ok_verifiability(self, cookie, request, unverifiable):
		if unverifiable and self.common.is_third_party(request):
			if cookie.version > 0 and self.strict_rfc2965_unverifiable:
				if (self.DEBUG):
					print("	  third-party RFC 2965 cookie during unverifiable "
						  "transaction")
				return False
			elif cookie.version == 0 and self.strict_ns_unverifiable:
				if (self.DEBUG):
					print("	  third-party Netscape cookie during unverifiable "
						  "transaction")
				return False
		return True

	def return_ok_secure(self, cookie, request, unverifiable):
		if cookie.secure and request.get_type() != "https":
			if (self.DEBUG):
				print("	  secure cookie with non-secure request")
			return False
		return True

	def return_ok_expires(self, cookie, request, unverifiable):
		if cookie.is_expired(self._now):
			if (self.DEBUG):
				print("	  cookie expired")
			return False
		return True

	def return_ok_port(self, cookie, request, unverifiable):
		if cookie.port:
			req_port = self.common.request_port(request)
			if req_port is None:
				req_port = "80"
			for p in string.split(cookie.port, ","):
				if p == req_port:
					break
			else:
				if (self.DEBUG):
					print("	  request port %s does not match cookie port %s",
						  req_port, cookie.port)
				return False
		return True

	def return_ok_domain(self, cookie, request, unverifiable):
		req_host, erhn = self.common.eff_request_host(request)
		domain = cookie.domain

		# strict check of non-domain cookies: Mozilla does this, MSIE5 doesn't
		if (cookie.version == 0 and
			(self.strict_ns_domain & self.DomainStrictNonDomain) and
			not cookie.domain_specified and domain != erhn):
			if (self.DEBUG):
				print("	  cookie with unspecified domain does not string-compare "
					  "equal to request domain")
			return False

		if cookie.version > 0 and not self.common.domain_match(erhn, domain):
			if (self.DEBUG):
				print("	  effective request-host name %s does not domain-match "
					  "RFC 2965 cookie domain %s", erhn, domain)
			return False
		if cookie.version == 0 and not self.common.endswith("."+req_host, domain):
			if (self.DEBUG):
				print("	  request-host %s does not match Netscape cookie domain "
					  "%s", req_host, domain)
			return False
		return True

	def domain_return_ok(self, domain, request, unverifiable):
		if self.is_blocked(domain):
			if (self.DEBUG):
				print("	  domain %s is in user block-list", domain)
			return False
		if self.is_not_allowed(domain):
			if (self.DEBUG):
				print("	  domain %s is not in user allow-list", domain)
			return False
		return True

	def path_return_ok(self, path, request, unverifiable):
		if (self.DEBUG):
			print("- checking cookie path=%s", path)
		req_path = self.common.request_path(request)
		if not self.common.startswith(req_path, path):
			if (self.DEBUG):
				print("	 %s does not path-match %s", req_path, path)
			return False
		return True


