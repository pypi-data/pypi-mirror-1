import unittest

from yaxl import *

class XpathTests(unittest.TestCase):
	def test_selectRoot(self):
		x = Element('test')
		y = x.append('test2')
		z = x.append('test3')
		
		for node in (x, y, z):
			self.assertEquals(node.select('/'), x)
	
	def test_selectSubElement(self):
		x = Element('test')
		x.append('x').text = 'something'
		
		self.assertEquals(parse('<x>something</x>'), x.select('x'))	
		
	def test_simpleAttributeSelect(self):
		x = Element('test', {'x': 5})
		
		self.assertEquals('5', x.select('@x'))

	def test_leveledSubElementSelect(self):
		x = Element('test')
		x.append('t1').append('t2').text = 'something'
		
		self.assertEquals(x('./t1/t2').text, 'something')
		
	def test_selectWorksViaCall(self):
		x = Element('test', {'t': 'something else'})
		x.append('t1').text = 'something'
		
		self.assertEquals(x('t1'), parse('<t1>something</t1>'))		
		self.assertEquals(x('@t'), 'something else')
	
	def test_unabbrevChildAxis_singleStep(self):
		x = Element('x')
		y = x.append('y')
		y2 = x.append('y')
		z = y.append('z')
		
		self.assertEquals(x('/child::y'), (y, y2))
		self.assertEquals(y('child::z'), z)
		self.assertEquals(None, x('child::z'))		
		
	def test_childAxis_multiStep(self):
		x = Element('x')
		y = x.append('y')		
		z = y.append('z')
		
		self.assertEquals(x('/y/z'), z)
		self.assertEquals(x('y/z'), z)		
		
	def test_unabbrevDescendantAxis_singleStep(self):
		x = Element('x')
		y = x.append('y')
		z = y.append('z')
		z2 = y.append('z')
		w = y.append('w')
		
		self.assertEquals(x('/descendant::z'), (z, z2))
		self.assertEquals(x('descendant::w'), w)
		
	def test_descendantAxis(self):
		x = Element('x')		
		y = x.append('y')
		z = y.append('z')
		z2 = y.append('z')
		w = y.append('w')
		w2 = y.append('w')
		w3 = z2.append('w')
		a = x.append('a')
		w4 = a.append('w')
		
		self.assertEquals(x('//z'), (z, z2))
		self.assertEquals(x('y//w'), (w, w2, w3))
		self.assertEquals(x('a//w'), w4)
		self.assertEquals(x('//w'), (w, w2, w3, w4))
		
	def test_unabbrevParentAxis_singleStep(self):
		x = Element('x')
		y = x.append('y')
		
		self.assertEquals(x, y('parent::x'))
		self.assertEquals(x, y('parent::*'))
		self.assertEquals(None, y('parent::w'))
		self.assertEquals(None, x('parent::*'))
		
	def test_parentAxis_multiStep(self):
		x = Element('x', {'a': 5})
		y = x.append('y')
		w = x.append('w', {'b': 'hello'})
		z = y.append('z')
		
		self.assertEquals(x, z('../..'))
		self.assertEquals('5', z('../../@a'))
		self.assertEquals('hello', z('parent::*/../child::w/@b'))
		
	def test_unabbrevAncestorAxis_singleStep(self):
		x = Element('x')
		y = x.append('y')
		
		self.assertEquals(x, y('ancestor::x'))
		self.assertEquals(x, y('ancestor::*'))
		self.assertEquals(None, y('ancestor::y'))
	
	# Here we are missing tests for the following axes:
	#	following-sibling
	#	preceding-sibling
	#	following
	#	preceding	
	
	def test_unabbrevAttributeAxis_singleStep(self):
		x = Element('x', {'a': 5})
		
		self.assertEquals('5', x('attribute::a'))
	
	# Missing namespace axis tests
	
	def test_unabbrevSelfAxis_singleStep(self):
		x = Element('x')
		
		self.assertEquals(None, x('self::w'))
		self.assertEquals(x, x('self::x'))
		self.assertEquals(x, x('self::*'))
		
	def test_selfAxis(self):
		x = Element('x', {'t': 5})
		
		self.assertEquals(None, x('./w/w'))
		self.assertEquals(x, x('.'))		
		
		
	def test_unabbrevDescendantOrSelfAxis_singleStep(self):
		x = Element('x')
		y = x.append('y')
		z = y.append('z')
		
		self.assertEquals(z, x('descendant-or-self::z'))
		self.assertEquals(z, y('descendant-or-self::z'))
		self.assertEquals(z, z('descendant-or-self::z'))
		
	def test_unabbrevAncestorOrSelfAxis_singleStep(self):
		x = Element('x')
		y = x.append('y')
		z = y.append('z')
		
		self.assertEquals(x, x('ancestor-or-self::x'))
		self.assertEquals(x, y('ancestor-or-self::x'))
		self.assertEquals(x, z('ancestor-or-self::x'))
		
	def test_unabbrevMultiStep(self):
		x = Element('x')
		y = x.append('y', {'a': 5, 'b': 'something'})
		z1 = y.append('z', {'a': 17}, text='a test')
		z2 = y.append('z')
		z3 = y.append('z', text='another test')
		
		self.assertEquals((z1, z2, z3), x('child::y/child::z'))
		self.assertEquals('17', x('descendant-or-self::z/attribute::a'))
		self.assertEquals(('5', '17'), x('descendant-or-self::*/attribute::a'))
		self.assertEquals(None, x('descendant-or-self::z/attribute::b'))

	def test_elementExistancePredicate(self):
		x = Element('x')
		y2 = x.append('y', {'a': 5})
		y = x.append('y')
		y.append('z')		
		
		self.assertEquals(y, x('y[z]'))
		self.assertEquals(y2, x('y[@a]'))
	
	"""
	def test_attributeValueEqualPredicate(self):
		x = Element('x')
		y = x.append('y', {'a': 5})
		y2 = x.append('y', {'a': 'something'})
		
		self.assertEquals(y, x('y[@a=5]'))
		self.assertEquals(y2, x('y[@a="something"]'))
	"""
	
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
		
		self.assertEquals('<?xml version="1.0"?><test />', x.asdoc())
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
		
		
		
	def test_appendBindsNamespacesBeforeCreatingSubElement(self):
		test = Element('test', {'xmlns:something': 'http://example.org'})
		t1 = test.append('myns:t1', {'xmlns:myns': 'http://example.org'})

class ParserTests(unittest.TestCase):
	def test_attributesAreParsed(self):
		test = parse('<test />')		
		test['t1'] = 'something'
		self.assertEquals(test, parse('<test t1="something" />'))
		
	def test_childrenAreParsed(self):
		test = parse('<test />')		
		test['t1'] = 'something'				
		test.append('t2')		
		self.assertEquals(test, parse('<test t1="something"><t2 /></test>'))
	
	def test_basicXMLFragment(self):
		test = parse('<test />')
				
		self.assertEquals(test, parse('<test />'))		
		self.assertEquals(str(test), '<test />')
		
	def test_textIsParsed(self):
		test = parse("""
		<person id="1234">
			<name>Bob Smith</name>
			<age>25</age>
			<address>
					<street>Coconut Grove</street>
					<number>4160</number>
			</address>
		</person>""")
		
		self.assertEquals(test('address/street').text, 'Coconut Grove')

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
		
if __name__ == '__main__':
	unittest.main()