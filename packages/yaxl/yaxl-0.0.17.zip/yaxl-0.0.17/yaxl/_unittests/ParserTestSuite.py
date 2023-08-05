import unittest

from yaxl import *
from cStringIO import StringIO
	
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
	
	def test_allCharactersArePickedUp(self):
		x = Element('x', text='Hello, World!')
		y = Element('x', text='Hello,')
		y.append('y')
		y += ' World!'
		
		#self.assertEquals(x, y)
		self.assertEquals(str(x), str(parse('<x>Hello,<img url="something else" /> World!</x>')))
	
	def test_basicXMLFragment(self):
		test = parse('<test />')
				
		self.assertEquals(test, parse('<test />'))		
		self.assertEquals(repr(test), '<test />')
		
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
		
		self.assertEquals(str(test('address/street')), 'Coconut Grove')
		
	def test_parseUTF8Chinese(self):
		t1 = parse('yaxl/_unittests/testcases/xml/test_utf8_chinese_1.xml')
		
		try:
			t1.write(StringIO(), 'latin1')
			self.fail('Should have raised a UnicodeEncodeError')
		except UnicodeEncodeError:
			pass
			
		t1.write(StringIO())
		
		t2 = parse('yaxl/_unittests/testcases/xml/test_utf8_chinese_2.xml')
		
		t2.write(StringIO(), 'latin1')
		t2.write(StringIO())
		