"""Tests for ClientCookie._HTTPDate."""

import re, string, time
from unittest import TestCase
from mechanoid.misc.Common import Common
common = Common()
from mechanoid.cookiejar.Header_Utils import Header_Utils
utils = Header_Utils()
from mechanoid.cookiejar.CookieJar import CookieJar
jar = CookieJar()

class DateTimeTests(TestCase):

    def test_time2isoz(self):
        base = 1019227000
        day = 24*3600
        assert jar.time2isoz(base) == "2002-04-19 14:36:40Z"
        assert jar.time2isoz(base+day) == "2002-04-20 14:36:40Z"
        assert jar.time2isoz(base+2*day) == "2002-04-21 14:36:40Z"
        assert jar.time2isoz(base+3*day) == "2002-04-22 14:36:40Z"

        az = jar.time2isoz()
        bz = jar.time2isoz(500000)
        for text in (az, bz):
            assert re.search(r"^\d{4}-\d\d-\d\d \d\d:\d\d:\d\dZ$", text), \
                   "bad time2isoz format: %s %s" % (az, bz)

    def test_parse_date(self):

        def parse_date(text):
            return time.gmtime(utils.http2time(text))[:6]

        assert parse_date("01 Jan 2001") == (2001, 1, 1, 0, 0, 0.0)

        # this test will break around year 2070
        assert parse_date("03-Feb-20") == (2020, 2, 3, 0, 0, 0.0)

        # this test will break around year 2048
        assert parse_date("03-Feb-98") == (1998, 2, 3, 0, 0, 0.0)

    def test_http2time_formats(self):
        # test http2time for supported dates.  Test cases with 2 digit year
        # will probably break in year 2044.
        tests = [
         'Thu, 03 Feb 1994 00:00:00 GMT',  # proposed new HTTP format
         'Thursday, 03-Feb-94 00:00:00 GMT',  # old rfc850 HTTP format
         'Thursday, 03-Feb-1994 00:00:00 GMT',  # broken rfc850 HTTP format

         '03 Feb 1994 00:00:00 GMT',  # HTTP format (no weekday)
         '03-Feb-94 00:00:00 GMT',  # old rfc850 (no weekday)
         '03-Feb-1994 00:00:00 GMT',  # broken rfc850 (no weekday)
         '03-Feb-1994 00:00 GMT',  # broken rfc850 (no weekday, no seconds)
         '03-Feb-1994 00:00',  # broken rfc850 (no weekday, no seconds, no tz)

         '03-Feb-94',  # old rfc850 HTTP format (no weekday, no time)
         '03-Feb-1994',  # broken rfc850 HTTP format (no weekday, no time)
         '03 Feb 1994',  # proposed new HTTP format (no weekday, no time)

         # A few tests with extra space at various places
         '  03   Feb   1994  0:00  ',
         '  03-Feb-1994  ',
        ]

        test_t = 760233600  # assume broken POSIX counting of seconds
        result = jar.time2isoz(test_t)
        expected = "1994-02-03 00:00:00Z"
        assert result == expected, \
               "%s  =>  '%s' (%s)" % (test_t, result, expected)

        for s in tests:
            t = utils.http2time(s)
            t2 = utils.http2time(string.lower(s))
            t3 = utils.http2time(string.upper(s))

            assert t == t2 == t3 == test_t, \
                   "'%s'  =>  %s, %s, %s (%s)" % (s, t, t2, t3, test_t)

    def test_http2time_garbage(self):

        for test in [
            '', 'Garbage',
            'Mandag 16. September 1996',

            '01-00-1980',
            '01-13-1980',
            '00-01-1980',
            '32-01-1980',
            '01-01-1980 25:00:00',
            '01-01-1980 00:61:00',
            '01-01-1980 00:00:62']:

            bad = False

            if utils.http2time(test) is not None:
                print "http2time(%s) is not None" % (test,)
                print "http2time(test)", utils.http2time(test)
                bad = True

            assert not bad


if __name__ == "__main__":
    import unittest
    unittest.main()
