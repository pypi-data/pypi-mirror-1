#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-

## Copyright 2004/2005 by LivingLogic AG, Bayreuth/Germany.
## Copyright 2004/2005 by Walter Dörwald
##
## All Rights Reserved
##
## Permission to use, copy, modify, and distribute this software and its documentation
## for any purpose and without fee is hereby granted, provided that the above copyright
## notice appears in all copies and that both that copyright notice and this permission
## notice appear in supporting documentation, and that the name of LivingLogic AG or
## the author not be used in advertising or publicity pertaining to distribution of the
## software without specific, written prior permission.
##
## LIVINGLOGIC AG AND THE AUTHOR DISCLAIM ALL WARRANTIES WITH REGARD TO THIS SOFTWARE,
## INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS, IN NO EVENT SHALL
## LIVINGLOGIC AG OR THE AUTHOR BE LIABLE FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL
## DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER
## IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR
## IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.


"""
This package contains various utility functions and classes used
by the other LivingLogic sub-packages.
"""


__version__ = tuple(map(int, "$Revision: 1.17 $"[11:-2].split(".")))
# $Source: /data/cvsroot/LivingLogic/Python/core/__init__.py,v $


import sys, new, pprint, collections

###
### Decorators
###

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


def asdisplayhook(function):
	"""
	A decorator that will install <arg>function</arg> as a cooperative
	display hook. <arg>function</arg> gets passed the object to be displayed
	and might print it in some form to <lit>sys.stdout</lit>. If <arg>function</arg>
	returns false the previous display hook gets a chance to print this object.
	The return value of <function>asdisplayhook</function> is <arg>function</arg>.
	"""
	oldhook = sys.displayhook
	def hook(obj):
		result = function(obj)
		if result is not None and not result: # check for None to support other hooks
			result = oldhook(obj)
		return result
	hook.__dict__.update(function.__dict__)
	hook.__doc__ = function.__doc__
	hook.__name__ = function.__name__
	sys.displayhook = hook
	return function


defaultprettyprinter = pprint.PrettyPrinter()


def defaultdisplayhook(obj):
	"""
	This function can be used as a default display hook. It uses the
	<module>pprint</module> module to pretty print <arg>obj</arg>.
	"""
	if obj is not None:
		defaultprettyprinter.pprint(obj)
	return True


###
### Properties
###

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
	<par><class>propclass</class> provides an alternate way to define properties.</par>

	<par>Subclassing <class>propclass</class> and defining methods
	<method>__get__</method>, <method>__set__</method> and <method>__delete__</method>
	will automatically generate the appropriate property:</par>

	<prog>
	class name(ll.propclass):
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


class _Namespace_Meta(type):
	def __delattr__(self, key):
		value = getattr(self, key)
		if hasattr(value, "__ns__"):
			value.__ns__ = None
		return super(_Namespace_Meta, self).__delattr__(key)

	def __setattr__(self, key, value):
		if isinstance(value, new.function):
			value = staticmethod(value)
		if hasattr(value, "__ns__"):
			value.__ns__ = self
		return super(_Namespace_Meta, self).__setattr__(key, value)

	def __getitem__(self, key):
		try:
			return getattr(self, key)
		except AttributeError:
			raise KeyError(key)


class Namespace(object):
	"""
	A namespace can be used as an <z>inheritable module</z> (see the method
	<pyref method="makemod"><method>makemod</method></pyref>). Namespaces are
	supposed to be subclassed, but not instantiated.
	"""
	__metaclass__ = _Namespace_Meta

	@classmethod
	def update(cls, *args, **kwargs):
		"""
		Copy attributes from all mappings in <arg>args</arg> and from
		<arg>kwargs</arg>.
		"""
		for mapping in args + (kwargs,):
			for (key, value) in mapping.iteritems():
				if value is not cls and key not in ("__name__", "__dict__"):
					setattr(cls, key, value)

	@classmethod
	def makemod(cls, vars=None):
		"""
		Update <cls/> with objects from <arg>vars</arg> (like
		<pyref method="update"><method>update</method></pyref> does) and turn the
		namespace into a module (replacing the module that contains the namespace
		in <lit>sys.modules</lit>).
		"""
		if vars is not None:
			cls.update(vars)
		name = vars["__name__"]
		if name in sys.modules: # If the name can't be found, the import is probably done by execfile(), in this case we can't communicate back that the module has been replaced
			cls.__originalmodule__ = sys.modules[name] # we have to keep the original module alive, otherwise Python would set all module attribute to None
			sys.modules[name] = cls
		# set the class name to the original module name, otherwise inspect.getmodule() will get problems
		cls.__name__ = name


###
### General iterator utilities
###

_defaultitem = object()

def item(iterator, index, default=_defaultitem):
	"""
	<par>Return the <arg>index</arg>th item from the iterator <arg>iterator</arg>.
	<arg>index</arg> must be an integer (negative integers are relative to the
	end (i.e. the last item produced by the iterator)).</par>

	<par>If <arg>default</arg> is given, this will be the default value when
	the iterator doesn't contain an item at this position. Otherwise an
	<class>IndexError</class> will be raised.</par>

	<par>Note that using this function will partially or totally exhaust the
	iterator.</par>
	"""
	i = index
	if i>=0:
		for item in iterator:
			if not i:
				return item
			i -= 1
	else:
		i = -index
		cache = collections.deque()
		for item in iterator:
			cache.append(item)
			if len(cache)>i:
				cache.popleft()
		if len(cache)==i:
			return cache.popleft()
	if default is _defaultitem:
		raise IndexError(index)
	else:
		return default


def first(iterator, default=_defaultitem):
	"""
	<par>Return the first object produced by the iterator <arg>iterator</arg> or
	<arg>default</arg> if the iterator didn't produce any items.</par>
	<par>Calling this function will consume one item from the iterator.</par>
	"""
	return item(iterator, 0, default)


def last(iterator, default=_defaultitem):
	"""
	<par>Return the last object from the iterator <arg>iterator</arg> or
	<arg>default</arg> if the iterator didn't produce any items.</par>
	<par>Calling this function will exhaust the iterator.</par>
	"""
	return item(iterator, -1, default)


def count(iterator):
	"""
	<par>Return the number of items produced by the iterator <arg>iterator</arg>.</par>
	<par>Calling this function will exhaust the iterator.</par>
	"""
	count = 0
	for node in iterator:
		count += 1
	return count


def iterone(item):
	"""
	Return an iterator that will produce one item: <arg>item</arg>.
	"""
	yield item


###
### Add __getitem__ support to an iterator
###

class Iterator(object):
	"""
	<class>Iterator</class> adds <method>__getitem__</method> support to an
	iterator. This is done by calling <pyref function="item"><function>item</function></pyref>
	internally.
	"""
	__slots__ = "iterator"

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
