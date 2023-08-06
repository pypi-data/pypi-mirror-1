from setuptools import setup, find_packages

setup(
	name = "jz.magic",
	version = "0.1",
	description = """Utility interface to magic python module.""",
	author_email = "gabi@jbox-comp.com",
	author = "Gabi Shaar",
	license = "GPL",
	url = "http://www.jellofishi.com/zope",
	packages = find_packages(),
	namespace_packages = ["jz",],
	package_data = {'': ['*.txt', '*.zcml']},
	install_requires = [
		'setuptools',
	],
	)
