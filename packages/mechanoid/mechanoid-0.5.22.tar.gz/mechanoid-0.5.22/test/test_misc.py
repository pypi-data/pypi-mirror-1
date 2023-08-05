"""Miscellaneous pyunit tests."""

import cStringIO, string
from unittest import TestCase

class TestUnSeekable:
	def __init__(self, text):
		self._file = cStringIO.StringIO(text)
		self.log = []

	def tell(self): return self._file.tell()

	def seek(self, offset, whence=0): assert False

	def read(self, size=-1):
		self.log.append(("read", size))
		return self._file.read(size)

	def readline(self, size=-1):
		self.log.append(("readline", size))
		return self._file.readline(size)

	def readlines(self, sizehint=-1):
		self.log.append(("readlines", sizehint))
		return self._file.readlines(sizehint)

class SeekableTests(TestCase):
	def testSeekable(self):
		from exceptions import StopIteration
		from mechanoid.seek_wrapper.Seek_Wrapper import Seek_Wrapper
		text = """\
The quick brown fox
jumps over the lazy

dog.

"""
		text_lines = map(lambda l: l+"\n", string.split(text, "\n")[:-1])
		fh = TestUnSeekable(text)
		sfh = Seek_Wrapper(fh)
		assert sfh.read(10) == text[:10]  # calls fh.read
		assert fh.log[-1] == ("read", 10)
		sfh.seek(0)	 # doesn't call fh.seek
		assert sfh.read(10) == text[:10]  # doesn't call fh.read
		assert len(fh.log) == 1
		sfh.seek(0)
		assert sfh.read(5) == text[:5]	# read only part of cached data
		assert len(fh.log) == 1
		sfh.seek(0)
		assert sfh.read(25) == text[:25]  # calls fh.read
		assert fh.log[1] == ("read", 15)
		lines = []
		sfh.seek(-1, 1)
		while 1:
			l = sfh.readline()
			if l == "": break
			lines.append(l)
		assert lines == ["s over the lazy\n"]+text_lines[2:]
		assert fh.log[2:] == [("readline", -1)]*5
		sfh.seek(0)
		lines = []
		while 1:
			l = sfh.readline()
			if l == "": break
			lines.append(l)
		assert lines == text_lines

		fh = TestUnSeekable(text)
		sfh = Seek_Wrapper(fh)
		sfh.read(5)
		sfh.seek(0)
		assert sfh.read() == text
		assert sfh.read() == ""
		sfh.seek(0)
		assert sfh.read() == text
		sfh.seek(0)
		assert sfh.readline(5) == "The q"
		assert sfh.read() == text[5:]
		sfh.seek(0)
		assert sfh.readline(5) == "The q"
		assert sfh.readline() == "uick brown fox\n"

		fh = TestUnSeekable(text)
		sfh = Seek_Wrapper(fh)
		sfh.read(25)
		sfh.seek(-1, 1)
		assert sfh.readlines() == ["s over the lazy\n"]+text_lines[2:]
		nr_logs = len(fh.log)
		sfh.seek(0)
		assert sfh.readlines() == text_lines

		fh = TestUnSeekable(text)
		sfh = Seek_Wrapper(fh)
		count = 0
		limit = 10
		while count < limit:
			if count == 5:
				self.assertRaises(StopIteration, sfh.next)
				break
			else:
				sfh.next() == text_lines[count]
			count = count + 1
		else:
			assert False, "StopIteration not raised"


if __name__ == "__main__":
	import unittest
	unittest.main()
