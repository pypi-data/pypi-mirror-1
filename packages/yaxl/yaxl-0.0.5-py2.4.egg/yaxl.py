"""Yet Another (Pythonic) XML Library

* Simplest interface possible - minimal number of functions and objects exported
* Learnable in 15 minutes
* Namespace aware
* XPathish support
* Easy to create XML
* Easy to read in and manipulate XML

yaxl is Copyright (C) 2005 by Iain Lowe and is released under the MIT License. Visit
http://www.ilowe.net/software/yaxl for the latest version.

"""

from xml.sax.handler import ContentHandler as _ContentHandler
from cStringIO import StringIO as _StringIO

class Element(object):
	"""An XML element.	
	
	"""
	
	def __init__(self, qname, attributes=None, namespaces={}, _parent=None):
		"""Create a new element with the supplied QName
		
		The attributes parameter, if supplied, should be a dict containing
		name/value mappings for this element's attributes. Attribute names
		may contain namespaces although those prefixes used must be either
		already bound to a URI or supplied in the namespaces parameter.
		
		The namespaces parameter, if supplied, should be a dict containing
		prefix/URI mappings that should be in effect for this element and
		for its children.
		
		The `_parent` parameter is supplied by the `append` method to link
		element's in a hierarchy. If you append elements directly to the
		children list (for some reason) you must create each element with
		a reference to its parent.
		"""
		
		self.parent = _parent
		self.qname = qname
		self.text = ''		
		self.children = []		
		self.attributes = {}
		
		self.namespaces = {}
		self.namespaces.update(namespaces)
		
		if attributes:
			_attributes = [x for x in attributes.items() if not x[0].startswith('xmlns:')]
			_namespaces = [x for x in attributes.items() if x[0].startswith('xmlns:')]			
			
			for aname, avalue in _namespaces:
				self[aname] = avalue
				
			for aname, avalue in _attributes:
				self[aname] = avalue
		
	def map(self, prefix, uri):
		"""Binds the supplied namespace prefix to the supplied URI.
		
		Any namespaces used in an element or its sub-elements must
		be bound before use.
		"""
		
		self.namespaces[prefix] = uri
	
	def __getitem__(self, name):
		"""Returns the value of the named attribute of this element.
		
		The attribute name may contain a namespace but the prefix
		used must be bound in this element or one of its ancestors.
		This method raises an exception if an undeclared namespace
		is used.
		"""
		
		if ':' in name:
			ns, localname = name.split(':')
		else:
			ns = ''
			localname = name
			
		if name.startswith('xmlns'):
			# lookup namespace mapping
			_ns = self.find_ns(localname)
			
			if not _ns:
				raise UndeclaredNamespaceException(ns)
			else:
				return _ns[1]
			
		return self.attributes[name]
	
	def __setitem__(self, name, value):
		"""Sets the value of the named attribute of this element.
		
		The attribute name may contain a namespace but the prefix
		used must be bound in this element or one of its ancestors.
		This method raises an exception if an undeclared namespace
		is used.
		"""
		
		if ':' in name:
			ns, localname = name.split(':')
			
			if not self.find_ns(ns) and ns != 'xmlns':
				raise UndeclaredNamespaceException('%s was not declared prior to use with localname %s' % (ns, localname))
			elif ns == 'xmlns':
				self.namespaces[localname] = value
				return
		
		self.attributes[name] = str(value)		
	
	def __delitem__(self, name):
		"""Removes the named attribute from this element.
		
		If the attribute named is a namespace and it cannot be deleted,
		this method raises an exception. If other attributes are in the
		namespace referenced, the namespace cannot be deleted.
		"""
		
		"""
		The attribute name may contain a namespace but the prefix
		used must be bound in this element or one of its ancestors.
		This method raises an exception if an undeclared namespace
		is used.
		"""
		
		if name.startswith('xmlns:'):
			k = name[len('xmlns:'):]			
			if len([x for x in self.attributes.items() if x[0].startswith('%s:' % k)]) > 0:			
				raise NamespaceNotDeletableException(name)
		
		if name.startswith('xmlns:'):
			ns, localname = name.split(':')
			
			if self.namespaces.has_key(localname):
				del self.namespaces[localname]			
		else:
			del self.attributes[name]
	
	def find_ns(self, prefix):
		"""Returns the URI bound to the supplied prefix or None if there is
		no binding for the prefix.
		
		If this element has the supplied prefix mapped its value is returned;
		otherwise, this element's ancestors are searched until the root of the
		tree is reached.		
		"""
		
		if self.namespaces.has_key(prefix):
			return self.namespaces[prefix]
		elif self.parent and not self.namespaces.has_key(prefix):
			return self.parent.find_ns(prefix)
		else:
			return None
	
	def lookup_prefix(self, uri):
		"""Returns the prefix bound to the supplied URI or None if there is
		no binding for the URI.
		
		If this element has a prefix bound to the supplied URI it is returned;
		otherwise, this element's ancestors are searched until the root of the
		tree is reached.
		"""
		
		for _p, _u in self.namespaces.items():
			if _u == uri:
				return _p
				
		if self.parent:
			return self.parent.lookup_prefix(uri)
		else:
			return None
	
	def append(self, qname, attributes=None, text=None):
		"""Returns a new child of this element.
		
		The child is created with the supplied QName, attributes and text.
		It is also passed this element as a parent. The child created is
		returned so you can chain calls to this method.
		
		This method raises an exception if the QName contains an un-declared
		namespace prefix.
		"""		
		if ':' in qname:
			xmlns, localname = qname.split(':')
			
			if xmlns not in self.namespaces.keys():
				raise UndeclaredNamespaceException('%s was not declared prior to use' % xmlns)
		
		elem = Element(qname, attributes, _parent=self)
		self.children.append(elem)
		
		if text:
			elem.text = text
		
		return elem
	
	def write(self, f):
		"""Writes out this element to file-like objects or any object with
		a `write` method.
		"""
		
		f.write('<%s' % self.qname)

		for namespace in self.namespaces.items():
			f.write(' xmlns:%s="%s"' % namespace)
			
		for attribute in self.attributes.items():
			f.write(' %s="%s"' % attribute)

		if len(self.children) == 0 and not self.text:
			f.write(' />')		
		else:
			f.write('>')
			
			if self.text:
				f.write(self.text)

			for child in self.children:				
				child.write(f)

			f.write('</%s>' % self.qname)
	
	def __repr__(self, asdoc=False):
		"""Returns an XML representation of this element.
		
		By default the XML returned is not a valid document. If the `asdoc` parameter
		supplied is true then the representation is prefaced with an XML version
		processing instruction so that a valid document is returned.
		"""
		
		f = _StringIO()
		self.write(f)
		xmlstring = f.getvalue().strip()
		r = '%s'
		
		if asdoc:
			r = '<?xml version="1.0"?>%s'
			
		return r % xmlstring			
	
	def asdoc(self):
		"""Returns an XML document representing this element.
		
		This is a conveniance method that calls `self.__repr__(True)`.
		"""
		return self.__repr__(True)
	
	def __eq__(self, elem):
		"""Returns `True` if `elem` is the same as this element.
		
		Equality is based on the QName, attributes and children of the elements.
		Order of elements and attributes is not taken into account.
		"""
		
		if elem.qname != self.qname:
			#print 'QNames did not match (%s != %s)' % (self.qname, elem.qname)
			return False
		elif elem.attributes != self.attributes:
			#print 'Attributes did not match (%s != %s)' % (self.attributes, elem.attributes)
			return False
		elif elem.children != self.children:
			#print 'Children did not match (%s != %s)' % (self.children, elem.children)
			return False
		else:
			return True
		
