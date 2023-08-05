import unittest

from yaxl import *

class XpathTests(unittest.TestCase):
	def test_parserSpeed(self):
		exprs = [
			"child::para",
			"child::*",
			"child::text()",
			"child::node()",
			"attribute::name",
			"attribute::*",
			"descendant::para",
			"ancestor::div",
			"ancestor-or-self::div",
			"descendant-or-self::para",
			"self::para",
			"child::chapter/descendant::para",
			"child::*/child::para",
			"/",
			"/descendant::para",
			"/descendant::olist/child::item",
			"child::para[position()=1]",
			#"child::para[position()=last()]",			
			#"child::para[position()=last()-1]",
			#"child::para[position()>1]",
			#"following-sibling::chapter[position()=1]",
			#"preceding-sibling::chapter[position()=1]",
			#"/descendant::figure[position()=42]",
			#"/child::doc/child::chapter[position()=5]/child::section[position()=2]",
			'child::para[attribute::type="warning"]',
			#"child::para[attribute::type='warning'][position()=5]",
			#'child::para[position()=5][attribute::type="warning"]',
			"child::chapter[child::title='Introduction']",
			"child::chapter[child::title]",
			#"child::*[self::chapter or self::appendix]",
			#"child::*[self::chapter or self::appendix][position()=last()]",
			#"//element[descendant::y[.='z']][1]"
		]
		
		import time		
		doc = Element('doc')
		doc.append('chapter')
		doc.append('chapter')
		doc.append('chapter')
		doc.append('chapter')		
		
		c = doc.append('chapter')		
		c.append('section')
		c.append('section')		
		
		x = doc.append('div').append('x', {'name': '1'})
		x.append('para')
		x.append('x').append('para').append('olist').append('item')
		x.append('chapter').append('x').append('para')
		x.append('chapter').append('title').appendTextNode('Introduction')
		
		#print '-----------------', x.append('para', {'type': 'warning'})('position()')
		x.append('para', {'type': 'warning'})		
		
		for e in exprs:
			t1 = time.time()
			
			if x(e):
				t2 = time.time()
				delta_t = t2 - t1
				#print delta_t, 'ms'
			else:
				self.fail('XPath expression returned no result: %s' % e)
			
		
	def test_selectRoot(self):
		x = Element('test')
		y = x.append('test2')
		z = x.append('test3')
		
		for node in (x, y, z):
			self.assertEquals(node('/'), x)
	
	def test_selectSubElement(self):
		x = Element('test')
		x.append('x').appendTextNode('something')
		
		self.assertEquals(parse('<x>something</x>'), x('x'))	
		
	def test_simpleAttributeSelect(self):
		x = Element('test', {'x': 5})
		
		self.assertEquals('5', x('@x'))

	def test_leveledSubElementSelect(self):
		x = Element('test')
		x.append('t1').append('t2').appendTextNode('something')
		
		self.assertEquals(str(x('./t1/t2')), 'something')
		
	def test_selectWorksViaCall(self):
		x = Element('test', {'t': 'something else'})
		x.append('t1').appendTextNode('something')
		
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
		self.assertEquals(['5'], x('attribute::*'))
	
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

class LessThanPredicateTests(unittest.TestCase):
	def test_elementValue(self):
		w = Element('w')		
		x = w.append('t', text=10)
		y = w.append('t', text=25)
		z = w.append('t', text=50)
		
		self.assertEquals(None, w('//t[.<10]'))
		self.assertEquals(x, w('//t[.<11]'))
		self.assertEquals(x, w('//t[.<25]'))
		self.assertEquals((x, y), w('//t[.<26]'))
		self.assertEquals((x, y), w('//t[.<50]'))
		self.assertEquals((x, y, z), w('//t[.<51]'))

	def test_attributeValue(self):
		w = Element('w')		
		x = w.append('t', {'a': 10})
		y = w.append('t', {'a': 25})
		z = w.append('t', {'a': 50})
		
		self.assertEquals(None, w('//t[@a<10]'))
		self.assertEquals(x, w('//t[@a<11]'))
		self.assertEquals(x, w('//t[@a<25]'))
		self.assertEquals((x, y), w('//t[@a<26]'))
		self.assertEquals((x, y), w('//t[@a<50]'))
		self.assertEquals((x, y, z), w('//t[@a<51]'))

