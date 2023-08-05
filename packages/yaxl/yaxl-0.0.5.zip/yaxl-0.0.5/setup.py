from setuptools import setup, find_packages

setup(
	name = 'yaxl',
	version = '0.0.5',	
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
		'Topic :: Software Development :: Libraries :: Python Modules'
    ],	
	keywords = 'xml',
	packages = find_packages(),
	test_suite = 'yaxltests',
	zip_safe = True
)