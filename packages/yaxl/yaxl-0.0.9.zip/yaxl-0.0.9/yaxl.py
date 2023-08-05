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

class XPathMixin:
	def __getRootElement(self):
		if self.parent:
			return self.parent.__getRootElement()
		else:
			return self
	
	def __formatRetval(self, retval):
		if len(retval) == 1:
			return retval[0]
		elif len(retval) > 1:
			return tuple(retval)
		else:
			return None			
	
	def __selectAlongChildAxis(self, nodeTest):
		return self.__formatRetval([x for x in self.children if x.qname == nodeTest])
	
	def __selectAlongAttributeAxis(self, nodeTest):
		if self.attributes.has_key(nodeTest):
			return self[nodeTest]
	
	def __selectAlongDescendantAxis(self, nodeTest):
		dlist = []
						
		def findMatchingNodes(x):
			for y in x.children:
				if y.qname == nodeTest:
					dlist.append(y)
				findMatchingNodes(y)

		findMatchingNodes(self)

		return self.__formatRetval(dlist)
		
	def __selectAlongDescendantOrSelfAxis(self, nodeTest):
		dlist = []
										
		def findMatchingNodes(x):
			for y in x.children:
				if nodeTest in ('*', y.qname):
					dlist.append(y)
				findMatchingNodes(y)

		findMatchingNodes(self)

		if nodeTest == self.qname:
			dlist.append(self)

		return self.__formatRetval(dlist)
	
	def select(self, xpath):		
		xpath = xpath.replace('//', '/descendant::')
		
		if xpath == '/':
			return self.__getRootElement()
		elif xpath.startswith('/'):
			return self.__getRootElement().select(xpath[1:])
				
		locationStep = None
		rest = None
		result = None
		predicates = []
		
		if '/' in xpath:
			xpathParts = xpath.split('/')
			locationStep, rest = xpathParts[0], '/'.join(xpathParts[1:])
		else:
			locationStep = xpath
		
		if '[' in locationStep:
			lStepParts = locationStep.split('[')
			predicates.append(lStepParts[1][:-1])
			locationStep = lStepParts[0]
		
		if '::' in locationStep:
			lsParts = locationStep.split('::')
			
			axis = lsParts[0]
			nodeTest = lsParts[1]
			
			if axis == 'child':
				result = self.__selectAlongChildAxis(nodeTest)
			elif axis == 'descendant':
				result = self.__selectAlongDescendantAxis(nodeTest)
			elif axis in ('parent', 'ancestor'):
				if self.parent and nodeTest in ('*', self.parent.qname):
					result =  self.parent
			elif axis == 'attribute':
				result = self.__selectAlongAttributeAxis(nodeTest)
			elif axis == 'self':
				if nodeTest in ('*', self.qname):
					result =  self
			elif axis == 'descendant-or-self':
				result = self.__selectAlongDescendantOrSelfAxis(nodeTest)
			elif axis == 'ancestor-or-self':
				dlist = []
				
				def findMatchingNodes(x):
					if x.qname == nodeTest:
						dlist.append(x)
						
					if x.parent:
						findMatchingNodes(x.parent)
				
				findMatchingNodes(self)
				
				result =  self.__formatRetval(dlist)
		elif locationStep[0] == '@':
			result = self.__selectAlongAttributeAxis(locationStep[1:])
		elif locationStep == '..':
			result = self.parent
		elif locationStep == '.':
			result = self
		else:
			result = self.__selectAlongChildAxis(locationStep)		
		
		"""
		if isinstance(result, tuple) and len(predicates) > 1:			
			r = []
			
			for x in result:
				print 'testing %s' % x
				for y in x.children:
					if y.qname == predicates[0]:
						r.append(x)
						
			result = self.__formatRetval(r)
		"""
		
		if result and predicates:
			if isinstance(result, tuple):
				result = self.__formatRetval([x for x in result if x(predicates[0]) is not None])
			
		if result and rest:
			r = []
			
			if isinstance(result, tuple):
				for n in result:					
					xx = n(rest)					
					
					if isinstance(xx, tuple):
						for x in xx:
							r.append(x)
					elif xx:
						r.append(xx)
			elif isinstance(result, Element):
				return result(rest)
					
			return self.__formatRetval(r)
		else:
			return result
				
	def __call__(self, xpath):
		return self.select(xpath)