class GreaterThanPredicateTests(unittest.TestCase):
	def test_elementValue(self):
		w = Element('w')		
		x = w.append('t', text=10)
		y = w.append('t', text=25)
		z = w.append('t', text=50)
		
		self.assertEquals((x, y, z), w('//t[.>9]'))
		self.assertEquals((y, z), w('//t[.>10]'))
		self.assertEquals(z, w('//t[.>25]'))
		self.assertEquals(None, w('//t[.>50]'))
		
	def test_attributeValue(self):
		w = Element('w')		
		x = w.append('t', {'a': 10})
		y = w.append('t', {'a': 25})
		z = w.append('t', {'a': 50})
		
		self.assertEquals((x, y, z), w('//t[@a>9]'))
		self.assertEquals((y, z), w('//t[@a>10]'))
		self.assertEquals(z, w('//t[@a>25]'))
		self.assertEquals(None, w('//t[@a>50]'))
		
class LessThanOrEqualPredicateTests(unittest.TestCase):
	def test_elementValue(self):
		w = Element('w')		
		x = w.append('t', text=10)
		y = w.append('t', text=25)
		z = w.append('t', text=50)

		self.assertEquals(None, w('//t[.<=9]'))
		self.assertEquals(x, w('//t[.<=10]'))
		self.assertEquals((x, y), w('//t[.<=25]'))
		self.assertEquals((x, y, z), w('//t[.<=50]'))

	def test_attributeValue(self):
		w = Element('w')		
		x = w.append('t', {'a': 10})
		y = w.append('t', {'a': 25})
		z = w.append('t', {'a': 50})
		
		self.assertEquals(None, w('//t[@a<=9]'))
		self.assertEquals(x, w('//t[@a<=10]'))
		self.assertEquals((x, y), w('//t[@a<=25]'))
		self.assertEquals((x, y, z), w('//t[@a<=50]'))

class GreaterThanOrEqualPredicateTests(unittest.TestCase):
	def test_elementValue(self):
		w = Element('w')		
		x = w.append('t', text=10)
		y = w.append('t', text=25)
		z = w.append('t', text=50)

		self.assertEquals((x, y, z), w('//t[.>=10]'))
		self.assertEquals((y, z), w('//t[.>=25]'))
		self.assertEquals(z, w('//t[.>=50]'))
		self.assertEquals(None, w('//t[.>=51]'))
		
	def test_attributeValue(self):
		w = Element('w')		
		x = w.append('t', {'a': 10})
		y = w.append('t', {'a': 25})
		z = w.append('t', {'a': 50})

		self.assertEquals((x, y, z), w('//t[@a>=10]'))
		self.assertEquals((y, z), w('//t[@a>=25]'))
		self.assertEquals(z, w('//t[@a>=50]'))
		self.assertEquals(None, w('//t[@a>=51]'))
		
class NotEqualPredicateTests(unittest.TestCase):
	def test_elementValue(self):
		w = Element('w')		
		x = w.append('t', text=10)
		y = w.append('t', text='something')
		z = w.append('t', text=50)
		
		a = z.append('a', text='test')
		a1 = y.append('a', text='nothing')
		
		self.assertEquals((x, z), w('//t[.!="somethingnothing"]'))
		self.assertEquals((x, y), w('//t[.!="50test"]'))
		self.assertEquals((x, y, z), w('//t[.!=5]'))
		self.assertEquals(z, w('//t[a!="nothing"]'))
		
	def test_attributeValue(self):
		w = Element('w')		
		x = w.append('t', {'a': 10})
		y = w.append('t', {'b': 'something'})
		z = w.append('t', {'a': 50})

		self.assertEquals(z, w('//t[@a!=10]'))
		self.assertEquals(x, w('//t[@a!=50]'))
		self.assertEquals((x, z), w('//t[@a!=75]'))
		self.assertEquals(y, w('//t[@b!=50]'))
		self.assertEquals(None, w('//t[@b!="something"]'))

