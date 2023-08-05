#!/usr/bin/env python

from __future__ import generators

import sys
from unittest import TestCase

try:
    enumerate
except NameError:
    def enumerate(it):
        i = 0
        while 1:
            v = it.next()
            yield i, v
            i += 1

def peek_token(p):
    tok = p._PullParser__get_token()
    p._PullParser__unget_token(tok)
    return tok

class PullParserTests(TestCase):
    def data_and_file(self):
        from StringIO import StringIO
        data = """<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN"
"http://www.w3.org/TR/html4/strict.dtd">
<html>
<head>
<title an=attr>Title</title>
</head>
<body>
<p>This is a data <img alt="blah"> &amp; that was an entityref and this &#097; is
a charref.  <blah foo="bing" blam="wallop">.
<!-- comment blah blah
still a comment , blah and a space at the end 
-->
<!rheum>
<?rhaponicum>
<randomtag spam="eggs"/>
</body>
</html>
"""
        f = StringIO(data)
        return data, f

    def test_encoding(self):
        from mechanoid.pullparser.PullParser import PullParser
        from StringIO import StringIO
        data = "<a>&#1092;</a>"

        f = StringIO(data)
        p = PullParser(f, encoding="KOI8-R")
        p.get_tag("a")
        self.assert_(p.get_text() == "\xc6")

        f = StringIO(data)
        p = PullParser(f, encoding="UTF-8")
        p.get_tag("a")
        self.assert_(p.get_text() == "\xd1\x84")

    def test_get_token(self):
        from mechanoid.pullparser.PullParser import PullParser
        from mechanoid.misc.Errors import NoMoreTokensError

        data, f = self.data_and_file()
        p = PullParser(f)
        self.assert_(
            p._PullParser__get_token() == ("decl",
'''DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN"
"http://www.w3.org/TR/html4/strict.dtd"''', None))
        self.assert_(p._PullParser__get_token() == ("data", "\n", None))
        self.assert_(p._PullParser__get_token() == ("starttag", "html", []))
        self.assert_(p._PullParser__get_token() == ("data", "\n", None))
        self.assert_(p._PullParser__get_token() == ("starttag", "head", []))
        self.assert_(p._PullParser__get_token() == ("data", "\n", None))
        self.assert_(p._PullParser__get_token() == ("starttag", "title", [("an", "attr")]))
        self.assert_(p._PullParser__get_token() == ("data", "Title", None))
        self.assert_(p._PullParser__get_token() == ("endtag", "title", None))
        self.assert_(p._PullParser__get_token() == ("data", "\n", None))
        self.assert_(p._PullParser__get_token() == ("endtag", "head", None))
        self.assert_(p._PullParser__get_token() == ("data", "\n", None))
        self.assert_(p._PullParser__get_token() == ("starttag", "body", []))
        self.assert_(p._PullParser__get_token() == ("data", "\n", None))
        self.assert_(p._PullParser__get_token() == ("starttag", "p", []))
        self.assert_(p._PullParser__get_token() == ("data", "This is a data ", None))
        self.assert_(p._PullParser__get_token() == ("starttag", "img", [("alt", "blah")]))
        self.assert_(p._PullParser__get_token() == ("data", " ", None))
        self.assert_(p._PullParser__get_token() == ("entityref", "amp", None))
        self.assert_(p._PullParser__get_token() == ("data",
                                       " that was an entityref and this ",
                                       None))
        self.assert_(p._PullParser__get_token() == ("charref", "097", None))
        self.assert_(p._PullParser__get_token() == ("data", " is\na charref.  ", None))
        self.assert_(p._PullParser__get_token() == ("starttag", "blah",
                                       [("foo", "bing"), ("blam", "wallop")]))
        self.assert_(p._PullParser__get_token() == ("data", ".\n", None))
        self.assert_(p._PullParser__get_token() == (
            "comment", " comment blah blah\n"
            "still a comment , blah and a space at the end \n", None))
        self.assert_(p._PullParser__get_token() == ("data", "\n", None))
        self.assert_(p._PullParser__get_token() == ("decl", "rheum", None))
        self.assert_(p._PullParser__get_token() == ("data", "\n", None))
        self.assert_(p._PullParser__get_token() == ("pi", "rhaponicum", None))
        self.assert_(p._PullParser__get_token() == ("data", "\n", None))
        self.assert_(p._PullParser__get_token() == ("startendtag", "randomtag",
                                       [("spam", "eggs")]))
        self.assert_(p._PullParser__get_token() == ("data", "\n", None))
        self.assert_(p._PullParser__get_token() == ("endtag", "body", None))
        self.assert_(p._PullParser__get_token() == ("data", "\n", None))
        self.assert_(p._PullParser__get_token() == ("endtag", "html", None))
        self.assert_(p._PullParser__get_token() == ("data", "\n", None))
        self.assertRaises(NoMoreTokensError, p._PullParser__get_token)

    def test_unget_token(self):
        from mechanoid.pullparser.PullParser import PullParser
        from mechanoid.misc.Errors import NoMoreTokensError
        data, f = self.data_and_file()
        p = PullParser(f)
        p._PullParser__get_token()
        tok = p._PullParser__get_token()
        self.assert_(tok == ("data", "\n", None))
        p._PullParser__unget_token(tok)
        self.assert_(p._PullParser__get_token() == ("data", "\n", None))
        tok = p._PullParser__get_token()
        self.assert_(tok == ("starttag", "html", []))
        p._PullParser__unget_token(tok)
        self.assert_(tok == ("starttag", "html", []))

    def test_get_tag(self):
        from mechanoid.pullparser.PullParser import PullParser
        from mechanoid.misc.Errors import NoMoreTokensError
        data, f = self.data_and_file()
        p = PullParser(f)
        self.assert_(p.get_tag() == ("starttag", "html", []))
        self.assert_(p.get_tag("blah", "body", "title") ==
                     ("starttag", "title", [("an", "attr")]))
        self.assert_(p.get_tag() == ("endtag", "title", None))
        self.assert_(p.get_tag("randomtag") == ("startendtag", "randomtag",
                                                [("spam", "eggs")]))
        self.assert_(p.get_tag() == ("endtag", "body", None))
        self.assert_(p.get_tag() == ("endtag", "html", None))
        self.assertRaises(NoMoreTokensError, p.get_tag)
