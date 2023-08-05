import unittest

from yaxl import *
	
class ElementTests(unittest.TestCase):
	def test_iterationOverChildren(self):
		x = Element('x')
		y1 = x.append('y1')
		y2 = x.append('y2')
		y3 = x.append('y3')
		
		i = iter(x)
		
		self.assertEquals(y1, i.next())
		self.assertEquals(y2, i.next())
		self.assertEquals(y3, i.next())
		
		try:
			i.next()
			self.fail('Should have raised StopIteration')
		except StopIteration:
			pass
	
	def test_listStyleAccessToChildren(self):
		x = Element('x')
		y1 = x.append('y1')
		y2 = x.append('y2')
		y3 = x.append('y3')
		
		self.assertEquals(y1, x[0])
		self.assertEquals(y2, x[1])
		self.assertEquals(y3, x[2])
	
	"""
	def test_propertyStyleAccessToChildren(self):
		x = Element('x')
		y1 = x.append('y1')
		y2 = y1.append('y2')
		y3 = x.append('y3')
		
		self.assertEquals(y1, x/'y1')
		self.assertEquals(y2, x.y1.y2)
		self.assertEquals(y3, x.y3)
	"""
	
	def test_iadd_appendsText(self):
		x = Element('x')
		x += 'hello'
		
		self.assertEquals('hello', x.text)
		
		x += ', world!'
		
		self.assertEquals('hello, world!', x.text)
	
	def test_asdoc(self):
		x = Element('test')		
		
		self.assertEquals('<?xml version="1.0" encoding="UTF8"?><test />', x.asdoc())
		self.assertEquals(x.__repr__(asdoc=True), x.asdoc())

	def test_addingExistingNamespaceIsNoop(self):
		t = Element('test')
		t1 = t.append('t1')
		
		t.map('test', 'http://example.org')
		
		self.assertEquals('http://example.org', t1.find_ns('test'))
		self.assertEquals(len(t1.namespaces), 1)
		
		t.map('test', 'http://example.org')
		
		self.assertEquals('http://example.org', t1.find_ns('test'))
		self.assertEquals(len(t1.namespaces), 1)
	
	def test_xmlNamespaceExistsByDefault(self):
		x = Element('x')
		x['xml:lang'] = 'en'
	
	def test_defaultNamespace(self):
		x = Element('x', {'xmlns': 'http://example.org'})
		self.assertEquals('<x xmlns="http://example.org" />', str(x))
		
		y = parse('<x xmlns="http://example.org" />')
		self.assertEquals('<x xmlns="http://example.org" />', str(y))
		self.assertEquals(str(y), str(x))
	
	def test_simpleEquality(self):
		self.assertEquals(Element('test'), Element('test'))
		
	def test_equalityWithAttributesAndSubElements(self):
		t1 = Element('test')
		t2 = Element('test')
		
		t1.append('t2', {'x': 5})
		t2.append('t2', {'x': 5})
		
		self.assertEquals(t1, t2)
		
	def test_equalityWithNonElement(self):
		x = Element('x')
		self.assertTrue(x != 'x')
	
	def test_attributeValuesAreNormalized(self):
		t1 = Element('test')
		t2 = Element('test')
				
		t1.append('t2', {'x': 5})
		t2.append('t2', {'x': 5})
		
		t1['test'] = 5
		t2['test'] = '5'
		
		self.assertEquals(t1, t2)
		
		t1['t2'] = u'something'
		t2['t2'] = 'something'
		
		self.assertEquals(t1, t2)
		
		t1[u't3'] = 'something'
		t2['t3'] = 'something'
		
		self.assertEquals(t1, t2)
	
	def test_namespaces(self):
		t1 = Element('test', {'xmlns:test2': 'http://www.example2.org'})
		
		t1.map('test', 'http://www.example.org')
		
		self.assertTrue('test' in t1.namespaces.keys())
		self.assertTrue('test2' in t1.namespaces.keys())

		t2 = t1.append('t2')
		
		self.assertTrue(t2.parent is t1)
		self.assertTrue(isinstance(t2, Element))
		
		self.assertEquals(t2['xmlns:test'], t1['xmlns:test'])
		
		self.assertEquals('http://www.example.org', t2.find_ns('test'))
		self.assertEquals('http://www.example2.org', t2.find_ns('test2'))
		
		t2['test:bob'] = 5
		
		t2['xmlns:test'] = 'http://www.example3.org'
		
		t3 = t2.append('test:t3')
		
		self.assertEquals('http://www.example3.org', t3.find_ns('test'))
	
	def test_namespacesGetOutput(self):
		t = Element('test:t', {'xmlns:test': 'http://www.example.org/'})
		self.assertEquals(str(t), '<test:t xmlns:test="http://www.example.org/" />')
	
	def test_elementsOutputTextContents(self):
		test = Element('test')
		test.text = 'something'
		
		self.assertEquals(str(test), '<test>something</test>')
	
	def test_addTextAsPartOfAppend(self):
		t = Element('t')
		t.append('x', text='something')
		
		self.assertEquals(t, parse('<t><x>something</x></t>'))
	
	def test_intsOutputAsString(self):
		t = Element('t')
		t.text = 5
		
		self.assertEquals('<t>5</t>', str(t))
	
	def test_Element2Document(self):	
		test = parse('<test />')		
		test['t1'] = 'something'				
		test.append('t2')
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
			
	"""
	def test_listStyleAppend(self):
		t1 = Element('t1')
		t1.append(
			['t2',
			('t3', None, 'hello'),
			('t4', {'x': 56})])
		
		self.assertEquals(t1, parse(
		<t1>
			<t2 />
			<t3>hello</t3>
			<t4 x="56" />
		</t1>
	"""
	
	def test_qnameIsReadOnly(self):
		x = Element('x')
		
		try:
			x.qname = 'b'
			self.fail('Should have thrown a TypeError')
		except TypeError:
			pass
	
	def test_significantChildOrderInEquality(self):
		t1 = Element('t1')
		t1.append('t2')
		t1.append('t3')
		t1.append('t4')
		
		t2 = Element('t1')
		t2.append('t2')		
		t2.append('t4')
		t2.append('t3')
		
		self.assertTrue(t1 != t2)
	
	def test_insignificantAttributeOrderInEquality(self):
		t1 = Element('t1')
		t1.append('t2', {'a': 1, 'b': 2})
		t1.append('t4')
		t1.append('t3')		
		
		t2 = Element('t1')
		t2.append('t2', {'b': 2, 'a': 1})
		t2.append('t4')
		t2.append('t3')
		
		self.assertTrue(t1 == t2)
		
	def test_insignificantUnusedNamespaces(self):
		t1 = Element('t1')
		t1.append('t2')
		t1.append('t3', {'xmlns:test': 'http://example.org'})
		t1.append('t4')
		
		t2 = Element('t1')
		t2.append('t2')		
		t2.append('t3')		
		t2.append('t4')		
		
		self.assertTrue(t1 == t2)
	
	def test_documentEquality(self):
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

		self.assertEquals(test, d)

		test['test:t4'] = 'something'

		self.assertEquals(test, parse('<test xmlns:test="http://www.example.org" test:t4="something"><t2 /><t3 bob="test" jim="3" /><test:t1 /></test>'))
		
	def test_dontOutputUnusedNamespaces(self):
		x = Element('x', {'xmlns:test': 'http://example.org'})
		self.assertEquals('<x />', str(x))
	
	def test_namespaceDeclarationsPulledUp(self):
		x = Element('x', {'xmlns:a': 'a', 'xmlns:b': 'b'})
		y = x.append('a:y')
		
		self.assertEquals('<x xmlns:a="a"><a:y /></x>', str(x))
		
	def test_namespaceDeclarationsMinimized(self):
		x = Element('x', {'xmlns:a': 'a', 'xmlns:b': 'b'})
		x.append('a:y')
		x.append('a:z')
				
		self.assertEquals('<x xmlns:a="a"><a:y /><a:z /></x>', str(x))
		
	def test_appendBindsNamespacesBeforeCreatingSubElement(self):
		test = Element('test', {'xmlns:something': 'http://example.org'})
		t1 = test.append('myns:t1', {'xmlns:myns': 'http://example.org'})

	def test_encodedOutputAddsEncodingToPI(self):
		test = Element('x')
		test.text = 'hello'
		
		self.assertEquals('<?xml version="1.0" encoding="utf8"?><x>hello</x>', test.asdoc('utf8'))