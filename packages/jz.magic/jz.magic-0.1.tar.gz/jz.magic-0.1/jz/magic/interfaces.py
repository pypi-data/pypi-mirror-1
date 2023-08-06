# zope modules
from zope.interface import Interface


class IFileMagic(Interface):
	"""File magic utility.

	Use magic bytes to get info about file.
	"""

	def getMimeType(data):
		"""Get mime type of data stream."""

	def getFileExtension(data):
		"""Get file extension based on mime type of data stream."""