#        print "tag", p.get_tag()
#        sys.exit()

    def test_get_text(self):
        from mechanoid.pullparser.PullParser import PullParser
        from mechanoid.misc.Errors import NoMoreTokensError

        data, f = self.data_and_file()
        p = PullParser(f)
        self.assert_(p.get_text() == "\n")
        self.assert_(peek_token(p).data == "html")
        self.assert_(p.get_text() == "")
        self.assert_(peek_token(p).data == "html"); p._PullParser__get_token()
        self.assert_(p.get_text() == "\n"); p._PullParser__get_token()
        self.assert_(p.get_text() == "\n"); p._PullParser__get_token()
        self.assert_(p.get_text() == "Title"); p._PullParser__get_token()
        self.assert_(p.get_text() == "\n"); p._PullParser__get_token()
        self.assert_(p.get_text() == "\n"); p._PullParser__get_token()
        self.assert_(p.get_text() == "\n"); p._PullParser__get_token()
        self.assert_(p.get_text() == "This is a data blah[IMG]"); p._PullParser__get_token()
        self.assert_(p.get_text() == " & that was an entityref "
                     "and this a is\na charref.  "); p._PullParser__get_token()
        self.assert_(p.get_text() == ".\n\n\n\n"); p._PullParser__get_token()
        self.assert_(p.get_text() == "\n"); p._PullParser__get_token()
        self.assert_(p.get_text() == "\n"); p._PullParser__get_token()
        self.assert_(p.get_text() == "\n"); p._PullParser__get_token()
        # no more tokens, so we just get empty string
        self.assert_(p.get_text() == "")
        self.assert_(p.get_text() == "")
        self.assertRaises(NoMoreTokensError, p._PullParser__get_token)
        #print "text", `p.get_text()`
        #sys.exit()

    def test_get_text_2(self):
        # more complicated stuff

        from mechanoid.pullparser.PullParser import PullParser
        from mechanoid.misc.Errors import NoMoreTokensError

        # endat
        data, f = self.data_and_file()
        p = PullParser(f)
        self.assert_(p.get_text(endat=("endtag", "html")) ==
                     u"\n\n\nTitle\n\n\nThis is a data blah[IMG]"
                     " & that was an entityref and this a is\na charref.  ."
                     "\n\n\n\n\n\n")
        f.close()

        data, f = self.data_and_file()
        p = PullParser(f)
        self.assert_(p.get_text(endat=("endtag", "title")) ==
                     "\n\n\nTitle")
        self.assert_(p.get_text(endat=("starttag", "img")) ==
                     "\n\n\nThis is a data blah[IMG]")
        f.close()

        # textify arg
        data, f = self.data_and_file()
        p = PullParser(f, textify={"title": "an", "img": lambda x: "YYY"})
        self.assert_(p.get_text(endat=("endtag", "title")) ==
                     "\n\n\nattr[TITLE]Title")
        self.assert_(p.get_text(endat=("starttag", "img")) ==
                     "\n\n\nThis is a data YYY")
        f.close()

        # get_compressed_text
        data, f = self.data_and_file()
        p = PullParser(f)
        self.assert_(p.get_compressed_text(endat=("endtag", "html")) ==
                     u"Title This is a data blah[IMG]"
                     " & that was an entityref and this a is a charref. .")
        f.close()

    def test_tags(self):
        from mechanoid.pullparser.PullParser import PullParser
        from mechanoid.misc.Errors import NoMoreTokensError

        # no args
        data, f = self.data_and_file()
        p = PullParser(f)

        expected_tag_names = [
            "html", "head", "title", "title", "head", "body", "p", "img",
            "blah", "randomtag", "body", "html"
            ]

        for i, token in enumerate(p.tags()):
            self.assertEquals(token.data, expected_tag_names[i])
        f.close()

        # tag name args
        data, f = self.data_and_file()
        p = PullParser(f)

        expected_tokens = [
            ("starttag", "head", []),
            ("endtag", "head", None),
            ("starttag", "p", []),
            ]

        for i, token in enumerate(p.tags("head", "p")):
            self.assertEquals(token, expected_tokens[i])
        f.close()

    def test_tokens(self):
        from mechanoid.pullparser.PullParser import PullParser
        from mechanoid.misc.Errors import NoMoreTokensError

        # no args
        data, f = self.data_and_file()
        p = PullParser(f)

        expected_token_types = [
            "decl", "data", "starttag", "data", "starttag", "data", "starttag",
            "data", "endtag", "data", "endtag", "data", "starttag", "data",
            "starttag", "data", "starttag", "data", "entityref", "data",
            "charref", "data", "starttag", "data", "comment", "data", "decl",
            "data", "pi", "data", "startendtag", "data", "endtag", "data",
            "endtag", "data"
            ]

        for i, token in enumerate(p.tokens()):
            self.assertEquals(token.type, expected_token_types[i])
        f.close()

        # token type args
        data, f = self.data_and_file()
        p = PullParser(f)

        expected_tokens = [
            ("entityref", "amp", None),
            ("charref", "097", None),
            ]

        for i, token in enumerate(p.tokens("charref", "entityref")):
            self.assertEquals(token, expected_tokens[i])
        f.close()


if __name__ == "__main__":
    import unittest
    unittest.main()
