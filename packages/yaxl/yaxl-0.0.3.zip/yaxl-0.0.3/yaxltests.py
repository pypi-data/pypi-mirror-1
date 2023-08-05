import unittest

from yaxl import *

class ElementTests(unittest.TestCase):
	def test_asdoc(self):
		x = Element('test')		
		
		assert '<?xml version="1.0"?><test />' == x.asdoc()
		assert x.asdoc() == x.__repr__(asdoc=True)
	
	def test_addingExistingNamespaceIsNoop(self):
		t = Element('test')
		t1 = t.append('t1')
		
		t.map('test', 'http://example.org')
		
		assert 'http://example.org' == t1.find_ns('test')
		assert len(t1.namespaces) == 0
		
		t.map('test', 'http://example.org')
		
		assert 'http://example.org' == t1.find_ns('test')
		assert len(t1.namespaces) == 0
		
	def test_simpleEquality(self):
		assert Element('test') == Element('test')
		
	def test_equalityWithAttributesAndSubElements(self):
		t1 = Element('test')
		t2 = Element('test')
		
		t1.append('t2', {'x': 5})
		t2.append('t2', {'x': 5})
		
		assert t1 == t2	
	
	def test_attributeValuesAreNormalized(self):
		t1 = Element('test')
		t2 = Element('test')
				
		t1.append('t2', {'x': 5})
		t2.append('t2', {'x': 5})
		
		t1['test'] = 5
		t2['test'] = '5'
		
		assert t1 == t2
		
		t1['t2'] = u'something'
		t2['t2'] = 'something'
		
		assert t1 == t2
		
		t1[u't3'] = 'something'
		t2['t3'] = 'something'
		
		assert t1 == t2
	
	def test_namespaces(self):
		t1 = Element('test', {'xmlns:test2': 'http://www.example2.org'})
		
		t1.map('test', 'http://www.example.org')
		
		assert 'test' in t1.namespaces.keys()
		assert 'test2' in t1.namespaces.keys()

		t2 = t1.append('t2')
		
		assert t2.parent is t1
		assert isinstance(t2, Element)
		
		assert t2['xmlns:test'] == t1['xmlns:test']
		
		assert 'http://www.example.org' == t2.find_ns('test')
		assert 'http://www.example2.org' == t2.find_ns('test2')		
		
		t2['test:bob'] = 5
		
		t2['xmlns:test'] = 'http://www.example3.org'
		
		t3 = t2.append('test:t3')
		
		assert 'http://www.example3.org' == t3.find_ns('test')
	
	def test_namespacesGetOutput(self):
		t = Element('test:t', {'xmlns:test': 'http://www.example.org/'})
		assert str(t) == '<test:t xmlns:test="http://www.example.org/" />'
	
	def test_elementsOutputTextContents(self):
		test = Element('test')
		test.text = 'something'
		
		assert str(test) == '<test>something</test>'
	
	def test_addTextAsPartOfAppend(self):
		t = Element('t')
		t.append('x', text='something')
		
		assert t == parse('<t><x>something</x></t>')
	
	def test_Element2Document(self):	
		test = parse('<test />')
		
		self.assertEquals(test, parse('<test />'))
		
		assert str(test) == '<test />'
		
		test['t1'] = 'something'
		self.assertEquals(test, parse('<test t1="something" />'))
				
		test.append('t2')		
		assert test == parse('<test t1="something"><t2 /></test>')
		
		del test['t1']
		test.append('t3', {u'bob': u'test', u'jim': u'3'})
		
		try:
			test.append('test:t1')
			self.fail('Should have thrown UndeclaredNamespaceException')
		except UndeclaredNamespaceException:
			pass
		
		try:
			test['test:something'] = 'something else'
			self.fail('Should have thrown UndeclaredNamespaceException')
		except UndeclaredNamespaceException:
			pass
		
		test = Element('test', {'xmlns:test': 'http://www.example.org'})
		test.append('t2')
		test.append('t3', {'bob': 'test', 'jim': 3})
		test.append('test:t1')		
		
		d = parse("""
		<test xmlns:test="http://www.example.org">
			<t2 />
			<t3 bob="test" jim="3" />
			<test:t1 />
		</test>""")
		
		assert test == d
		
		test['test:t4'] = 'something'
		
		self.assertEquals(test, parse('<test xmlns:test="http://www.example.org" test:t4="something"><t2 /><t3 bob="test" jim="3" /><test:t1 /></test>'))
		
		test = Element('test', {'xmlns:test': 'http://example.org', 'test:t4': 'something'})
		
		try:
			del test['xmlns:test']
			self.fail('Should have raised a NamespaceNotDeletableException')
		except NamespaceNotDeletableException:
			pass
			
		del test['test:t4']
		del test['xmlns:test']
		'''
		test = Element('test')
		test.namespaces['test'] = 'http://example.org'
		t1 = test.append('t1', {'test:jim': 'something'})
		
		assert 'http://example.org' == t1.find_ns('test')
		del test['xmlns:test']
		assert 'http://example.org' == t1.find_ns('test')
		'''
		
if __name__ == '__main__':
	unittest.main()