class Element(object, XPathMixin):
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
		
		self.namespaces = {'xml': 'http://www.w3.org/XML/1998/namespace'}
		self.namespaces.update(namespaces)
		
		if attributes:
			_attributes = [x for x in attributes.items() if not x[0].startswith('xmlns:')]
			_namespaces = [x for x in attributes.items() if x[0].startswith('xmlns')]
			
			for aname, avalue in _namespaces:				
				self[aname] = avalue
				
			for aname, avalue in _attributes:
				self[aname] = avalue
				
		if ':' in qname and not self.find_ns(qname.split(':')[0]):
			raise UndeclaredNamespaceException(qname.split(':')[0])
		
	def map(self, prefix, uri):
		"""Binds the supplied namespace prefix to the supplied URI.
		
		Any namespaces used in an element or its sub-elements must
		be bound before use.
		"""
		
		self.namespaces[prefix] = uri
	
	def __remap(self, old_prefix, new_prefix):
		"""Recursively re-binds all attributes and sub-elements that were bound to
		old_prefix to new_prefix."""
		
		if self.find_ns(old_prefix) == self.find_ns(new_prefix):
			for aname, avalue in self.attributes.items()[:]:
				if aname.startswith('%s:' % old_prefix):
					self.attributes['%s:%s' % (new_prefix, aname.split(':')[1])] = avalue
					del self.attributes[aname]

			if self.qname.startswith('%s:' % old_prefix):
				self.qname = '%s:%s' % (new_prefix, self.qname.split(':')[1])
	
		for child in self.children:
			child.__remap(old_prefix, new_prefix)
	
	def __iadd__(self, value):
		"""Appends the supplied value to this element as a `text` node.
		"""
		self.text += value
		return self
	
	def __iter__(self):
		return iter([x for x in self.children])
	
	def __getitem__(self, name):
		"""Returns the value of the named attribute of this element.
		
		The attribute name may contain a namespace but the prefix
		used must be bound in this element or one of its ancestors.
		This method raises an exception if an undeclared namespace
		is used.
		
		This method also gets called when you use a list-style access
		to this element's children. In this case it is called with an
		index into the list of children.
		"""
		
		if isinstance(name, int):
			childPosition = name
			return self.children[childPosition]
		
		if ':' in name:
			ns, localname = name.split(':')
		else:
			ns = ''
			localname = name
			
		if name.startswith('xmlns:'):
			# lookup namespace mapping
			_ns = self.find_ns(localname)
			
			if not _ns:
				raise UndeclaredNamespaceException(ns)
			else:
				return _ns
			
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
			
			if ns == 'xmlns':
				self.namespaces[localname] = value
				return
				
			if not self.find_ns(ns):
				raise UndeclaredNamespaceException('%s was not declared prior to use with localname %s' % (ns, localname))
		
		self.attributes[name] = str(value)		
	
	def __nodes_bound(self, ns_prefix):
		x = len([x for x in self.attributes.items() if x[0].startswith('%s:' % ns_prefix)])
		
		if self.qname.startswith('%s:' % ns_prefix):
			x += 1
			
		return x
	
	def __unmap_namespace(self, ns_prefix):
		"""Unmaps the supplied prefix from this element if the corresponding
		URI is bound in an ancestor.
		
		This method raises a `NamespaceNotDeletableException` if the namespace of the supplied
		prefix is not bound in an ancestor and there are child elements or attributes that
		are bound to the namespace.
		"""
		
		if self.namespaces.has_key(ns_prefix):				
			ns_uri = self.namespaces[ns_prefix]

			parentHasPrefixBound = self.parent and self.parent.find_ns(ns_prefix) == ns_uri
			parentHasURIBound = self.parent and self.parent.lookup_prefix(ns_uri)
			parentHasNamespaceBound = parentHasPrefixBound or parentHasURIBound
			
			if not parentHasNamespaceBound and self.__nodes_bound(ns_prefix) > 0:
				raise NamespaceNotDeletableException(self.find_ns(ns_prefix))

			if parentHasNamespaceBound and not parentHasPrefixBound:				
				self.__remap(ns_prefix, self.parent.lookup_prefix(ns_uri))

		del self.namespaces[ns_prefix]
	
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
			self.__unmap_namespace(name.split(':')[1])
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
			
		if self.parent:
			return self.parent.find_ns(prefix)
			
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
	
	def append(self, qname, attributes=None, text=None, namespaces={}):
		"""Returns a new child of this element.
		
		The child is created with the supplied QName, attributes and text.
		It is also passed this element as a parent. The child created is
		returned so you can chain calls to this method.
		
		This method raises an exception if the QName contains an un-declared
		namespace prefix.
		"""
		"""
		if ':' in qname:
			xmlns, localname = qname.split(':')
			
			if xmlns not in self.namespaces.keys():
				raise UndeclaredNamespaceException('%s was not declared prior to use' % xmlns)
		"""
		elem = Element(qname, attributes, namespaces=namespaces, _parent=self)
		self.children.append(elem)
		
		if text:
			elem.text = text
		
		return elem
	
	def write(self, f):
		"""Writes out this element to file-like objects or any object with
		a `write` method.
		"""
		
		f.write('<%s' % self.qname)

		for namespace in [x for x in self.namespaces.items() if x[0] != 'xml']:
			if namespace[0]:
				f.write(' xmlns:%s="%s"' % namespace)
			else:
				f.write(' xmlns="%s"' % namespace[1])
			
		for attribute in self.attributes.items():
			f.write(' %s="%s"' % attribute)

		if len(self.children) == 0 and not self.text:
			f.write(' />')		
		else:
			f.write('>')
			
			if self.text:
				f.write(str(self.text))

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
		
		if not isinstance(elem, Element):
			return False
		
		if elem.qname != self.qname:			
			return False
			
		for n, v in self.attributes.items():
			if not elem.attributes.has_key(n) or not elem[n] == v:				
				return False
		
		if elem.children != self.children:			
			return False
			
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
		#del self.namespaces[prefix]
		pass
	
	def characters(self, content):
		if self.elem:
			self.elem.text = content.strip()
	
	def __parseQNameFromName(self, name):
		ns = [x for x in self.namespaces.items() if x[1] == name[0]]
					
		if len(ns) > 0:
			ns = ns[0][0]
		else:
			ns = None

		if ns:
			qname = '%s:%s' % (ns, name[1])
		else:
			qname = name[1]
			
		return qname
	
	def startElementNS(self, name, qname, attrs):
		if not qname:
			qname = self.__parseQNameFromName(name)
		
		if self.elem:
			elem = self.elem.append(qname, namespaces=self.namespaces)
		else:
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
			self.elem = elem
			
	def endElementNS(self, name, qname):
		if self.elem:
			self.elem = self.elem.parent
			
	def fatalError(self, exc):
		raise exc		

