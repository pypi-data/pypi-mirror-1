#! /usr/bin/env python
# -*- coding: utf-8 -*-

## Copyright 2004-2008 by LivingLogic AG, Bayreuth/Germany.
## Copyright 2004-2008 by Walter Dörwald
##
## All Rights Reserved
##
## See __init__.py for the license


"""
<mod>ll.misc</mod> contains various utility functions and classes used
by the other LivingLogic modules and packages.
"""


import sys, types, collections, weakref


# fetch item, first, last and count
from ll._misc import *


__docformat__ = "xist"


def notimplemented(function):
	"""
	A decorator that raises <class>NotImplementedError</class> when the method
	is called. This saves you the trouble of formatting the error message
	yourself for each implementation.
	"""
	def wrapper(self, *args, **kwargs):
		raise NotImplementedError("method %s() not implemented in %r" % (function.__name__, self.__class__))
	wrapper.__dict__.update(function.__dict__)
	wrapper.__doc__ = function.__doc__
	wrapper.__name__ = function.__name__
	wrapper.__wrapped__ = function
	return wrapper


def withdoc(doc):
	"""
	A decorator that adds a docstring to the function it decorates. This can be
	useful if the docstring is not static, and adding it afterwards is not
	possible.
	"""
	def wrapper(function):
		function.__doc__ = doc
		return function
	return wrapper


class _propclass_Meta(type):
	def __new__(cls, name, bases, dict):
		if bases == (property,):
			# create propclass itself normally
			return super(_propclass_Meta, cls).__new__(cls, name, bases, dict)
		newdict = dict.copy()
		newdict.pop("__get__", None)
		newdict.pop("__set__", None)
		newdict.pop("__delete__", None)
		newdict.pop("__metaclass__", None)
		self = type.__new__(cls, name, bases, newdict)
		inst = self(
			dict.get("__get__", None),
			dict.get("__set__", None),
			dict.get("__delete__", None),
			dict.get("__doc__", None)
		)
		inst.__name__ = name
		return inst


class propclass(property):
	'''
	<p><class>propclass</class> provides an alternate way to define properties.</p>

	<p>Subclassing <class>propclass</class> and defining methods
	<meth>__get__</meth>, <meth>__set__</meth> and <meth>__delete__</meth>
	will automatically generate the appropriate property:</p>

	<prog>
	class name(misc.propclass):
		"""
		The name property
		"""
		def __get__(self):
			return self._name
		def __set__(self, name):
			self._name = name.lower()
		def __delete__(self):
			self._name = None
	</prog>
	'''
	__metaclass__ = _propclass_Meta


class Pool(object):
	"""
	A <class>Pool</class> object can be used as an inheritable alternative
	to modules. The weak-referenceable attributes of a module can be put into a
	pool and each pool can have base pools where lookup continues if an attribute
	can't be found.
	"""
	def __init__(self, *objects):
		self._attrs = weakref.WeakValueDictionary()
		self.bases = []
		for object in objects:
			self.register(object)

	def register(self, object):
		"""
		Register <arg>object</arg> in the pool. <arg>object</arg> can be a module,
		a dictionary or a <class>Pool</class> objects (with registers the pool as
		a base pool. If <arg>object</arg> is a module and has an attribute
		<lit>__bases__</lit> (being a sequence of other modules) this attribute
		will be used to initialize <self/>s base pool.
		"""
		if isinstance(object, types.ModuleType):
			for (key, value) in object.__dict__.iteritems():
				try:
					self._attrs[key] = value
				except TypeError:
					pass
			if hasattr(object, "__bases__"):
				for base in object.__bases__:
					if not isinstance(base, Pool):
						base = self.__class__(base)
					self.register(base)
		elif isinstance(object, dict):
			for (key, value) in object.iteritems():
				try:
					self._attrs[key] = value
				except TypeError:
					pass
		elif isinstance(object, Pool):
			self.bases.append(object)

	def __getitem__(self, key):
		try:
			return self._attrs[key]
		except KeyError:
			for base in self.bases:
				return base[key]
			raise

	def __getattr__(self, key):
		try:
			return self.__getitem__(key)
		except KeyError:
			raise AttributeError(key)

	def clone(self):
		copy = self.__class__()
		copy._attrs = self._attrs.copy()
		copy.bases = self.bases[:]
		return copy


def iterone(item):
	"""
	Return an iterator that will produce one item: <arg>item</arg>.
	"""
	yield item


class Iterator(object):
	"""
	<class>Iterator</class> adds <meth>__getitem__</meth> support to an iterator.
	This is done by calling <pyref function="item"><func>item</func></pyref>
	internally.
	"""
	__slots__ = ("iterator", )

	def __init__(self, iterator):
		self.iterator = iterator

	def __getitem__(self, index):
		if isinstance(index, slice):
			return list(self.iterator)[index]
		return item(self, index)

	def __iter__(self):
		return self

	def next(self):
		return self.iterator.next()

	# We can't implement __len__, because if such an object is passed to list(), __len__() would be called, exhausting the iterator

	def __nonzero__(self):
		for node in self:
			return True
		return False

	def get(self, index, default=None):
		"""
		Return the <arg>index</arg>th item from the iterator
		(or <arg>default</arg> if there's no such item).
		"""
		return item(self, index, default)


class Queue(object):
	"""
	<class>Queue</class> provides FIFO queues: The method <meth>write</meth>
	writes to the queue and the method <meth>read</meth> read from the other
	end of the queue and remove the characters read.
	"""
	def __init__(self):
		self._buffer = ""

	def write(self, chars):
		"""
		Write the string <arg>chars</arg> to the buffer.
		"""
		self._buffer += chars

	def read(self, size=-1):
		"""
		Read up to <arg>size</arg> character from the buffer (or all if <arg>size</arg> is negative).
		Those characters will be removed from the buffer.
		"""
		if size<0:
			s = self._buffer
			self._buffer = ""
			return s
		else:
			s = self._buffer[:size]
			self._buffer = self._buffer[size:]
			return s


class Const(object):
	"""
	This class can be used for singleton constants.
	"""
	__slots__ = ("_name")

	def __init__(self, name):
		self._name = name

	def __repr__(self):
		return "%s.%s" % (self.__module__, self._name)


def tokenizepi(string):
	"""
	Tokenize the string object <arg>string</arg> according to the processing
	instructions in the string. <func>tokenize</func> will generate tuples with
	the first item being the processing instruction target and the second being
	the PI data. <z>Text</z> content (i.e. anything other than PIs) will be
	returned as <lit>(None, <rep>data</rep>)</lit>.
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
		part = string[pos:pos1]
		if part:
			yield (None, part)
		part = string[pos1+2: pos2].strip()
		parts = part.split(None, 1)
		target = parts[0]
		if len(parts) > 1:
			data = parts[1]
		else:
			data = ""
		yield (target, data)
		pos = pos2+2
