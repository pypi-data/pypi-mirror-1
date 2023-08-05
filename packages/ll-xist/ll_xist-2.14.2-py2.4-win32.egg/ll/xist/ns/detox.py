#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-

## Copyright 1999-2006 by LivingLogic AG, Bayreuth/Germany.
## Copyright 1999-2006 by Walter D�rwald
##
## All Rights Reserved
##
## See xist/__init__.py for the license


'''
<par>This module is an &xist; namespace. It provides a simple template language
based on processing instructions embedded in &xml; or plain text.</par>

<par>The following example is a simple <z>Hello, World</z> type template:</par>

<prog><![CDATA[
from ll.xist.ns import detox

template = """
<?def helloworld(n=10)?>
	<?for i in xrange(n)?>
		Hello, World!
	<?endfor?>
<?enddef?>
"""

module = detox.xml2mod(template)

print "".join(module.helloworld())
]]></prog>
'''


__version__ = "$Revision: 1.1 $".split()[1]
# $Source: /data/cvsroot/LivingLogic/Python/xist/src/ll/xist/ns/detox.py,v $


import sys, os, datetime, new

from ll.xist import xsc


class expr(xsc.ProcInst):
	"""
	Embed the value of the expression 
	"""
	pass


class textexpr(xsc.ProcInst):
	pass


class attrexpr(xsc.ProcInst):
	pass


class code(xsc.ProcInst):
	"""
	<par>Embed the PI data literally in the generated code.</par>

	<par>For example <lit>&lt;?code foo = 42?&gt;</lit> will put the
	statement <lit>foo = 42</lit> into the generated Python source.</par>
	"""


class if_(xsc.ProcInst):
	"""
	<par>Starts an if block. An if block can contain zero or more
	<pyref class="elif_"><class>elif_</class></pyref> blocks, followed by zero
	or one <pyref class="else_"><class>else_</class></pyref> block and must
	be closed with an <pyref class="endif"><class>endif</class></pyref> PI.</par>

	<par>For example:</par>

	<prog><![CDATA[
	<?code import random?>
	<?code n = random.choice("123?")?>
	<?if n == "1"?>
		One
	<?elif n == "2"?>
		Two
	<?elif n == "3"?>
		Three
	<?else?>
		Something else
	<?endif?>
	]]></prog>
	"""
	xmlname = "if"


class elif_(xsc.ProcInst):
	"""
	Starts an elif block.
	"""
	xmlname = "elif"


class else_(xsc.ProcInst):
	"""
	Starts an else block.
	"""
	xmlname = "else"


class endif(xsc.ProcInst):
	"""
	Ends an <pyref class="if_">if block</pyref>.
	"""


class def_(xsc.ProcInst):
	"""
	<par>Start a function (or method) definition. A function definition must be
	closed with an <pyref class="enddef"><class>enddef</class></pyref> PI.</par>

	<par>Example:</par>

	<prog><![CDATA[
	<?def persontable(persons)?>
		<table>
			<tr>
				<th>first name</th>
				<th>last name</th>
			</tr>
			<?for person in persons?>
				<tr>
					<td><?textexpr person.firstname?></td>
					<td><?textexpr person.lastname?></td>
				</tr>
			<?endfor?>
		</table>
	<?enddef?>
	]]></prog>

	<par>If the generated function contains output (i.e. if there is text content
	or <pyref class="expr"><class>expr</class></pyref>,
	<pyref class="textexpr"><class>textexpr</class></pyref> or
	<pyref class="attrexpr"><class>attrexpr</class></pyref> PIs before the matching
	<pyref class="enddef"><class>enddef</class></pyref>) the generated function
	will be a generator function.</par>

	<par>Output outside of a function definition will be ignored.</par>
	"""
	xmlname = "def"


class enddef(xsc.ProcInst):
	"""
	<par>Ends a <pyref class="def_">function definition</pyref>.</par>
	"""


class class_(xsc.ProcInst):
	"""
	<par>Start a class definition. A class definition must be closed with an
	<pyref class="endclass"><class>endclass</class></pyref> PI.</par>

	<par>Example:</par>
	<prog><![CDATA[
	<?class mylist(list)?>
		<?def output(self)?>
			<ul>
				<?for item in self?>
					<li><?textexpr item?></li>
				<?endfor?>
			</ul>
		<?enddef?>
	<?endclass?>
	]]></prog>
	"""
	xmlname = "class"


class endclass(xsc.ProcInst):
	"""
	<par>Ends a <pyref class="class_">class definition</pyref>.</par>
	"""


class for_(xsc.ProcInst):
	"""
	<par>Start a <lit>for</lit> loop. A for loop must be closed with an
	<pyref class="endfor"><class>endfor</class></pyref> PI.</par>

	<par>For example:</par>
	<prog><![CDATA[
	<ul>
		<?for i in xrange(10)?>
			<li><?expr str(i)?></li>
		<?endfor?>
	</ul>
	]]></prog>
	"""
	xmlname = "for"


class endfor(xsc.ProcInst):
	"""
	<par>Ends a <pyref class="for_">for loop</pyref>.</par>
	"""


