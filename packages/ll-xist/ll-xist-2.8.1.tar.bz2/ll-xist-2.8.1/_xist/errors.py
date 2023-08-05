#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-

## Copyright 1999-2004 by LivingLogic AG, Bayreuth, Germany.
## Copyright 1999-2004 by Walter D�rwald
##
## All Rights Reserved
##
## See xist/__init__.py for the license

"""
<par>This module contains all the exception classes of &xist;.
But note that &xist; will raise other exceptions as well.</par>

<par>All exceptions defined in this module are derived from
the base class <pyref class="Error"><class>Error</class></pyref>.</par>
"""

__version__ = tuple(map(int, "$Revision: 2.54 $"[11:-2].split(".")))
# $Source: /data/cvsroot/LivingLogic/xist/_xist/Attic/errors.py,v $

import types, warnings

from xml.sax import saxlib

import presenters


class Error(Exception):
	"""
	base class for all &xist; exceptions
	"""
	pass


class Warning(UserWarning):
	"""
	base class for all warning exceptions (i.e. those that won't
	result in a program termination.)
	"""
	pass


class IllegalAttrError(Warning, LookupError):
	"""
	exception that is raised, when an element has an illegal attribute
	(i.e. one that isn't defined in the appropriate attributes class)
	"""

	def __init__(self, attrs, attrname, xml=False):
		self.attrs = attrs
		self.attrname = attrname
		self.xml = xml

	def __str__(self):
		if self.attrs is not None:
			return "Attribute with %s name %r not allowed for %s" % (("Python", "XML")[self.xml], self.attrname, self.attrs._str(fullname=True, xml=False, decorate=False))
		else:
			return "Global attribute with %s name %r not allowed" % (("Python", "XML")[self.xml], self.attrname)


class IllegalAttrValueWarning(Warning):
	"""
	warning that is issued when an attribute has an illegal value when parsing or publishing.
	"""

	def __init__(self, attr):
		self.attr = attr

	def __str__(self):
		attr = self.attr
		return "Attribute value %r not allowed for %s. " % (str(attr), attr._str(fullname=True, xml=False, decorate=False))


class RequiredAttrMissingWarning(Warning):
	"""
	warning that is issued when a required attribute is missing during parsing or publishing.
	"""

	def __init__(self, attrs, reqattrs):
		self.attrs = attrs
		self.reqattrs = reqattrs

	def __str__(self):
		v = ["Required attribute"]
		if len(self.reqattrs)>1:
			v.append("s ")
			v.append(", ".join("%r" % attr for attr in self.reqattrs))
		else:
			v.append(" %r" % self.reqattrs[0])
		v.append(" missing in %s." % self.attrs._str(fullname=True, xml=False, decorate=False))
		return "".join(v)


class IllegalDTDChildWarning(Warning):
	"""
	warning that is issued when the <pyref module="ll.xist.parsers" class="HTMLParser"><class>HTMLParser</class></pyref>
	detects an element that is not allowed inside its parent element according to the &html; &dtd;
	"""

	def __init__(self, childname, parentname):
		self.childname = childname
		self.parentname = parentname

	def __str__(self):
		return "Element %s not allowed as a child of element %s" % (self.childname, self.parentname)


class IllegalCloseTagWarning(Warning):
	"""
	warning that is issued when the <pyref module="ll.xist.parsers" class="HTMLParser"><class>HTMLParser</class></pyref>
	finds an end tag that has no corresponding start tag.
	"""

	def __init__(self, name):
		self.name = name

	def __str__(self):
		return "Element %s has never been opened" % (self.name,)


class IllegalPrefixError(Error, LookupError):
	"""
	Exception that is raised when a namespace prefix is undefined.
	"""
	def __init__(self, prefix):
		self.prefix = prefix

	def __str__(self):
		return "namespace prefix %r is undefined" % self.prefix


class IllegalNamespaceError(Error, LookupError):
	"""
	Exception that is raised when a namespace name is undefined
	i.e. if there is no namespace with this name.
	"""
	def __init__(self, name):
		self.name = name

	def __str__(self):
		return "namespace name %r is undefined" % self.name


