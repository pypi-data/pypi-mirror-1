#! /usr/bin/env/python
# -*- coding: iso-8859-1 -*-

## Copyright 1999-2005 by LivingLogic AG, Bayreuth/Germany.
## Copyright 1999-2005 by Walter D�rwald
##
## All Rights Reserved
##
## See xist/__init__.py for the license


from ll.xist import xsc
from ll.xist.ns import html


def test_mapped():
	def maplang(node, converter):
		if isinstance(node, xsc.Text):
			node = node.replace("lang", converter.lang)
		return node

	node = xsc.Frag(
		"lang",
		html.div(
			"lang",
			class_="lang",
		)
	)
	node2 = node.mapped(maplang, lang="en")
	assert node == xsc.Frag(
		"lang",
		html.div(
			"lang",
			class_="lang",
		)
	)
	assert node2 == xsc.Frag(
		"en",
		html.div(
			"en",
			class_="lang", # No replacement in attributes
		)
	)