class while_(xsc.ProcInst):
	"""
	<par>Start a <lit>while</lit> loop. A while loop must be closed with an
	<pyref class="endwhile"><class>endwhile</class></pyref> PI.</par>

	<par>For example:</par>
	<prog><![CDATA[
	<?code i = 0?>
	<ul>
		<?while True?>
			<li><?expr str(i)?><?code i += 1?></li>
			<?code if i > 10: break?>
		<?endwhile?>
	</ul>
	]]></prog>
	"""
	xmlname = "while"


class endwhile(xsc.ProcInst):
	"""
	<par>Ends a <pyref class="while_">while loop</pyref>.</par>
	"""


# Used for indenting Python source code
indent = "\t"


@classmethod
def xml2py(cls, source):
	stack = []
	stackoutput = [] # stack containing only True for def and False for class

	lines = [
		"# generated by %s %s on %s UTC" % (__file__, __version__, datetime.datetime.utcnow()),
		"",
		"from ll.xist.helpers import escapetext as __detox_escapetext__, escapeattr as __detox_escapeattr__",
		"",
	]

	def endscope(action):
		if not stack:
			raise SyntaxError("can't end %s scope: no active scope" % action._str(fullname=True, xml=False, decorate=False))
		if not issubclass(stack[-1][0], action):
			raise SyntaxError("can't end %s scope: active scope is: %s %s" % (action._str(fullname=True, xml=False, decorate=False), stack[-1][0]._str(fullname=True, xml=False, decorate=False), stack[-1][1]))
		stack.pop(-1)

	for (t, s) in cls.tokenize(source):
		if t is unicode:
			# ignore output outside of functions
			if stackoutput and stackoutput[-1]:
				lines.append("%syield %r" % (len(stack)*cls.indent, s))
		elif issubclass(t, expr):
			# ignore output outside of functions
			if stackoutput and stackoutput[-1]:
				lines.append("%syield %s" % (len(stack)*cls.indent, s))
		elif issubclass(t, textexpr):
			# ignore output outside of functions
			if stackoutput and stackoutput[-1]:
				lines.append("%syield __detox_escapetext__(%s)" % (len(stack)*cls.indent, s))
		elif issubclass(t, attrexpr):
			# ignore output outside of functions
			if stackoutput and stackoutput[-1]:
				lines.append("%syield __detox_escapeattr__(%s)" % (len(stack)*cls.indent, s))
		elif issubclass(t, code):
			lines.append("%s%s" % (len(stack)*cls.indent, s))
		elif issubclass(t, def_):
			lines.append("")
			lines.append("%sdef %s:" % (len(stack)*cls.indent, s))
			stack.append((t, s))
			stackoutput.append(True)
		elif issubclass(t, enddef):
			endscope(def_)
			stackoutput.pop()
		elif issubclass(t, class_):
			lines.append("")
			lines.append("%sclass %s:" % (len(stack)*cls.indent, s))
			stack.append((t, s))
			stackoutput.append(False)
		elif issubclass(t, endclass):
			endscope(class_)
			stackoutput.pop()
		elif issubclass(t, for_):
			lines.append("%sfor %s:" % (len(stack)*cls.indent, s))
			stack.append((t, s))
		elif issubclass(t, endfor):
			endscope(for_)
		elif issubclass(t, while_):
			lines.append("%swhile %s:" % (len(stack)*cls.indent, s))
			stack.append((t, s))
		elif issubclass(t, endwhile):
			endscope(while_)
		elif issubclass(t, if_):
			lines.append("%sif %s:" % (len(stack)*cls.indent, s))
			stack.append((t, s))
		elif issubclass(t, else_):
			lines.append("%selse:" % ((len(stack)-1)*cls.indent))
		elif issubclass(t, elif_):
			lines.append("%selif %s:" % ((len(stack)-1)*cls.indent, s))
		elif issubclass(t, endif):
			endscope(if_)
	if stack:
		raise SyntaxError("unclosed scopes remaining")
	return "\n".join(lines)


@classmethod
def xml2mod(cls, source, name=None, filename="<string>", store=False, loader=None):
	name = name or "ll.xist.ns.detox.sandbox_%x" % (hash(filename) + sys.maxint + 1)
	module = new.module(name)
	module.__file__ = filename
	if loader is not None:
		module.__loader__ = loader
	if store:
		sys.modules[name] = module
	code = compile(cls.xml2py(source), filename, "exec")
	exec code in module.__dict__
	return module


# The following stuff has been copied from Kid's import hook

DETOX_EXT = ".detox"


@classmethod
def enable_import(cls, suffixes=None):
	class VenomLoader(object):
		def __init__(self, path=None):
			if path and os.path.isdir(path):
				self.path = path
			else:
				raise ImportError

		def find_module(self, fullname):
			path = os.path.join(self.path, fullname.split(".")[-1])
			for ext in [cls.DETOX_EXT] + self.suffixes:
				if os.path.exists(path + ext):
					self.filename = path + ext
					return self
			return None

		def load_module(self, fullname):
			try:
				return sys.modules[fullname]
			except KeyError:
				return cls.xml2mod(open(self.filename, "r").read(), name=fullname, filename=self.filename, store=True, loader=self)

	VenomLoader.suffixes = suffixes or []
	sys.path_hooks.append(VenomLoader)
	sys.path_importer_cache.clear()


class __ns__(xsc.Namespace):
	xmlname = "detox"
	xmlurl = "http://xmlns.livinglogic.de/xist/ns/detox"
__ns__.makemod(vars())
