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

from xpathlib import XPathMixin

##############################################################################################
##############################################################################################
################################### E l e m e n t ############################################
##############################################################################################
##############################################################################################


class Element(object, XPathMixin):
	"""An XML element.	
	
	"""
				
	def __getattr__(self, name):
		if name == 'qname':
			if self.ns:
				return '%s:%s' % (self.ns, self.localname)			
			else:
				return self.localname
	
	def __setattr__(self, name, value):
		if name == 'qname':
			raise TypeError('read-only attribute')
		elif name == 'text':
			if value:
				self.__dict__[name] = unicode(value)
			else:
				self.__dict__[name] = ''
		else:
			self.__dict__[name] = value
	
	def __init__(self, qname, attributes=None, text=None, namespaces=None, _parent=None):
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
		
		if ':' in qname:
			self.ns, self.localname = qname.split(':')
		else:
			self.ns, self.localname = (None, qname)
		
		if text:
			self.text = str(text)
		else:
			self.text = ''
			
		self.children = []		
		self.attributes = {}		
		
		self.namespaces = {'xml': 'http://www.w3.org/XML/1998/namespace'}
		
		if namespaces:
			self.namespaces.update(namespaces)
		
		if attributes:
			_attributes = [x for x in attributes.items() if not x[0].startswith('xmlns')]
			_namespaces = [x for x in attributes.items() if x[0].startswith('xmlns')]
			
			# Do namespaces first so that we can add attributes in them after
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
				self.ns = new_prefix
	
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
		elif name == 'xmlns':
			if self.ns:
				return self.ns
			elif self.parent:
				return self.parent['xmlns']
			
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
		elif name == 'xmlns':			
			self.ns = self.lookup_prefix(value)			
		
		self.attributes[name] = unicode(value).encode('utf8')
	
	def __nodes_bound(self, ns_prefix, include_children = False):
		"""Returns the number of nodes (children or attributes) that are
		bound to the supplied namespace prefix.
		
		If `include_children` is `True` then children are checked recursively.
		"""
		
		x = len([x for x in self.attributes.items() if x[0].startswith('%s:' % ns_prefix)])
		
		if self.ns == ns_prefix:
			x += 1
		
		if include_children:
			for child in self.children:
				x += child.__nodes_bound(ns_prefix)
		
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
		
	def detach(self):
		"""Detaches this element from its parent.
		
		This method performs appropriate cleanup on namespaces
		inherited from its parent or other ancestors.
		"""
		
		if self.parent:
			def findDefaultNamespace(x):
				if x.attributes.has_key('xmlns'):
					return x['xmlns']
				elif not x.parent:
					return None
				else:
					return findDefaultNamespace(x.parent)

			defaultNamespace = findDefaultNamespace(self)

			if defaultNamespace:			
				self['xmlns'] = defaultNamespace
				
			self.parent.children.remove(self)
			self.parent = None		
	
	def append(self, qnameOrElement, attributes=None, text=None, namespaces=None):
		"""Appends child to this element.
		
		If the first parameter is an instance of `Element`, this method adds
		the element as a child of this one. Note that this method calls `detach` before
		adding the supplied element as a child.
		
		If the first parameter is a string, a new element is created and added
		as a child of this element.
		
		The added child is returned so you can chain calls to this method.
		
		This method raises an exception if the QName contains an un-declared
		namespace prefix.
		"""
		"""
		child has parent and needs it for namespace mapping		
		"""
		
		if namespaces is None:
			namespaces = {}
		
		namespaces.update(self.namespaces)
		
		if isinstance(qnameOrElement, Element):
			qnameOrElement.detach()
			self.children.append(qnameOrElement)
			elem = qnameOrElement
		else:
			elem = Element(qnameOrElement, attributes, namespaces=namespaces, text=text, _parent=self)
			self.children.append(elem)
		
		return elem
	
	def write(self, f, encoding='UTF8'):
		"""Writes out this element to file-like objects or any object with
		a `write` method.
		"""
		
		f.write('<%s' % self.qname)

		for namespace in [x for x in self.namespaces.items() if x[0] != 'xml']:			
			if namespace[0]:
				if not (self.parent and self.parent.find_ns(namespace[0])) and self.__nodes_bound(namespace[0], include_children=True) > 0:
					f.write(' xmlns:%s="%s"' % namespace)				
			else:
				f.write(' xmlns="%s"' % namespace[1])
			
		for name, value in [(x[0], x[1]) for x in self.attributes.items()]:			
			f.write((' %s="%s"' % (name, value.decode(encoding))).encode(encoding))

		if len(self.children) == 0 and not self.text:
			f.write(' />')		
		else:
			f.write('>')
			
			if self.text:
				text = unicode(self.text)
				
				if encoding:
					text = text.encode(encoding)
					
				f.write(text)

			for child in self.children:				
				child.write(f, encoding)

			f.write('</%s>' % self.qname)
	
	def __str__(self):
		"""Returns the string-value of this element: the concatenation of
		this element's `text` property and the string-value of its children.
		"""
		
		return self.text
	
	def __repr__(self, asdoc=False, encoding='UTF8'):
		"""Returns an XML representation of this element.
		
		By default the XML returned is not a valid document. If the `asdoc` parameter
		supplied is true then the representation is prefaced with an XML version
		processing instruction so that a valid document is returned.
		
		If the `encoding` parameter is supplied, it will be used as the encoding
		for the XML document returned.
		"""
		
		f = _StringIO()
		self.write(f, encoding)
		xmlstring = f.getvalue().strip()
		r = '%s'
		
		if asdoc:
			r = '<?xml version="1.0" encoding="%s"?>%%s' % encoding
			
		return r % xmlstring
	
	def asdoc(self, encoding='UTF8'):
		"""Returns an XML document representing this element.
		
		This is a conveniance method that calls `self.__repr__(True)`.
		"""
		return self.__repr__(True, encoding)
	
	def __eq__(self, elem):
		"""Returns `True` if `elem` is the same as this element.
		
		Equality is based on the QName, attributes and children of the elements.
		Order of elements and attributes is not taken into account.
		"""
		
		if not isinstance(elem, Element):
			return False
		
		if elem.find_ns(elem.ns) != self.find_ns(self.ns) or elem.localname != self.localname:
			#print 'NS or localname do not match: %s %s\n%s\n%s' % ((elem.ns, self.ns), (elem.localname, self.localname), elem, self)
			return False
			
		for n, v in self.attributes.items():
			if not elem.attributes.has_key(n) or not elem[n] == v:
				#print 'Children do not match'
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
		import re
		
		if self.elem:
			if self.elem.text:
				self.elem.text = re.sub(r'\s+', ' ', '%s%s' % (self.elem.text, content))
			else:
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
