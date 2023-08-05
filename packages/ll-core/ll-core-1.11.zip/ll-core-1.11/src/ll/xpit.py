#! /usr/bin/env python
# -*- coding: utf-8 -*-

## Copyright 2005-2008 by LivingLogic AG, Bayreuth/Germany.
## Copyright 2005-2008 by Walter Dörwald
##
## All Rights Reserved
##
## See __init__.py for the license


"""
<p><mod>ll.xpit</mod> contains functions that make it possible to embed
Python expressions and conditionals in text.</p>

<p>An example:</p>

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

<p>This will print:</p>

<tty>
a = 23
b = 42
The sum is 65
a is positive
</tty>
"""


__docformat__ = "xist"


def tokenize(string):
	"""
	Tokenize the string <arg>string</arg> and split it into processing
	instructions and text. <func>tokenize</func> will generate tuples
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
	<p>Convert <arg>string</arg> using <arg>globals</arg> and
	<arg>locals</arg> as the global and local namespace.</p>

	<p>All processing instructions in <arg>string</arg> with the target <lit>=</lit>
	(e.g. <lit>&lt;?=23+42?&gt;</lit>) will be evaluated with <arg>globals</arg> as the
	global and <arg>locals</arg> as the local namespace. Plain text will be passed
	through literally. Other allowed PI targets are <lit>if</lit>, <lit>else</lit>,
	<lit>elif</lit> and <lit>endif</lit>. These PIs implement conditional output.
	The PI content of <lit>if</lit> and <lit>elif</lit> is evaluated as a Python
	expression. If it is true, everything after this PI (up to the next
	<lit>else</lit>, <lit>endif</lit> etc.) will be included in the output.
	All these PIs will have <arg>globals</arg> as the global and
	<arg>locals</arg> as the local namespace.</p>

	<p>Processing instructions with other targets will raise an
	<pyref class="UnknownTargetError"><class>UnknownTargetError</class></pyref> exception.</p>
	"""
	v = []
	conds = [] # stack of (condition type, if-expression, else-expresion)
	for (action, data) in tokenize(string):
		if action is None:
			if all(ifcond for (type, ifcond, notelsecond) in conds):
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
			if all(ifcond for (type, ifcond, notelsecond) in conds):
				data = str(eval(data, globals, locals))
				v.append(data)
		elif action is not None:
			raise UnknownTargetError(action)
	return "".join(v)