def parse(xml):
	"""Returns a hierarchy of Element objects parsed from
	the supplied XML source.
	
	The XML source can be a full document or any well-formed
	XML fragment.
	
	In addition, the `xml` parameter can be a file path, a string, a file-like object
	or a URL.
	"""
	
	from xml.sax.handler import feature_namespaces, feature_namespace_prefixes
	from xml.sax import make_parser, SAXNotSupportedException, SAXNotRecognizedException
	
	import urllib

	builder = __XMLBuilder()

	parser = make_parser()
	
	# Perform namespace processing
	parser.setFeature(feature_namespaces, True)
	
	# Report original prefixed names (i.e. qname is passed to startElementNS)
	# if not possible, we have fallback code anyway
	try:
		parser.setFeature(feature_namespace_prefixes, True)
	except SAXNotSupportedException:
		pass
	except SAXNotRecognizedException:
		pass
	
	parser.setContentHandler(builder)
	parser.setErrorHandler(builder)

	if not hasattr(xml, 'read'):		
		try:
			xml = open(xml)
		except:
			#print 'Could not find a file called %s' % xml
			try:
				xml = urllib.urlopen(xml)
			except:
				#print 'Could not find a URL called %s' % xml				
				xml = _StringIO(xml)
	
	parser.parse(xml)
	
	return builder.tree