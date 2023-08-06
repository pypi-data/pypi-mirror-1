from setuptools import setup, find_packages

setup(
	name = "jz.stream",
	version = "0.1",
	description = """Generic data stream classes and views.""",
	author_email = "gabi@jbox-comp.com",
	author = "Gabi Shaar",
	license = "GPL",
	url = "http://www.jellofishi.com/zope",
	packages = find_packages(),
	namespace_packages = ["jz",],
	package_data = {'': ['*.txt', '*.zcml']},
	install_requires = [
		'setuptools',
		'jz.common',
		'jz.magic',
		'jz.filerepresentation',
		'jz.datetime',
	],
	)
