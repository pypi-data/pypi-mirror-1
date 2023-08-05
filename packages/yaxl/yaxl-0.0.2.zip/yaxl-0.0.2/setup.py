from setuptools import setup, find_packages

setup(
	name = 'yaxl',
	version = '0.0.2',
	packages = find_packages(),
	author = 'Iain Lowe',
	author_email = 'ilowe@cryogen.com',
	description = 'Yet Another (Pythonic) XML Library',
	license = 'MIT',
	keywords = 'xml',
	url = 'http://www.ilowe.net/software/yaxl',
	test_suite = 'yaxltests',
)