# zo pe modules
from zope.interface import implements

# jz modules
from interfaces import IFileMagic

# external modules
import magic


class FileMagic(object):
	"""File magic utility.

	Identify files by their magic code (first few characters in file contents).
	"""

	implements(IFileMagic)

	magicdb = None

	def __init__(self):
		self.magicdb = magic.open(magic.MAGIC_MIME)
		self.magicdb.load()

	def getMimeType(self, data):
		mimetype = self.magicdb.buffer(data)
		return mimetype

	def getFileExtension(self, data):
		mimetype = self.getMimeType(data)
		return mimetype.split("/")[1].split(".")[-1]


FileMagic = FileMagic()