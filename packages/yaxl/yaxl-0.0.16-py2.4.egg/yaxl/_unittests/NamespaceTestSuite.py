import unittest

from yaxl import *

class NamespaceTests(unittest.TestCase):
	def test_cannotDeleteNamespaceWhileBoundAttributesExist(self):
		test = Element('test', {'xmlns:test': 'http://example.org', 'test:t4': 'something'})
				
		try:
			del test['xmlns:test']
			self.fail('Should have raised a NamespaceNotDeletableException')
		except NamespaceNotDeletableException:
			pass

		del test['test:t4']
		del test['xmlns:test']
		
	def test_canDeleteNamespaceIfMappedInAncestors(self):	
		test = Element('test')
		t1 = test.append('t1', {'test:jim': 'something', 'xmlns:test': 'http://example.org'})
		
		self.assertEquals('http://example.org', t1.find_ns('test'))
		
		try:
			del t1['xmlns:test']
			self.fail('Should have raised a NamespaceNotDeletableException')
		except NamespaceNotDeletableException:
			pass
		
		test['xmlns:test'] = 'http://example.org'
		del t1['xmlns:test']
		
		self.assertEquals('http://example.org', t1.find_ns('test'))
		
	def test_deletingParentBoundNamespaceRemapsAttributesToParentsPrefix(self):
		test = Element('test', {'xmlns:something': 'http://example.org'})
		t1 = test.append('t1', {'test:jim': 'something', 'xmlns:test': 'http://example.org'})
		
		try:
			del t1['xmlns:test']
		except NamespaceNotDeletableException, e:
			self.fail('Should have re-mapped namespace prefix on attributes successfully: %s' % e)
			
		self.assertEquals(t1['something:jim'], 'something')
	
	
	
	def test_deletingParentBoundRemapsChildrenToParentsPrefix(self):
		test = Element('test', {'xmlns:something': 'http://example.org'})
		t1 = test.append('myns:t1', {'xmlns:myns': 'http://example.org'})
		t2 = t1.append('myns:t2')
		
		try:
			del t1['xmlns:myns']
		except NamespaceNotDeletableException:
			self.fail('Should have re-mapped namespace prefix on sub-elements')
					
		self.assertEquals(t1.qname, 'something:t1')
		self.assertEquals(t2.qname, 'something:t2')
		
	def test_deletingDifferentlyMappedPrefix(self):
		test = Element('test', {'xmlns:something': 'http://example.org'})
		t1 = test.append('myns:t1', {'xmlns:myns': 'http://example.org'})
		t2 = t1.append('myns:t2', {'xmlns:myns': 'http://something.org'})
		
		del t1['xmlns:myns']
		
		self.assertEquals('something:t1', t1.qname)
		
		try:
			del t2['xmlns:myns']
			self.fail('Should have raised a NamespaceNotDeletableException')			
		except NamespaceNotDeletableException:
			pass
			
		self.assertEquals(t2['xmlns:myns'], 'http://something.org')
		self.assertEquals('myns:t2', t2.qname)

	def test_insignificantNamespacePrefixEquality(self):
		x = Element('a:x', {'xmlns:a': 'http://example.org'})
		y = Element('b:x', {'xmlns:b': 'http://example.org'})
		
		self.assertEquals(x, y)
	
	def test_defaultNamespace(self):
		x = Element('x', {'xmlns': 'http://example.org'})
		
		self.assertEquals('<x xmlns="http://example.org" />', repr(x))
	
	def test_namespaceDefaultsToParent(self):
		x = Element('a:x', {'xmlns:a': 'http://example.org'})
		y = x.append('a:y')
		
		self.assertEquals('http://example.org', y['xmlns:a'])
		
		x = Element('x', {'xmlns': 'http://example1.org'})
		y = x.append('y')
		
		self.assertEquals('http://example1.org', y['xmlns'])
	
	def test_namespaces_1(self):
		x = parse("""<?xml version="1.0"?>
		<atom:feed xmlns:atom="http://www.w3.org/2005/Atom">
			<atom:title>Test</atom:title>
		</atom:feed>""")
		
		y = parse("""<?xml version="1.0"?>		
		<feed xmlns="http://www.w3.org/2005/Atom">
			<title>Test</title>
		</feed>
		""")
		
		self.assertEquals(x, y)