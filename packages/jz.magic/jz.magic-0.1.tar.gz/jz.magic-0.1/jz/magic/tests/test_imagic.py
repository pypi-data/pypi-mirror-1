# zope modules
import unittest
from zope.testing.doctestunit import DocTestSuite
from zope.interface.verify import verifyObject

# custom modules
from jz.magic.interfaces import IFileMagic


class TestIFileMagic(unittest.TestCase):
	"""Interface test for magic utility."""

	def makeTestObject(self):
		raise NotImplemented()

	def test_verifyInterfaceImplementation(self):
		self.assert_(verifyObject(IFileMagic, self.makeTestObject()))


def test_suite():
	return unittest.TestSuite((
		))


if __name__ == '__main__':
	unittest.main(defaultTest='test_suite')