# zope modules
import unittest
from zope.testing.doctestunit import DocTestSuite
from zope.testing.doctest import DocFileSuite

# jz modules
from test_imagic import TestIFileMagic
from jz.magic.utility import FileMagic


class TestFileMagic(TestIFileMagic):

	def makeTestObject(self):
		return FileMagic


def setUp(test):
	global FileMagic
	test.globs['FileMagic'] = FileMagic


def test_suite():
	return unittest.TestSuite((
		unittest.makeSuite(TestFileMagic),
		DocFileSuite('../readme.txt', setUp=setUp),
		))


if __name__ == '__main__':
	unittest.main(defaultTest='test_suite')