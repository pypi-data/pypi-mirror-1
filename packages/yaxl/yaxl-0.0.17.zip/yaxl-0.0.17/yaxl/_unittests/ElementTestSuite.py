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
    
    def test_createUsingKwArgsAsAttributes(self):
        x = Element('x', test=5)
        y = x.append('y', test=6)
        
        self.assertEquals(x['test'], '5')
        self.assertEquals(y['test'], '6')
    
    """
    def test_reparseElement(self):
        x = Element('x', text='Something')
        
        self.assertEquals(None, x('//b'))
        
        x += '<b>test</b>'
        
        self.assertEquals(None, x('//b'))
        
        x.append('b', text='test2')
        
        self.assertEquals(1, len(x('//b')))
        
        x.reparse()
        
        self.assertEquals(2, len(x('//b')))
    """
    
    def test_iterExcludesNonTextNodes(self):
        x = Element('x')
        x += 'Hello '
        y = x.append('y', text='world')
        
        self.assertEquals('<x>Hello <y>world</y></x>', repr(x))
        
        x += ', this is a test!'
        
        self.assertEquals('<x>Hello <y>world</y>, this is a test!</x>', repr(x))
        
        self.assertEquals(len([child for child in x]), 1)
        self.assertEquals(y, [child for child in x][0])
        
    def test_childrenPropertyExcludesNonTextNodes(self):
        x = Element('x')
        x += 'Hello '
        y = x.append('y', text='world')

        self.assertEquals('<x>Hello <y>world</y></x>', repr(x))

        x += ', this is a test!'

        self.assertEquals('<x>Hello <y>world</y>, this is a test!</x>', repr(x))

        self.assertEquals(len([child for child in x._children]), 1)
        self.assertEquals(y, [child for child in x._children][0])
    
    def test_iadd_appendsText(self):
        x = Element('x')
        x += 'hello'
        
        self.assertEquals('hello', str(x))
        
        x += ', world!'
        
        self.assertEquals('hello, world!', str(x))
    
    def test_nodeStringValueGlomsChildStringValues(self):
        x = parse("""<x>Hello cruel <test>world<strong>!</strong></test></x>""")
        self.assertEquals('Hello cruel world!', str(x))
    
    def test_mixedContentPreservesChildTags(self):
        x = parse("""<x>a <y>b</y>c</x>""")     
        self.assertEquals('<x>a <y>b</y>c</x>', repr(x))
    
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
        self.assertEquals('<x xmlns="http://example.org" />', repr(x))
        
        y = parse('<x xmlns="http://example.org" />')
        self.assertEquals('<x xmlns="http://example.org" />', repr(y))
        self.assertEquals(repr(y), repr(x))
    
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
        self.assertEquals(repr(t), '<test:t xmlns:test="http://www.example.org/" />')
    
    def test_elementsOutputTextContents(self):
        test = Element('test', text='something')        
        self.assertEquals(repr(test), '<test>something</test>')
    
    def test_addTextAsPartOfAppend(self):
        t = Element('t')
        t.append('x', text='something')
        
        self.assertEquals(t, parse('<t><x>something</x></t>'))
    
    def test_intsOutputAsString(self):
        t = Element('t', text='5')      
        
        self.assertEquals('<t>5</t>', repr(t))
    
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
    
    def test_settingQNameWithNoNamespaceSetsLocalname(self):
        x = Element('x')
        
        x.qname = 'b'
        assert x.localname == 'b'       
        
    def test_settingQNameWithNamespaceSetsLocalnameAndNamespace(self):
        x = Element('x', namespaces={'a': 'ns_a'})
                
        x.qname = 'a:b'
        
        assert x.ns == 'a'
        assert x.localname == 'b'
    
    def test_settingQNameToUnMappedNamespace(self):
        x = Element('x')
        
        try:
            x.qname = 'a:b'
            self.fail('Should have thrown a NamespaceException')
        except UndeclaredNamespaceException:
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
        self.assertEquals('<x />', repr(x))
    
    def test_namespaceDeclarationsPulledUp(self):
        x = Element('x', {'xmlns:a': 'a', 'xmlns:b': 'b'})
        y = x.append('a:y')
        
        self.assertEquals('<x xmlns:a="a"><a:y /></x>', repr(x))
        
    def test_namespaceDeclarationsMinimized(self):
        x = Element('x', {'xmlns:a': 'a', 'xmlns:b': 'b'})
        x.append('a:y')
        x.append('a:z')
                
        self.assertEquals('<x xmlns:a="a"><a:y /><a:z /></x>', repr(x))
    
    def test_elementContents(self):
        x = Element('x', text='something')
        self.assertEquals('something', str(x))
    
    def test_appendBindsNamespacesBeforeCreatingSubElement(self):
        test = Element('test', {'xmlns:something': 'http://example.org'})
        t1 = test.append('myns:t1', {'xmlns:myns': 'http://example.org'})

    def test_encodedOutputAddsEncodingToPI(self):
        test = Element('x')
        self.assertEquals('<?xml version="1.0" encoding="utf8"?><x />', test.asdoc('utf8'))
        
    def test_appendElement(self):
        x = Element('x')
        y = Element('y')
        
        x.append(y)
        
        self.assertEquals('<x><y /></x>', repr(x))
        
    def test_detachElement(self):
        x = Element('x')
        y = x.append('y')
        
        y.detach()
        
        self.assertEquals(None, y.parent)
        
        y.detach()
    
    def test_detachPreservesNamespaceMappings(self):
        x = Element('x', {'xmlns': 'a'})
        y = x.append('y')
        
        y.detach()
        
        self.assertEquals('a', y['xmlns'])
    
    def test_detachPreservesAncestralNamespaceMappings(self):       
        w = Element('w', {'xmlns': 'a'})
        x = w.append('x', {'xmlns:b': 'b'})
        y = x.append('y')
        z = y.append('z', {'b:val': 5})
        
        z.detach()
        
        self.assertEquals('a', z['xmlns'])
        self.assertEquals('b', z.lookup_prefix('b'))
        self.assertEquals('b', z.find_ns('b'))      
        
    def test_detachRemovesElementFromParentsChildren(self):
        x = Element('x')
        y = x.append('y')
        
        y.detach()
        self.assertEquals([], x.children)
    
    def test_appendElementWithParent(self):
        x = Element('x')
        y = x.append('y')
        
        x2 = Element('x')
        y2 = x2.append('y')
        
        x2.append(y)

        self.assertEquals('<x />', repr(x))
        self.assertEquals('<x><y /><y /></x>', repr(x2))
        
    def test_returnNodeListKeyword(self):
        x = Element('x')
        y = x.append('y')
        z = y.append('z')
        
        self.assertEquals(z, x('//z'))        
        self.assertEquals((z,), x('//z', return_nodelist=True))        