#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-

## Copyright 2004 by LivingLogic AG, Bayreuth/Germany.
## Copyright 2004 by Walter Dörwald
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


__version__ = tuple(map(int, "$Revision: 1.13 $"[11:-2].split(".")))
# $Source: /data/cvsroot/LivingLogic/Python/core/__init__.py,v $


import sys, new, pprint


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
	will automatically generated the appropriate property:</par>

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
	def __new__(cls, name, bases, dict):
		# Convert functions to staticmethods as Namespaces won't be instantiated anyway
		# If you need a classmethod simply define one
		for (key, value) in dict.iteritems():
			if isinstance(value, new.function):
				dict[key] = staticmethod(value)
		return super(_Namespace_Meta, cls).__new__(cls, name, bases, dict)

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
	A namespace can be used as inheritable module (see the method
	<pyref method="makemod"><method>makemod</method></pyref>).
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
