# YAXL #
## Yet Another (Pythonic) XML Library v0.0.12 ##

[YAXL](http://www.ilowe.net/software/yaxl) is a library for reading, writing and manipulating [XML](http://www.w3.org/TR/REC-xml/) in [Python](http://www.python.org/).

## Download ##

You can download the latest version of YAXL from the [distribution archive](dist).

Check out YAXL's [page at the cheeseshop](http://cheeseshop.python.org/pypi/yaxl).

I also publish YAXL in the following formats:
	
	* [Python Egg](dist/yaxl-0.0.12-py2.4.egg) for use with [setuptools](http://peak.telecommunity.com/DevCenter/setuptools)
	* [Source distribution](dist/yaxl-0.0.12.zip) if you want to hack around

### Usage ###

Check out [Developing with YAXL](developing-with-yaxl.html) for more details. YAXL also comes with extensive online documentation. Use code like the following to access the module's built-in help:

	>>> import yaxl
	>>> help(yaxl)

### Requirements ###

Here's the list of things I really wanted:

	* Learnable in 15 minutes
    * Simplest interface possible - minimal number of functions and objects exported
	* [XML Namespace](http://www.w3.org/TR/REC-xml-names) aware
	* [XPath](http://www.w3.org/TR/xpath) support
	* Easy to create [XML](http://www.w3.org/TR/REC-xml/) documents and fragments
	* Easy to read in and manipulate [XML](http://www.w3.org/TR/REC-xml/) documents and fragments
	
Let me know at [ilowe@cryogen.com](mailto:ilowe@cryogen.com) whether or not I'm succeeding.

### Future Enhancements ###

	* XPath support needs to be improved (add `following`, `following-sibling`, `preceding`, `preceding-sibling` and `namespace` axes; handle functions)
	* Re-organize module to embed test suite so it can be run from the Python Egg distro

### Changes ###

    * (2005-10-10) Added `=`, `!=`, `>=`, `<=`, `<`, `>` and existance predicates for XPath	
    * (2005-10-10) Added automated testing of documentation examples
	* (2005-10-09) Basic encoding support added (read/write)
    * (2005-10-09) Modified internal module structure
	* (2005-10-08) Plays nice with default namespaces now
	* (2005-10-08) Unit test refactoring
	* (2005-10-08) Added sequence-style access for child nodes
	* (2005-10-08) Added modification-safe iterator support over children
	* (2005-10-08) Added namespace "re-mapping" - now handles the case where a namespace mapped in an ancestor is deleted properly
	* (2005-10-08) Tightened up constraints for `Element` equality
    * (2005-10-08) Cleanup in `find_ns`
    * (2005-10-08) Fixed `feature_namespace_prefixes` not handled by expat bug, 
    * (2005-10-06) Fixed a bug when QName is `None` when the SAX parser calls `startElementNS` - now the `feature_namespace_prefixes` feature is explicitly enabled and the XML builder has some fallback code that parses the QName properly from the namespace and the element name by searching current namespace mappings
	* (2005-10-06) Added abbreviated syntax for all supported axes, added existance predicate (select this node if it has a child named such-and-such or an attribute named such-and-such)
	* (2005-10-05) Added support for unabbreviated XPath location steps for `child`, `descendant`, `parent`, `self`, `ancestor`, `attribute`, `descendant-or-self`, `ancestor-or-self`	

### Aknowledgements

The following people have submitted bug reports or enhancement suggestions: Marc, "Crest" and Marcus Gnaﬂ. Thank you all for your contribution!

### Why another XML library? Especially for Python? ###

I looked around (even spent some time sifting through Uche Ogbuji's
[State of Python-XML in 2004](http://www.xml.com/pub/a/2004/10/13/py-xml.html) with its 74 projects)
and couldn't find anything I liked. The existing modules were all "un-Pythonic" (for some value of "Pythonic") or just didn't have the exact flavour I wanted. Whatever.

I know that most Pythonistas look down on XML a bit but you really
need to use it to get by in most web projects, especially those involving data formats.
So unless you want to spend hours hand-coding XML you are stuck painstakingly
struggling with SAX and DOM interfaces. This is also highlighted by the
over-abundance of XML processing/parsing/binding/etc. frameworks available for Python.

I opted for the time-honoured tradition of re-inventing the wheel. I built this library
mostly for use with [my Atom library](http://www.ilowe.net/software/atom/).

### Inspiration / Other Frameworks ###

I shamelessly spent hours poring over the following projects and ripping out all the
coolest features to create this one:

	* Frederik Lundh's [ElementTree](http://effbot.org/zone/element-index.htm) is what I consider to be the best all-around XML library out there
	* Aaron Swartz's [xmltramp](http://www.aaronsw.com/2002/xmltramp/) is the inspiration for the extreme simplicity of the YAXL interface
	* Philippe Normand's [EaseXML](http://easexml.base-art.net/) is more of a Python/XML mapping library than a pure XML manipulation library
	* Fourthought Inc's [4suite](http://4suite.org) is probably the most complete in terms of standards-compliant support for XML and XML-related technologies (DOM, RDF, XSLT, XInclude, XPointer, XLink, XPath, XUpdate, RELAX NG, and XML/SGML Catalogs)
	* [lxml](http://codespeak.net/lxml/) provides a Pythonic binding for the [libxml2](http://xmlsoft.org/) and [libxslt](http://xmlsoft.org/XSLT) libraries which were written in C for the [Gnome](http://www.gnome.org) project

### Contact ###

You can reach me at [ilowe@cryogen.com](mailto:ilowe@cryogen.com) with feedback.

### Terms of use ###

If you care, this software is Copyright (C) 2005 by Iain Lowe and is released
under the terms of the MIT License.