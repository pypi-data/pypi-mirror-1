jz.magic:

Utility to inteface with the file magic python module.

Requirements:
	file package with python bindings (ftp://ftp.astron.com/pub/file/)

Example:

	>>> sampleData = u'<HTML />'
	>>> sampleMimeType = 'text/html'

	>>> magic = FileMagic

	>>> sampleMimeType == magic.getMimeType(sampleData)
	True

	>>> "html" == magic.getFileExtension(sampleData)
	True