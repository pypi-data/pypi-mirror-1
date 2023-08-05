#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-

## Copyright 2005-2006 by LivingLogic AG, Bayreuth/Germany.
## Copyright 2005-2006 by Walter D�rwald
##
## All Rights Reserved
##
## See xist/__init__.py for the license

"""
This module is an &xist; namespace for
<link href="http://kid.lesscode.org/">Kid</link> files.
"""

__version__ = "$Revision: 1.1 $".split()[1]
# $Source: /data/cvsroot/LivingLogic/Python/xist/src/ll/xist/ns/kid.py,v $


from ll.xist import xsc, sims


class python(xsc.ProcInst):
	""" 
	The <class>python</class> processing instruction contains Python code.
	"""


class __ns__(xsc.Namespace):
	xmlname = "py"
	xmlurl = "http://purl.org/kid/ns#"

	class Attrs(xsc.Namespace.Attrs):
		"""
		Global attributes.
		"""
		class for_(xsc.TextAttr):
			"""
			The <class>for_</class> attribute may appear on any element to signify
			that the element should be processed multiple times, once for each
			value in the sequence specified.
			"""
			xmlname = "for"

		class if_(xsc.TextAttr):
			"""
			The <class>if_</class> attribute may appear on any element to signify
			that the element and its decendant items should be output only if the
			boolean expression specified evaluates to true in Python.
			"""
			xmlname = "if"

		class content(xsc.TextAttr):
			"""
			This attribute may appear on any element to signify that the decendant
			items of the element are to be replaced with the result of evaluating
			the attribute content as a Python expression.
			"""

		class replace(xsc.TextAttr):
			"""
			<class>replace</class> is shorthand for specifying a
			<class>content</class> and a <markup>strip="True"</markup>
			on the same element.
			"""
		class strip(xsc.TextAttr):
			"""
			The <class>strip</class> attribute may apppear on any element to
			signify that the containing element should not be output.
			"""
		class attrs(xsc.TextAttr):
			"""
			The <class>attrs</class> attribute may appear on any element to
			specify a set of attributes that should be set on the element
			when it is processed.
			"""
		class def_(xsc.TextAttr):
			"""
			The <class>def_</class> attribute may appear on any element to
			create a <z>Named Template Function</z>.
			"""
			xmlname = "def"
		class match(xsc.TextAttr):
			"""
			The <class>match</class> attribute may appear on any element to
			create a <z>Match Template</z>.
			"""
		class extends(xsc.TextAttr):
			"""
			The <class>extends</class> attribute may appear on the root element
			to specify that the template should inherit the Named Template Functions
			and Match Templates defined in another template (or set of templates).
			"""
__ns__.makemod(vars())