class EqualPredicateTests(unittest.TestCase):
	def test_elementValue(self):
		w = Element('w')		
		x = w.append('t', text=10)
		y = w.append('t', text='something')
		y1 = w.append('t', text='something')
		z = w.append('t', text=50)

		self.assertEquals((y, y1), w('//t[.="something"]'))
		self.assertEquals(z, w('//t[.=50]'))
		self.assertEquals(None, w('//t[.=5]'))
		self.assertEquals(x, w('//t[.=10]'))
		
	def test_elementValueEqualPredicateWithInteger(self):
		w = Element('w')		
		
		x = w.append('x')
		x2 = w.append('x', text='something')
		x3 = w.append('x')
		
		y = x.append('y', text=5)
		x.append('y')
		x3.append('y', text=5)
		
		self.assertEquals(y, x('y[.=5]'))
		self.assertEquals((y, y), w('x/y[.=5]'))
		self.assertEquals((x, x3), w('x[y=5]'))
	
	def test_elementValueEqualPredicateWithString(self):
		w = Element('w')		

		x = w.append('x')
		x2 = w.append('x', text='something')
		x3 = w.append('x')

		y = x.append('y', text='another')
		x.append('y')
		x3.append('y', text="another")

		self.assertEquals(y, x('y[.="another"]'))
		self.assertEquals((y, y), w('x/y[.="another"]'))
		self.assertEquals((x, x3), w('x[y="another"]'))
	
	def test_attributeValueEqualPredicateWithInteger(self):
		x = Element('x')
		y = x.append('y', {'a': 5})
		y2 = x.append('y', {'a': 'something'})
		
		self.assertEquals(y, x('y[@a=5]'))

	def test_attributeValueEqualPredicateWithDoubleQuotedString(self):
		x = Element('x')
		y = x.append('y', {'a': 'another thing'})
		y2 = x.append('y', {'a': 'something'})		

		self.assertEquals(y2, x('y[@a="something"]'))
		
class ExistancePredicateTests(unittest.TestCase):
	def test_elementExistancePredicate(self):
		x = Element('x')
		y2 = x.append('y', {'a': 5})
		y = x.append('y')
		y.append('z')
		y3 = x.append('y', {'b': 5})
		y3.append('z')		

		self.assertEquals((y, y3), x('y[z]'))
		self.assertEquals(y2, x('y[@a]'))
		self.assertEquals(y3, x('y[z][@b]'))

class DataTypeTests(unittest.TestCase):
	def atest_nodeSetUnion(self):
		x = Element('x')
		y1 = x.append('y')
		y2 = x.append('y', {'a': 1})
		y3 = x.append('y', {'b': 2})

		self.assertEquals((y2, y3), x('//y[@a="1"]|y[@b=1]'))

class NodeSetCoreFunctionTests(unittest.TestCase):
	def test_function_position(self):
		x = Element('x')
		y1 = x.append('y1')
		y2 = x.append('y2')

		self.assertEquals(1, x('y1/position()'))
		self.assertEquals(1, y1('position()'))
		self.assertEquals(2, x('y2/position()'))
		self.assertEquals(2, y2('position()'))
		self.assertEquals(y2, x('child::*[position()=2]'))
		
	def test_last(self):
		x = Element('x')
		y1 = x.append('y1')
		y2 = x.append('y2')		
		
		self.assertEquals(2, x('last()'))
		self.assertEquals(y2, x('child::*[position()=last()]'))
		
	def test_count(self):
		x = Element('x')
		x.append('y')
		
		self.assertEquals(1, x('count(y)'))
		self.assertEquals(1, x('count(child::*)'))
		
		x.append('y')
		
		self.assertEquals(2, x('count(child::*)'))