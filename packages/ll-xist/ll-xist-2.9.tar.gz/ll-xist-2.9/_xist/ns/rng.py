#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-

## Copyright 1999-2004 by LivingLogic AG, Bayreuth, Germany.
## Copyright 1999-2004 by Walter Dörwald
##
## All Rights Reserved
##
## See xist/__init__.py for the license

"""
<par>An &xist; namespace that contains definitions the
<link href="http://www.relaxng.org/">RELAX NG</link> definition.</par>
"""

__version__ = tuple(map(int, "$Revision: 2.63 $"[11:-2].split(".")))
# $Source: /data/cvsroot/LivingLogic/xist/_xist/ns/html.py,v $

from ll.xist import xsc, sims


class CommonAttrs(xsc.Element.Attrs):
	class ns(xsc.TextAttr): pass
	class datatypeLibrary(xsc.URLAttr): pass


class __ns__(xsc.Namespace):
	xmlname = "rng"
	xmlurl = "http://relaxng.org/ns/structure/1.0"
__ns__.makemod(vars())
