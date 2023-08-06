from setuptools import setup, find_packages

setup(
	name = "jz.cache",
	version = "0.1",
	description = """Cache utilties which store data in annotations.""",
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
	],
	)
