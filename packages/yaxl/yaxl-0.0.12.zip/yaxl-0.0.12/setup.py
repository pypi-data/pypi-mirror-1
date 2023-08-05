from setuptools import setup, find_packages

setup(
	name = 'yaxl',
	version = '0.0.12',
	description = 'Yet Another (Pythonic) XML Library',
	long_description = """A library for reading, writing and manipulating XML in Python""",
	author = 'Iain Lowe',
	author_email = 'ilowe@cryogen.com',
	url = 'http://www.ilowe.net/software/yaxl',
	license = 'MIT License',
	classifiers = [
		'Development Status :: 4 - Beta',
		'Intended Audience :: Developers',
		'License :: OSI Approved :: MIT License',
		'Natural Language :: English',
		'Operating System :: OS Independent',
		'Programming Language :: Python',    	
		'Topic :: Software Development :: Libraries :: Python Modules',
		'Topic :: Text Processing :: Markup :: XML'
    ],	
	keywords = 'xml',
	test_suite = 'yaxl._unittests.test_suite',
	zip_safe = True
)