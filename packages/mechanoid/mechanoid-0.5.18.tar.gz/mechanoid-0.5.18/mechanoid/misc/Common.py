
# mechanoid.misc.Common.py::refactored from JJLee's original classes
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
# Copyright 2004 Richard Harris (mechanoid fork of mechanize - see README)
# Copyright 2002-2003 John J Lee <jjl@pobox.com>
# Copyright 1997-1999 Gisle Aas (original libwww-perl code)
#

import httplib, re, urlparse, string, urllib, types, time, os, pickle
import StringIO
from calendar import timegm
from Consts import IPV4_RE, MONTHS_LOWER
from exceptions import StopIteration

class Common:
	STRING_TYPES = types.StringType, types.UnicodeType
	SPACE_DICT = {}
	DEFAULT_HTTP_PORT = str(httplib.HTTP_PORT)
	HTTP_PATH_SAFE = "%/;:@&=+$,!~*'()"
	UTC_ZONES = {"GMT": None, "UTC": None, "UT": None, "Z": None}
	DEBUG = 0

	def __init__(self):
		self.token_re		 = re.compile(r"^\s*([^=\s;,]+)")
		self.quoted_value_re = re.compile(r"^\s*=\s*\"([^\"\\]*(?:\\.[^\"\\]*)*)\"")
		self.value_re		 = re.compile(r"^\s*=\s*([^\s;,]*)")
		self.escape_re		 = re.compile(r"\\(.)")
		self.timezone_re     = re.compile(r"^([-+])?(\d\d?):?(\d\d)?$")
		self.cut_port_re     = re.compile(r":\d+$")
		# Characters in addition to A-Z, a-z, 0-9, '_', '.', and '-' that don't
		# need to be escaped to form a valid HTTP URL (RFCs 2396 and 1738).
		self.escaped_char_re = re.compile(r"%([0-9a-fA-F][0-9a-fA-F])")
		for c in string.whitespace:
			self.SPACE_DICT[c] = None
		del c
		return

	#
	# Methods from original ClientCookie 
	#

	def is_HDN(self, text):
		"""
		Return True if text is a host domain name.

		"""
		# XXX This may well be wrong.  Which RFC is HDN defined in, if
		# any (for the purposes of RFC 2965)?  For the current
		# implementation, what about IPv6?  Remember to look at other
		# uses of IPV4_RE also, if you change this.
		if IPV4_RE.search(text):
			return False
		if text == "":
			return False
		if text[0] == "." or text[-1] == ".":
			return False
		return True

	def domain_match(self, A, B):
		"""
		Return True if domain A domain-matches domain B, according to RFC 2965.

		A and B may be host domain names or IP addresses.

		RFC 2965, section 1:

		Host names can be specified either as an IP address or a HDN string.
		Sometimes we compare one host name with another.  (Such comparisons SHALL
		be case-insensitive.)  Host A's name domain-matches host B's if

			 *  their host name strings string-compare equal; or

			 * A is a HDN string and has the form NB, where N is a non-empty
				name string, B has the form .B', and B' is a HDN string.  (So,
				x.y.com domain-matches .Y.com but not Y.com.)

		Note that domain-match is not a commutative operation: a.b.c.com
		domain-matches .c.com, but not the reverse.

		"""
		# Note that, if A or B are IP addresses, the only relevant part of the
		# definition of the domain-match algorithm is the direct string-compare.
		A = string.lower(A)
		B = string.lower(B)
		if A == B:
			return True
		if not self.is_HDN(A):
			return False
		i = string.rfind(A, B)
		if i == -1 or i == 0:
			# A does not have form NB, or N is the empty string
			return False
		if not self.startswith(B, "."):
			return False
		if not self.is_HDN(B[1:]):
			return False
		return True

	def liberal_is_HDN(self, text):
		"""
		Return True if text is a sort-of-like a host domain name.
		For accepting/blocking domains.

		"""
		if IPV4_RE.search(text):
			return False
		return True

	def user_domain_match(self, A, B):
		"""
		For blocking/accepting domains.
		A and B may be host domain names or IP addresses.

		"""
		A = string.lower(A)
		B = string.lower(B)
		if not (self.liberal_is_HDN(A) and self.liberal_is_HDN(B)):
			if A == B:
				# equal IP addresses
				return True
			return False
		initial_dot = self.startswith(B, ".")
		if initial_dot and self.endswith(A, B):
			return True
		if not initial_dot and A == B:
			return True
		return False

	def request_host(self, request):
		"""
		Return request-host, as defined by RFC 2965.
		Variation from RFC: returned value is lowercased,
		for convenient comparison.

		"""
		url = request.get_full_url()
		host = urlparse.urlparse(url)[1]
		if host == "":
			host = request.get_header("Host", "")
		# remove port, if present
		host = self.cut_port_re.sub("", host, 1)
		return string.lower(host)

	def eff_request_host(self, request):
		"""
		Return a tuple (request-host, effective request-host name).
		As defined by RFC 2965, except both are lowercased.

		"""
		erhn = req_host = self.request_host(request)
		if ((string.find(req_host, ".") == -1) and
			(not IPV4_RE.search(req_host))):
			erhn = req_host + ".local"
		return req_host, erhn

	def request_path(self, request):
		"""
		request-URI, as defined by RFC 2965.

		"""
		url = request.get_full_url()
		path, parameters, query, frag = urlparse.urlparse(url)[2:]
		if parameters:
			path = "%s;%s" % (path, parameters)
		path = self.escape_path(path)
		req_path = urlparse.urlunparse(("", "", path, "", query, frag))
		if not self.startswith(req_path, "/"):
			req_path = "/"+req_path  # fix bad RFC 2396 absoluteURI
		return req_path

	def request_port(self, request):
		"""
		Port of URL.  Defaults to 80.
		As of Python 2.3 request.port is always None, and is unused by urllib2
		
		"""
		port = self.DEFAULT_HTTP_PORT
		host = request.get_host()
		index = string.find(host, ':')
		if (index != -1):
			port = host[index+1:]
			try:
				int(port)
			except ValueError:
				if (self.DEBUG):
					print("mechanoid.Common.request_port::nonnumeric port: '%s'", port)
				return None
		return port

	def uppercase_escaped_char(self, match):
		return "%%%s" % string.upper(match.group(1))

	def escape_path(self, path):
		"""
		Escape any invalid characters in HTTP URL, and uppercase all escapes.

		There's no knowing what character encoding was used to create
		URLs containing %-escapes, but since we have to pick one to
		escape invalid path characters, we pick UTF-8, as recommended in
		the HTML 4.0 spec:

		http://www.w3.org/TR/REC-html40/appendix/notes.html#h-B.2.1

		And here, kind of: draft-fielding-uri-rfc2396bis-03
		(And in draft IRI specification: draft-duerst-iri-05)
		(And here, for new URI schemes: RFC 2718)

		"""
		if isinstance(path, types.UnicodeType):
			path = path.encode("utf-8")
		path = urllib.quote(path, self.HTTP_PATH_SAFE)
		path = self.escaped_char_re.sub(self.uppercase_escaped_char, path)
		return path

	def reach(self, h):
		"""
		Return reach of host h, as defined by RFC 2965, section 1.

		The reach R of a host name H is defined as follows:
		   *  If
			  -  H is the host domain name of a host; and,
			  -  H has the form A.B; and
			  -  A has no embedded (that is, interior) dots; and
			  -  B has at least one embedded dot, or B is the string "local".
				 then the reach of H is .B.
		   *  Otherwise, the reach of H is H.

		>>> reach("www.acme.com")
		'.acme.com'
		>>> reach("acme.com")
		'acme.com'
		>>> reach("acme.local")
		'.local'

		"""
		i = string.find(h, ".")
		if i >= 0:
			#a = h[:i]  # this line is only here to show what a is
			b = h[i+1:]
			i = string.find(b, ".")
			if self.is_HDN(h) and (i >= 0 or b == "local"):
				return "."+b
		return h

	def is_third_party(self, request):
		"""
		RFC 2965, section 3.3.6:

			An unverifiable transaction is to a third-party host if its request-
			host U does not domain-match the reach R of the request-host O in the
			origin transaction.

		"""
		req_host = string.lower(self.request_host(request))
		if not self.domain_match(req_host, self.reach(request.origin_req_host)):
			return True
		else:
			return False

	#
	# Methods from original Util class
	#

	def isstringlike(self, x):
		try:
			x = x + ""
		except: return False
		else: return True

	def startswith(self, string, initial):
		if len(initial) > len(string): return False
		return string[:len(initial)] == initial

	def endswith(self, string, final):
		if len(final) > len(string): return False
		return string[-len(final):] == final

	def __isspace(self, string):
		for c in string:
			if not self.SPACE_DICT.has_key(c): return False
		return True

	def getheaders(self, msg, name):
		"""
		Get all values for a header.

		This returns a list of values for headers given more than once; each
		value in the result list is stripped in the same way as the result of
		getheader().  If the header is not given, return an empty list.

		"""
		result = []
		current = ''
		have_header = 0
		for s in msg.getallmatchingheaders(name):
			if self.__isspace(s[0]):
				if current:
					current = "%s\n %s" % (current, string.strip(s))
				else:
					current = string.strip(s)
			else:
				if have_header:
					result.append(current)
				current = string.strip(s[string.find(s, ":") + 1:])
				have_header = 1
		if have_header:
			result.append(current)
		return result

	#
	# time methods
	#

	def my_timegm(self, tt):
		year, month, mday, hour, min, sec = tt[:6]
		if ((year >= 1970) and (1 <= month <= 12) and (1 <= mday <= 31) and
			(0 <= hour <= 24) and (0 <= min <= 59) and (0 <= sec <= 61)):
			return timegm(tt)
		else:
			return None

	def str2time(self, day, mon, yr, hr, min, sec, tz):
		# translate month name to number
		# month numbers start with 1 (January)
		try:
			mon = MONTHS_LOWER.index(string.lower(mon))+1
		except ValueError:
			# maybe it's already a number
			try:
				imon = int(mon)
			except ValueError:
				return None
			if 1 <= imon <= 12:
				mon = imon
			else:
				return None

		# make sure clock elements are defined
		if hr is None: hr = 0
		if min is None: min = 0
		if sec is None: sec = 0

		yr = int(yr)
		day = int(day)
		hr = int(hr)
		min = int(min)
		sec = int(sec)

		if yr < 1000:
			# find "obvious" year
			cur_yr = time.localtime(time.time())[0]
			m = cur_yr % 100
			tmp = yr
			yr = yr + cur_yr - m
			m = m - tmp
			if abs(m) > 50:
				if m > 0:
					yr = yr + 100
				else:
					yr = yr - 100

		# convert UTC time tuple to seconds since epoch (not timezone-adjusted)
		t = self.my_timegm((yr, mon, day, hr, min, sec, tz))

		# adjust time using timezone string, to get absolute time since epoch
		if t is not None:
			if tz is None:
				tz = "UTC"
			tz = string.upper(tz)
			offset = self.offset_from_tz_string(tz)
			if offset is None:
				return None
			t = t - offset
		return t

	def offset_from_tz_string(self, tz):
		offset = None
		if self.UTC_ZONES.has_key(tz):
			offset = 0
		else:
			m = self.timezone_re.search(tz)
			if m:
				offset = 3600 * int(m.group(2))
				if m.group(3):
					offset = offset + 60 * int(m.group(3))
				if m.group(1) == '-':
					offset = -offset
		return offset

	#
	# from original HeadersUtil class
	#
	
	def unmatched(self, match):
		"""
		Return unmatched part of re.Match object.

		"""
		start, end = match.span(0)
		return match.string[:start]+match.string[end:]
	
	def split_header_words(self, header_values):
		"""
		Parse header values into a list of lists containing key,value pairs.

		The function knows how to deal with ",", ";" and "=" as well as quoted
		values after "=".  A list of space separated tokens are parsed as if they
		were separated by ";".

		If the header_values passed as argument contains multiple values, then they
		are treated as if they were a single value separated by comma ",".

		This means that this function is useful for parsing header fields that
		follow this syntax (BNF as from the HTTP/1.1 specification, but we relax
		the requirement for tokens).

		  headers			= #header
		  header			= (token | parameter) *( [";"] (token | parameter))

		  token				= 1*<any CHAR except CTLs or separators>
		  separators		= "(" | ")" | "<" | ">" | "@"
							| "," | ";" | ":" | "\" | <">
							| "/" | "[" | "]" | "?" | "="
							| "{" | "}" | SP | HT

		  quoted-string		= ( <"> *(qdtext | quoted-pair ) <"> )
		  qdtext			= <any TEXT except <">>
		  quoted-pair		= "\" CHAR

		  parameter			= attribute "=" value
		  attribute			= token
		  value				= token | quoted-string

		Each header is represented by a list of key/value pairs.  The value for a
		simple token (not part of a parameter) is None.	 Syntactically incorrect
		headers will not necessarily be parsed as you would want.

		This is easier to describe with some examples:

		>>> import Header_Utils
		>>> h = Header_Utils.Header_Utils()
		>>> h.split_header_words(['foo="bar"; port="80,81"; discard, bar=baz'])
		[[('foo', 'bar'), ('port', '80,81'), ('discard', None)], [('bar', 'baz')]]
		>>> h.split_header_words(['text/html; charset="iso-8859-1"'])
		[[('text/html', None), ('charset', 'iso-8859-1')]]
		>>> h.split_header_words([r'Basic realm="\"foo\bar\""'])
		[[('Basic', None), ('realm', '"foobar"')]]

		"""
		assert type(header_values) not in self.STRING_TYPES
		result = []
		for text in header_values:
			orig_text = text
			pairs = []
			while text:
				m = self.token_re.search(text)
				if m:
					text = self.unmatched(m)
					name = m.group(1)
					m = self.quoted_value_re.search(text)
					if m:  # quoted value
						text = self.unmatched(m)
						value = m.group(1)
						value = self.escape_re.sub(r"\1", value)
					else:
						m = self.value_re.search(text)
						if m:  # unquoted value
							text = self.unmatched(m)
							value = m.group(1)
							value = string.rstrip(value)
						else:
							# no value, a lone token
							value = None
					pairs.append((name, value))
				elif self.startswith(string.lstrip(text), ","):
					# concatenated headers, as per RFC 2616 section 4.2
					text = string.lstrip(text)[1:]
					if pairs: result.append(pairs)
					pairs = []
				else:
					# skip junk
					non_junk, nr_junk_chars = re.subn("^[=\s;]*", "", text)
					assert nr_junk_chars > 0, (
						"split_header_words bug: '%s', '%s', %s" %
						(orig_text, text, pairs))
					text = non_junk
			if pairs: result.append(pairs)
		return result

	#
	# from lib_rharris
	#
	

	def find_line(self, lines, pattern):
		index = -1
		for line in lines:
			if (string.find(line, pattern) != -1):
				return lines.index(line)
		return index

	def form_only(self, file):
		FORM = ["form","input","textarea", "select", "option", "optgroup", "base", "isindex"]
		g = ""
		lines = file.readlines()
		for line in lines:
			tag = line.split(">")[0].lower()
			for tg in FORM:
				if (tag.find(tg) != -1):
					g = g + line
					break
		data = StringIO.StringIO(g)
		return data
	
	def get_args(self):
		self.params = []
		self.options = []
		add = 0
		args = sys.argv
		for i in range(1, len(args)):
			arg = args[i]
			if (string.find(arg,'--') == 0):
				if (string.find(arg,":") != -1):
					add = 1
					arg = string.replace(arg,":","")	
				self.options.append(string.replace(arg,'--',''))
			elif (string.find(arg,'-') == 0):
				for j in range(1,len(arg)):
					self.options.append(arg[j])
			elif (add):
				add = 0
				self.options.append(arg)
			elif (arg != ''):
				self.params.append(arg)
		if (self.DEBUG):
			print "Params: "+`self.params`
			print "Options: "+`self.options`
		return (self.params, self.options)

	def get_dict(self, fname):
		try:
			f = open(fname)
			dict = pickle.load(f)
			f.close()
		except:	
			dict = {}
		return dict

	def get_lines(self, file, remote=0):
		lines = []
		if not (remote):
			file = os.path.expandvars(file)
			file = os.path.expanduser(file)
			try:
				f = open(file)
				lines = f.readlines()
				f.close()
			except:
				pass
		else:
			try:
				f = urllib.urlopen(file)
				lines = f.readlines()
			except KeyboardInterrupt:
				self.exit()
			except SystemExit:
				pass
			except:
				self.retries = self.retries + 1
				if (self.retries <= self.RETRIES):
					lines = self.get_lines(file)
		self.retries = 0	
		return lines

	def html_canonical(self, file, lower=0):
		data = string.replace(file.read(),"\n"," ")
		g = ""
		tag = 0
		comment = 0
		for i in range(0, len(data)):
			if (i < comment):
				continue
			if data[i] == "<":
				if (data[i+1] == "!") and (data[i+2] not in ["d","D"]):
					comment = data[i+1:].index("-->")+ 2 + i
					continue
				else:	
					tag = 1
					g = g + "\n"
			elif data[i] == ">":
				tag = 0
			if (tag and lower):
				g = g + string.lower(data[i])
			else:
				g = g + data[i]
		data = StringIO.StringIO(g)
		return data

	def save_dict(self, fname, dict):
		f = open(fname,'w')
		pickle.dump(dict,f)
		f.close()
		return

	def strip_html(self, line):
		length = len(line)
		newln = []
		tag = 0
		i = 0
		while (i < length):
			if (line[i] == '<'):
				tag = 1
			if not (tag):
				newln.append(line[i])				
			if (line[i] == '>'):
				tag = 0
				newln.append(" ")
			i = i + 1
		newln = string.strip(string.join(newln,""))
		next = ""
		while (newln != next):
			next = newln
			newln = string.replace(newln,"	"," ")
		return newln

	def tokens(self, line, sep=" "):
		tokens = []
		line = string.strip(line)
		if (line != ""):
			tmp = string.split(line, sep)
			for entry in tmp:
				if (entry != ""):
					tokens.append(entry)
		return tokens