class IllegalNodeError(Error, LookupError):
	"""
	exception that is raised, when an illegal node class (element, procinst, entity or charref) is requested
	"""

	type = "node"

	def __init__(self, name, xml=False):
		self.name = name
		self.xml = xml

	def __str__(self):
		return "%s with %s name %r not allowed" % (self.type, ("Python", "XML")[self.xml], self.name, )


class IllegalElementError(IllegalNodeError):
	type = "element"


class IllegalProcInstError(IllegalNodeError):
	type = "procinst"


class IllegalEntityError(IllegalNodeError):
	type = "entity"


class IllegalCharRefError(IllegalNodeError):
	type = "charref"

	def __str__(self):
		if isinstance(self.name, (int, long)):
			return "%s with codepoint %s not allowed" % (self.type, self.name)
		else:
			return IllegalNodeError.__str__(self)


class AmbiguousNodeError(Error, LookupError):
	"""
	exception that is raised, when an node class is ambiguous (most commonly for processing instructions or entities)
	"""

	type = "node"

	def __init__(self, name, xml=False):
		self.name = name
		self.xml = xml

	def __str__(self):
		return "%s with %s name %r is ambigous" % (self.type, ("Python", "XML")[self.xml], self.name)


class AmbiguousProcInstError(AmbiguousNodeError):
	type = "procinst"


class AmbiguousEntityError(AmbiguousNodeError):
	type = "entity"


class AmbiguousCharRefError(AmbiguousNodeError):
	type = "charref"

	def __str__(self):
		if isinstance(self.name, (int, long)):
			return "%s with codepoint %r is ambigous" % (self.type, self.name)
		else:
			return AmbiguousNodeError.__str__(self)


class MultipleRootsError(Error):
	def __str__(self):
		return "can't add namespace attributes: XML tree has multiple roots"


class ElementNestingError(Error):
	"""
	exception that is raised, when an element has an illegal nesting
	(e.g. <lit>&lt;a&gt;&lt;b&gt;&lt;/a&gt;&lt;/b&gt;</lit>)
	"""

	def __init__(self, expectedelement, foundelement):
		self.expectedelement = expectedelement
		self.foundelement = foundelement

	def __str__(self):
		return "mismatched element nesting (close tag for %s expected; close tag for %s found)" % (self.expectedelement._str(fullname=1, xml=0, decorate=1), self.foundelement._str(fullname=1, xml=0, decorate=1))


class IllegalAttrNodeError(Error):
	"""
	exception that is raised, when something is found
	in an attribute that doesn't belong there (e.g. an element or a comment).
	"""

	def __init__(self, node):
		self.node = node

	def __str__(self):
		return "illegal node of type %s found inside attribute" % self.node.__class__.__name__


class NodeNotFoundError(Error):
	"""
	exception that is raised when <pyref module="ll.xist.xsc" class="Node" method="findfirst"><method>findfirst</method></pyref> fails.
	"""
	def __str__(self):
		return "no appropriate node found"


class FileNotFoundWarning(Warning):
	"""
	warning that is raised, when a file can't be found
	"""
	def __init__(self, message, filename, exc):
		Warning.__init__(self, message, filename, exc)
		self.message = message
		self.filename = filename
		self.exc = exc

	def __str__(self):
		return "%s: %r not found (%s)" % (self.message, self.filename, self.exc)


class IllegalObjectWarning(Warning):
	"""
	warning that is issued when &xist; finds an illegal object in its object tree.
	"""

	def __init__(self, object):
		self.object = object

	def __str__(self):
		s = "an illegal object %r of type %s" % (self.object, type(self.object).__name__)
		if type(self.object) is types.InstanceType:
			s += " (class %s)" % self.object.__class__.__name__
		s += " has been found in the XSC tree. The object will be ignored."
		return s


class MalformedCharRefWarning(Warning):
	"""
	exception that is raised when a character reference is malformed (e.g. <lit>&amp;#foo;</lit>)
	"""

	def __init__(self, name):
		self.name = name

	def __str__(self):
		return "malformed character reference: &%s;" % self.name


