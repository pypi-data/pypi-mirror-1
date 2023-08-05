# YAXL #
## Yet Another (Pythonic) XML Library ##

[YAXL](http://www.ilowe.net/software/yaxl) is a library for reading, writing and manipulating XML in [Python](http://www.python.org/).

## Download ##

You can download the latest version of YAXL from the [distribution archive](dist).

Check out YAXL's [page at the cheeseshop](http://cheeseshop.python.org/pypi/yaxl).

I also publish YAXL in the following formats:
	
	* [Python Egg](dist/yaxl-0.0.7-py2.4.egg) for use with [setuptools](http://peak.telecommunity.com/DevCenter/setuptools)
	* [Source distribution](dist/yaxl-0.0.7.zip) if you want to hack around

### Usage ###

It's pretty easy to use the library. Some basic tips are in order...

#### Reading XML

Use the `parse` function to obtain a hierarchy of `Element` instances. The method accepts a file path, a file-like object, a URL or a string. It can also handle both full documents and well-formed XML fragments.

#### Creating new elements

You can create new elements by using the `Element` constructor or the `append` method of an existing `Element` instance. Both accept and name for the element (which may contain a properly bound namespace prefix), a `dict` of attributes (all non-string values are converted to strings) and a `text` parameter that sets the text node contents of the element being created. Both return the newly created element so you can chain calls to them.

Note that trying to create a new element whose qname uses an unbound namespace prefix will raise an `Exception`.

#### Locating elements

Locate elements by navigating the `children` property of elements or by using the XPath `select` method. As a convenience, you may "call" an element with an XPath and it has the same effect as the `select` method.

#### Manipulating attributes

You can access all of an element's attributes via the `attributes` property of the element. This `dict` includes the namespaces that are currently bound to URIs.

Note that trying to modify an attribute whose qname uses an unbound namespace prefix will raise an `Exception`.

#### Mapping namespace prefixes

To map a new namespace in an element, set an `xmlns:*` attribute to the URI to which the prefix should be bound. To bind the default namespace to a URI set the `xmlns` attribute. By default, the `xmlns` attribute is unset and the `xml` prefix is mapped to [http://www.w3.org/XML/1998/namespace](http://www.w3.org/XML/1998/namespace).

### Requirements ###

Here's the list of things I really wanted to support:

    * Simplest interface possible - minimal number of functions and objects exported
    * Learnable in 15 minutes
	* Namespace aware
	* XPathish support
	* Easy to create XML
	* Easy to read in and manipulate XML

### Future Enhancements ###

	* The namespace interface is a bit weird right now. The interface is split between a nice `xmlns:ns` attribute interface and `Element.namespaces`. This needs to be cleaned up a bit. For now, stick to using the attribute-style interface - the other one might go away.
	* Play nice with default namespaces (which are not handled properly right now).
	* XPath support needs to be improved (add remaining axes and handle predicates and functions)

### Changes ###

    * (2005-10-06) Fixed a bug when QName is `None` when the SAX parser calls `startElementNS` - now the `feature_namespace_prefixes` feature is explicitly enabled and the XML builder has some fallback code that parses the QName properly from the namespace and the element name by searching current namespace mappings
	* (2005-10-06) Added abbreviated syntax for all supported axes, added existance predicate (select this node if it has a child named such-and-such or an attribute named such-and-such)
	* (2005-10-05) Added support for unabbreviated XPath location steps for `child`, `descendant`, `parent`, `self`, `ancestor`, `attribute`, `descendant-or-self`, `ancestor-or-self`	

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

	* Aaron Swartz's [xmltramp](http://www.aaronsw.com/2002/xmltramp/)
	* Frederik Lundh's excellent [ElementTree](http://effbot.org/zone/element-index.htm)
	* Philippe Normand's [EaseXML](http://easexml.base-art.net/)
	* Fourthought Inc's [4suite](http://4suite.org)

### Contact ###

You can reach me at [ilowe@cryogen.com](mailto:ilowe@cryogen.com) with feedback.

### Terms of use ###

If you care, this software is Copyright (C) 2005 by Iain Lowe and is released
under the terms of the MIT License.