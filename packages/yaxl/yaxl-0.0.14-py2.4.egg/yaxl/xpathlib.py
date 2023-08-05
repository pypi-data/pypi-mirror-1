import yaxl

class XPathMixin:
	def __getRootElement(self):
		if self.parent:
			return self.parent.__getRootElement()
		else:
			return self
	
	def __assertPredicate(self, node, predicate):
		if '!=' in predicate:
			x, y = predicate.split('!=')
			
			y = eval(y)
			r = node(x)

			if isinstance(r, yaxl.Element):
				r = r.text

			return r and str(r) != str(y)
		elif '>=' in predicate:
			x, y = predicate.split('>=')
									
			y = eval(y)
			r = node(x)

			if isinstance(r, yaxl.Element):
				r = r.text
						
			return int(r) >= int(y)
		elif '<=' in predicate:
			x, y = predicate.split('<=')
												
			y = eval(y)
			r = node(x)

			if isinstance(r, yaxl.Element):
				r = r.text
									
			return int(r) <= int(y)
		elif '=' in predicate:
			x, y = predicate.split('=')
			
			y = eval(y)			
			r = node(x)
			
			if isinstance(r, yaxl.Element):
				r = r.text
				return str(r) == str(y)			
			elif isinstance(r, tuple):
				return True			
			else:
				return str(r) == str(y)
		elif '<' in predicate:
			x, y = predicate.split('<')
			
			y = eval(y)
			r = node(x)
			
			if isinstance(r, yaxl.Element):
				r = r.text
				
			return str(r) < str(y)
		elif '>' in predicate:
			x, y = predicate.split('>')
						
			y = eval(y)
			r = node(x)

			if isinstance(r, yaxl.Element):
				r = r.text
			
			return int(r) > int(y)
		else:
			return node(predicate) is not None
	
	def __applyPredicates(self, nodeset, predicates):
		if not isinstance(nodeset, tuple):
			return self.__applyPredicates((nodeset,), predicates)
			
		for predicate in predicates:				
			nodeset = [x for x in nodeset if self.__assertPredicate(x, predicate)]
		
		return self.__formatRetval(nodeset)
	
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
			predicates = [x[:-1] for x in lStepParts[1:]]
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
		
		if result:
			result = self.__applyPredicates(result, predicates)
			
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
			elif isinstance(result, yaxl.Element):
				return result(rest)
					
			return self.__formatRetval(r)
		else:
			return result
				
	def __call__(self, xpath):
		return self.select(xpath)
