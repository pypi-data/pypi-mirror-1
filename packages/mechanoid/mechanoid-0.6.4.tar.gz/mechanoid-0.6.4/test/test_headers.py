"""Tests for ClientCookie._HeadersUtil."""

from unittest import TestCase

class HeaderTests(TestCase):
	def test_parse_ns_headers(self):
		from mechanoid.cookiejar.Header_Utils import Header_Utils
		h = Header_Utils()

		# quotes should be stripped
		assert h.parse_ns_headers(['expires=01 Jan 2040 22:23:32 GMT']) == \
			   [[('expires', 2209069412L), ('version', '0')]]
		assert h.parse_ns_headers(['expires="01 Jan 2040 22:23:32 GMT"']) == \
			   [[('expires', 2209069412L), ('version', '0')]]

	def test_join_header_words(self):
		from mechanoid.cookiejar.Header_Utils import Header_Utils
		h = Header_Utils()
		
		assert h.join_header_words([[
			("foo", None), ("bar", "baz"), (None, "value")
			]]) == "foo; bar=baz; value"

		assert h.join_header_words([[]]) == ""

	def test_split_header_words(self):
		from mechanoid.cookiejar.Header_Utils import Header_Utils
		h = Header_Utils()

		tests = [
			("foo", [[("foo", None)]]),
			("foo=bar", [[("foo", "bar")]]),
			("	 foo   ", [[("foo", None)]]),
			("	 foo=	", [[("foo", "")]]),
			("	 foo=", [[("foo", "")]]),
			("	 foo=	; ", [[("foo", "")]]),
			("	 foo=	; bar= baz ", [[("foo", ""), ("bar", "baz")]]),
			("foo=bar bar=baz", [[("foo", "bar"), ("bar", "baz")]]),
			# doesn't really matter if this next fails, but it works ATM
			("foo= bar=baz", [[("foo", "bar=baz")]]),
			("foo=bar;bar=baz", [[("foo", "bar"), ("bar", "baz")]]),
			('foo bar baz', [[("foo", None), ("bar", None), ("baz", None)]]),
			("a, b, c", [[("a", None)], [("b", None)], [("c", None)]]),
			(r'foo; bar=baz, spam=, foo="\,\;\"", bar= ',
			 [[("foo", None), ("bar", "baz")],
			  [("spam", "")], [("foo", ',;"')], [("bar", "")]]),
			]

		for arg, expect in tests:
			try:
				result = h.split_header_words([arg])
			except:
				import traceback, StringIO
				f = StringIO.StringIO()
				traceback.print_exc(None, f)
				result = "(error -- traceback follows)\n\n%s" % f.getvalue()
			assert result == expect, """
When parsing: '%s'
Expected:	  '%s'
Got:		  '%s'
""" % (arg, expect, result)

	def test_roundtrip(self):
		from mechanoid.cookiejar.Header_Utils import Header_Utils
		h = Header_Utils()

		tests = [
			("foo", "foo"),
			("foo=bar", "foo=bar"),
			("	 foo   ", "foo"),
			("foo=", 'foo=""'),
			("foo=bar bar=baz", "foo=bar; bar=baz"),
			("foo=bar;bar=baz", "foo=bar; bar=baz"),
			('foo bar baz', "foo; bar; baz"),
			(r'foo="\"" bar="\\"', r'foo="\""; bar="\\"'),
			('foo,,,bar', 'foo, bar'),
			('foo=bar,bar=baz', 'foo=bar, bar=baz'),

			('text/html; charset=iso-8859-1',
			 'text/html; charset="iso-8859-1"'),

			('foo="bar"; port="80,81"; discard, bar=baz',
			 'foo=bar; port="80,81"; discard, bar=baz'),

			(r'Basic realm="\"foo\\\\bar\""',
			 r'Basic; realm="\"foo\\\\bar\""')
			]

		for arg, expect in tests:
			input = h.split_header_words([arg])
			res = h.join_header_words(input)
			assert res == expect, """
When parsing: '%s'
Expected:	  '%s'
Got:		  '%s'
Input was:	  '%s'""" % (arg, expect, res, input)


if __name__ == "__main__":
	import unittest
	unittest.main()