class IllegalCommentContentWarning(Warning):
	"""
	warning that is issued when there is an illegal comment, i.e. one
	containing <lit>--</lit> or ending in <lit>-</lit>.
	(This can only happen, when the comment is instantiated by the
	program, not when parsed from an &xml; file.)
	"""

	def __init__(self, comment):
		self.comment = comment

	def __str__(self):
		return "comment with content %s is illegal, as it contains '--' or ends in '-'." % presenters.strTextOutsideAttr(self.comment.content)


class IllegalProcInstFormatError(Error):
	"""
	exception that is raised, when there is an illegal processing instruction, i.e. one containing <lit>?&gt;</lit>.
	(This can only happen, when the processing instruction is instantiated by the
	program, not when parsed from an &xml; file.)
	"""

	def __init__(self, procinst):
		self.procinst = procinst

	def __str__(self):
		return "processing instruction with content %s is illegal, as it contains %r." % (presenters.strProcInstContent(self.procinst.content), "?>")


class IllegalXMLDeclFormatError(Error):
	"""
	exception that is raised, when there is an illegal XML declaration,
	i.e. there something wrong in <lit>&lt;?xml ...?&gt;</lit>.
	(This can only happen, when the processing instruction is instantiated by the
	program, not when parsed from an &xml; file.)
	"""

	def __init__(self, procinst):
		self.procinst = procinst

	def __str__(self):
		return "XML declaration with content %r is malformed." % presenters.strProcInstContent(self.procinst.content)


class ParseWarning(Warning):
	"""
	General warning issued during parsing.
	"""


class IllegalElementParseWarning(IllegalElementError, ParseWarning):
	"""
	Warning about an illegal element that is issued during parsing.
	"""
warnings.filterwarnings("error", category=IllegalElementParseWarning)


class IllegalProcInstParseWarning(IllegalProcInstError, ParseWarning):
	"""
	Warning about an illegal processing instruction that is issued during parsing.
	"""
warnings.filterwarnings("error", category=IllegalProcInstParseWarning)


class AmbiguousProcInstParseWarning(AmbiguousProcInstError, ParseWarning):
	"""
	Warning about an ambigous processing instruction that is issued during parsing.
	"""
warnings.filterwarnings("error", category=AmbiguousProcInstParseWarning)


class IllegalEntityParseWarning(IllegalEntityError, ParseWarning):
	"""
	Warning about an illegal entity that is issued during parsing.
	"""
warnings.filterwarnings("error", category=IllegalEntityParseWarning)


class AmbiguousEntityParseWarning(AmbiguousEntityError, ParseWarning):
	"""
	Warning about an ambigous entity that is issued during parsing.
	"""
warnings.filterwarnings("error", category=AmbiguousEntityParseWarning)


class IllegalCharRefParseWarning(IllegalCharRefError, ParseWarning):
	"""
	Warning about an illegal character references that is issued during parsing.
	"""
warnings.filterwarnings("error", category=IllegalCharRefParseWarning)


class AmbiguousCharRefParseWarning(AmbiguousCharRefError, ParseWarning):
	"""
	Warning about an ambigous character references that is issued during parsing.
	"""
warnings.filterwarnings("error", category=AmbiguousCharRefParseWarning)


class IllegalAttrParseWarning(IllegalAttrError, ParseWarning):
	"""
	Warning about an illegal attribute that is issued during parsing.
	"""
warnings.filterwarnings("error", category=IllegalAttrParseWarning)


class NodeOutsideContextError(Error):
	"""
	Error that is raised, when a convert method can't find required context
	info.
	"""

	def __init__(self, node, outerclass):
		self.node = node
		self.outerclass = outerclass

	def __str__(self):
		s = "node %s" % self.node._str(fullname=True, xml=False, decorate=True)
		if self.node.startloc is not None:
			s += " at %s" % self.node.startloc
		s += " outside of %r" % self.outerclass
		return s
