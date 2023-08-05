#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-

## Copyright 1999-2005 by LivingLogic AG, Bayreuth/Germany.
## Copyright 1999-2005 by Walter D�rwald
##
## All Rights Reserved
##
## See xist/__init__.py for the license

"""
<par>A module that allows you to embed &jsp; content as processing instructions.</par>
"""

__version__ = tuple(map(int, "$Revision: 2.40 $"[11:-2].split(".")))
# $Source: /data/cvsroot/LivingLogic/xist/_xist/ns/jsp.py,v $

import cgi # for parse_header

from ll.xist import xsc, sims


class directive(xsc.Element):
	model = sims.Empty()
	register = False # only serves as a base class

	def publish(self, publisher):
		publisher.write(u"<%@ ")
		self._publishname(publisher)
		self.attrs.publish(publisher)
		publisher.write(u"%>")


class scriptlet(xsc.ProcInst):
	"""
	will be published as <markup>&lt;% <rep>content</rep> %&gt;</markup>
	"""
	def publish(self, publisher):
		publisher.write(u"<% ")
		publisher.write(self.content)
		publisher.write(u" %>")


class expression(xsc.ProcInst):
	"""
	will be published as <markup>&lt;%= <rep>content</rep> %&gt;</markup>
	"""

	def publish(self, publisher):
		publisher.write(u"<%= ")
		publisher.write(self.content)
		publisher.write(u" %>")


class declaration(xsc.ProcInst):
	"""
	will be published as <markup>&lt;%! <rep>content</rep> %&gt;</markup>
	"""

	def publish(self, publisher):
		publisher.write(u"<%! ")
		publisher.write(self.content)
		publisher.write(u" %>")


class If(scriptlet):
	xmlname = "if"

	def convert(self, converter):
		return self.__ns__.scriptlet(u"if(", self.content, u"){")


class Else(scriptlet):
	xmlname = "else"

	def convert(self, converter):
		return self.__ns__.scriptlet(u"}else{")


class ElIf(scriptlet):
	xmlname = "elif"

	def convert(self, converter):
		return self.__ns__.scriptlet(u"}else if (", self.content, u"){")


class End(scriptlet):
	xmlname = "end"

	def convert(self, converter):
		return self.__ns__.scriptlet(u"}")


class block(xsc.Element):
	"""
	<par>This element embeds its content in <lit>{}</lit> brackets.</par>
	<par>Note that the content itself will not be turned into a scriptlet
	automatically but will be used as-is.</par>
	"""
	model = sims.Any()

	def convert(self, converter):
		e = xsc.Frag(
			self.__ns__.scriptlet(u"{"),
			self.content,
			self.__ns__.scriptlet(u"}")
		)
		return e.convert(converter)


class directive_include(directive):
	xmlname = "include"
	class Attrs(directive.Attrs):
		class file(xsc.TextAttr): pass


class directive_taglib(directive):
	xmlname = "taglib"
	class Attrs(directive.Attrs):
		class uri(xsc.TextAttr): pass
		class prefix(xsc.TextAttr): pass


class directive_page(directive):
	xmlname = "page"
	class Attrs(directive.Attrs):
		class language(xsc.TextAttr):
			values = ("java",)
		class extends(xsc.TextAttr): pass
		class import_(xsc.TextAttr): xmlname = "import"
		class session(xsc.TextAttr): values = (u"true", u"false")
		class buffer(xsc.TextAttr): pass
		class autoFlush(xsc.TextAttr): values = (u"true", u"false")
		class isThreadSafe(xsc.TextAttr): values = (u"true", u"false")
		class info(xsc.TextAttr): pass
		class errorPage(xsc.URLAttr): pass
		class contentType(xsc.TextAttr): pass
		class isErrorPage(xsc.TextAttr): values = (u"true", u"false")
		class pageEncoding(xsc.TextAttr): pass

	def publish(self, publisher):
		# Only a contentType attribute trigger the special code
		if u"contentType" not in self.attrs or self[u"contentType"].isfancy() or self[u"pageEncoding"].isfancy():
			super(directive_page, self).publish(publisher)
		else:
			(contenttype, options) = cgi.parse_header(unicode(self[u"contentType"]))
			pageencoding = unicode(self[u"pageEncoding"])
			if u"charset" in options and options[u"charset"] == pageencoding == publisher.encoding:
				super(directive_page, self).publish(publisher)
			else:
				options[u"charset"] = publisher.encoding
				node = self.__class__(
					self.attrs,
					contentType=(contenttype, u"; ", u"; ".join("%s=%s" % option for option in options.items())),
					pageEncoding=publisher.encoding
				)
				node.publish(publisher)


class __ns__(xsc.Namespace):
	xmlname = "jsp"
	xmlurl = "http://java.sun.com/JSP/Page"
__ns__.makemod(vars())
