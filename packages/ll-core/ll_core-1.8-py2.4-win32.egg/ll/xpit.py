#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-

## Copyright 2005-2007 by LivingLogic AG, Bayreuth/Germany.
## Copyright 2005-2007 by Walter Dörwald
##
## All Rights Reserved
##
## See __init__.py for the license


"""
<par><module>ll.xpit</module> contains functions that make it possible to embed
Python expressions and conditionals in text.</par>

<par>An example:</par>

<example>
<prog>
from ll import xpit

text = '''
a = &lt;?= a?&gt;
b = &lt;?= b?&gt;
The sum is &lt;?= a+b?&gt;
&lt;?if a&gt;0?&gt;a is positive&lt;?elif a==0?&gt;a is 0&lt;?else?&gt;a is negative&lt;?endif?&gt;
'''

print xpit.convert(text, dict(a=23, b=42))
</prog>
</example>

<par>This will print:</par>

<tty>
a = 23
b = 42
The sum is 65
a is positive
</tty>
"""


__version__ = tuple(map(int, "$Revision: 1.3 $"[11:-2].split(".")))
# $Source: /data/cvsroot/LivingLogic/Python/core/src/ll/xpit.py,v $


def tokenize(string):
	"""
	Tokenize the string <arg>string</arg> and split it into processing
	instructions and text. <function>tokenize</function> will generate tuples
	with the first item being the processing instruction target and the second
	being the PI data. <z>Text</z> content (i.e. anything other than PIs)
	will be returned as <lit>(None, <rep>data</rep>)</lit>. A literal
	<lit>&lt;?</lit> can be written as <lit>&lt;?&gt;</lit> and will be returned
	as text.
	"""
	pos = 0
	while True:
		pos1 = string.find("<?", pos)
		if pos1<0:
			part = string[pos:]
			if part:
				yield (None, part)
			return
		pos2 = string.find("?>", pos1)
		if pos2<0:
			part = string[pos:]
			if part:
				yield (None, part)
			return
		elif pos2 == pos1+1: # <?>
			yield (None, string[pos:pos1+2])
			pos = pos1+3
			continue
		part = string[pos:pos1]
		if part:
			yield (None, part)
		parts = string[pos1+2:pos2].split(None, 1)
		if len(parts) > 1:
			yield tuple(parts)
		else:
			yield (parts[0], parts[0][:0]) # empty string of correct type as data
		pos = pos2+2


class UnknownTargetError(ValueError):
	"""
	Exception that is raised when an unknown PI target (i.e. anything except
	<lit>=</lit>, <lit>if</lit>, <lit>elif</lit>, <lit>else</lit>, <lit>endif</lit>)
	is encountered.
	"""
	def __init__(self, target):
		self.target = target

	def __str__(self):
		return "Unknown PI target %s" % self.target


def convert(string, globals=None, locals=None):
	"""
	<par>Convert <arg>string</arg> using <arg>globals</arg> and
	<arg>locals</arg> as the global and local namespace.</par>

	<par>All processing instructions in <arg>string</arg> with the target <lit>=</lit>
	(e.g. <lit>&lt;?=23+42?&gt;</lit>) will be evaluated with <arg>globals</arg> as the
	global and <arg>locals</arg> as the local namespace. Plain text will be passed
	through literally. Other allowed PI targets are <lit>if</lit>, <lit>else</lit>,
	<lit>elif</lit> and <lit>endif</lit>. These PIs implement conditional output.
	The PI content of <lit>if</lit> and <lit>elif</lit> is evaluated as a Python
	expression. If it is true, everything after this PI (up to the next
	<lit>else</lit>, <lit>endif</lit> etc.) will be included in the output.
	All these PIs will have <arg>globals</arg> as the global and
	<arg>locals</arg> as the local namespace.</par>

	<par>Processing instructions with other targets will raise an
	<pyref class="UnknownTargetError"><class>UnknownTargetError</class></pyref> exception.</par>
	"""
	def all(conds): # FIXME: use the new all() in Python 2.5
		for (type, ifcond, notelsecond) in conds:
			if not ifcond:
				return False
		return True

	v = []
	conds = [] # stack of (condition type, if-expression, else-expresion)
	for (action, data) in tokenize(string):
		if action is None:
			if all(conds):
				v.append(data)
		elif action == "if":
			cond = eval(data, globals, locals)
			conds.append(("if", cond, not cond))
		elif action == "elif":
			cond = eval(data, globals, locals)
			conds[-1] = ("elif", cond, conds[-1][2] and not cond)
		elif action == "else":
			conds[-1] = ("else", conds[-1][2], False)
		elif action == "endif":
			del conds[-1]
		elif action == "=":
			if all(conds):
				data = str(eval(data, globals, locals))
				v.append(data)
		elif action is not None:
			raise UnknownTargetError(action)
	return "".join(v)