class UndeclaredNamespaceException(Exception):
	"""Raised when a prefix is used that is not bound to a URI
	"""
	
	def __init__(self, prefix):
		Exception.__init__(self, '%s was not bound to a URI before use' % prefix)

class NamespaceNotDeletableException(Exception):
	"""Raised when a namespace still has bindings in the current
	element or one of its descendants.
	"""
	
	def __init__(self, prefix):
		Exception.__init__(self, 'Could not delete namespace mapping to %s - some elements still belong to it' % prefix)

class __XMLBuilder(_ContentHandler):
	def __init__(self):		
		self.tree = None
		self.elem = None
		self.namespaces = {}
	
	def startPrefixMapping(self, prefix, uri):
		self.namespaces[prefix] = uri
		#print 'Started mapping %s to %s' % (prefix, uri)
		
	def endPrefixMapping(self, prefix):
		del self.namespaces[prefix]
	
	def startElementNS(self, name, qname, attrs):
		elem = Element(qname, namespaces=self.namespaces)
		
		for k,v in attrs.items():			
			ns, localname = k			
			
			if ns:
				p = elem.lookup_prefix(ns)
				elem['%s:%s' % (p, localname)] = v
			else:
				elem[localname] = v
		
		if not self.tree:
			self.tree = elem
			self.elem = elem
		else:
			self.elem.children.append(elem)

def parse(xml):
	"""Returns a hierarchy of Element objects parsed from
	the supplied XML source.
	
	The XML source can be a full document or any well-formed
	XML fragment.
	"""
	
	from xml.sax.handler import feature_namespaces
	from xml.sax import make_parser
	
	builder = __XMLBuilder()
	
	parser = make_parser()
	parser.setFeature(feature_namespaces, True)
	parser.setContentHandler(builder)
	parser.setErrorHandler(builder)
	
	f = _StringIO(xml)
	parser.parse(f)
	
	return builder.tree