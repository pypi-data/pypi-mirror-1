import os
import doctest
import unittest

import ParserTestSuite, ElementTestSuite, NamespaceTestSuite, XPathTestSuite
test_modules = [ParserTestSuite, ElementTestSuite, NamespaceTestSuite, XPathTestSuite]

def test_suite():
	suite = unittest.TestSuite()
	
	for mod in test_modules:
		suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(mod))
	
	suite.addTests(doctest.DocFileSuite('../../docs/developing-with-yaxl.txt'))
	
	for path, dnames, fnames in os.walk(os.path.join(os.path.dirname(__file__), 'testcases/doctests')):
		for fname in fnames:
			if '.svn' not in path:
				suite.addTests(doctest.DocFileSuite(os.path.join(path, fname)))
	
	return suite