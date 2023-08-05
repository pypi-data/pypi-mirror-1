#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

## Copyright 2002-2005 by LivingLogic AG, Bayreuth/Germany.
## Copyright 2002-2005 by Walter Dörwald
##
## All Rights Reserved
##
## See __init__.py for the license


"""
<par><module>ll.make</module> provides tools for building projects.</par>

<par>Like <app>make</app> it allows you to specify dependencies
between files and actions to be executed when files don't exist or are out of date
with respect to one of their sources. But unlike <app>make</app> you
can do this in a object oriented way and targets are not only limited to files,
but you can implement e.g. dependencies on database records by implementing new
<pyref class="Target"><class>Target</class></pyref> classes.</par>

<par>Relevant classes are:</par>
<ulist>
<item><pyref class="Project"><class>Project</class></pyref>, which is the
container for all targets, actions and dependencies in a project,</item>
<item><pyref class="Target"><class>Target</class></pyref> (and subclasses),
which are files (or other entities like database records) that have to be built
by actions,</item>
<item><pyref class="Dep"><class>Dep</class></pyref> (and subclasses) which
specify types of dependencies between targets and</item>
<item><pyref class="Action"><class>Action</class></pyref> (and subclasses) which
specify how targets are (re)built if they don't exist or aren't up to date.</item>
</ulist>
"""

__version__ = "$Revision: 1.9 $"[11:-1]

import sys, os, os.path, optparse, warnings, re, datetime, cStringIO, errno, tempfile, operator, new, cPickle

from ll import misc, ansistyle, url


###
### exceptions & warnings
###

class MakeWarning(Warning):
	"""
	Base class for all warnings in <app>make</app>.
	"""


class RedefinedTargetWarning(MakeWarning):
	"""
	Warning that will be issued when a target is added to a project and a target
	with the same id already exists.
	"""

	def __init__(self, targetid):
		self.targetid = targetid

	def __str__(self):
		return "target with id=%r redefined" % self.targetid


class ClockSkewWarning(MakeWarning):
	"""
	Warning that will be issued when a target has a last modification date from the future.
	"""

	def __init__(self, targetid, lastmodified, now):
		self.targetid = targetid
		self.lastmodified = lastmodified
		self.now = now

	def __str__(self):
		return "target %r is from the future: %r>%r=now" % (self.targetid, self.lastmodified, self.now)


class UndefinedTargetError(KeyError):
	"""
	Exception that will be raised when a target with the specified id doesn't
	exist within the project.
	"""

	def __init__(self, id):
		self.id = id

	def __str__(self):
		return "target %r undefined" % self.id


class InputError(Exception):
	"""
	Exception that will be raised when a target has the wrong number of inputs.
	"""

	def __init__(self, action, target, inputs):
		self.action = action
		self.target = target
		self.inputs = inputs

	def __str__(self):
		return "wrong number of inputs for target %r in action %r: %r" % (self.target, self.action, self.inputs)


class ChainError(Exception):
	"""
	Exeption that will be raised when an action in a chain gets an input
	it can't handle.
	"""
	def __init__(self, target, message):
		self.target = target
		self.message = message

	def __str__(self):
		return "can't create %r: %s" % (self.target, self.message)


###
### Dependency classes
###

class Dep(object):
	"""
	<par>A <class>Dep</class> is a dependency between an <z>input</z>
	and an <z>output</z> <pyref class="Target"><class>Target</class></pyref>.
	It's possible to assign specific meanings to certain dependencies by using
	subclasses of <class>Dep</class>.</par>
	"""
	__slots__ = ("input", "output")

	def __init__(self, input, output):
		"""
		<par>create a <class>Dep</class> instance.</par>
		"""
		self.input = input
		self.output = output
		output._inputs.append(self)
		input._outputs.append(self)

	def __hash__(self):
		return hash(self.input.id) ^ hash(self.output.id)

	def __eq__(self, other):
		return self.input.id == other.input.id and self.output.id == other.output.id

	def __ne__(self, other):
		return self.input.id != other.input.id or self.output.id != other.output.id

	def __repr__(self):
		return "<%s from %r to %r at 0x%x>" % (self.__class__.__name__, self.input, self.output, id(self))


class MainDep(Dep):
	"""
	This class can be used to create a special dependency between two targets.
	This is used by <pyref class="SelectMainAction"><class>SelectMainAction</class></pyref>
	to select the main input target.
	"""
	pass


class OrderedDep(MainDep):
	"""
	This dependency class represents an ordered dependency, i.e. each
	instance has an <lit>order</lit> attribute. This is used by
	<pyref class="JoinOrderedAction"><class>JoinOrderedAction</class></pyref>
	to join several input targets in a specified order.
	"""
	order = 0

	__slots__ = ("order")

	def __init__(self, source, target, order=None):
		"""
		Create a new <class>OrderedDep</class> instance.
		When <arg>order</arg> is not specified, a new unique order value
		will be used that will be greater than the order value of
		previously created <class>OrderedDep</class> instances.
		"""
		MainDep.__init__(self, source, target)
		if order is None:
			order = self.__class__.order
			self.__class__.order += 1
		self.order = order


class ImportDep(Dep):
	"""
	A dependency that has been generated automatically by
	<pyref class="UseModuleAction"><class>UseModuleAction</class></pyref>.
	Such a dependency should never be generated by the user, as it will be
	automatically removed and recreated during build operations.
	"""


###
### Target classes
###

_nodata = object() # marker object for "no data object computed yet"

class Target(object):
	"""
	<par>The base class of all targets.</par>

	<par>For each target there are two representations: An internal and an external
	one. The internal representation is a Python object that is generated during
	the build process. The external representation will be a file in most cases,
	but might also be a database record or similar things. The internal
	representation will be stored in the target object.</par>

	<par>For converting between internal and external representation and between
	different internal representations each target stores four
	<pyref class="ChainedAction">action chains</pyref>):</par>

	<dlist>
	<term><lit>readaction</lit></term><item>This action is used to convert from
	the external representation to the internal representation of the target
	(e.g. by reading the content of a file and returning it as a string.</item>

	<term><lit>writeaction</lit></term><item>This action is used for converting
	the internal representation to the external representation (e.g. by taking
	the string produced by the previous action in the chain and writing it to
	the output file.</item>

	<term><lit>convertaction</lit></term><item>This action is used for converting
	one internal representation to another (e.g. by doing an &xist; conversion
	etc.).</item>

	<term><lit>useaction</lit></term><item>This action is executed when internal
	and external representation are up-to-date and this target is merely reused
	by other targets.</item>
	</dlist>

	<par>When a target is updated there are several possible situations:</par>

	<ulist>
	<item>The external representation of a target doesn't exist or is out of date:
	In this case the internal representation of this target is regenerated by
	executing the chain of convert actions. The resulting object is cached in
	the target. Then the external representation is generated from the internal
	representation via the chain of write actions.</item>

	<item>The external representation of a target exists and is up to date, but
	there is no internal representation, but this internal representation is
	needed (e.g. one of <self/>s output targets might need the data):
	In this case the internal representation is regenerated from the external
	representation by executing the chain of read actions.</item>

	<item>The external representation of a target exists and is up to date, and
	an internal representation exists: In this case the chain of use actions is
	executed (see <pyref class="UseModuleAction"><class>UseModuleAction</class></pyref>
	for how this chain might be used).</item>
	</ulist>
	"""
	def __init__(self, project, id, convertaction=None, writeaction=None, readaction=None, useaction=None, cache=False):
		"""
		<par>Create a new <class>Target</class> instance.</par>
		<par><arg>convertaction</arg>, <arg>writeaction</arg>, <arg>readaction</arg> and
		<arg>useaction</arg> are used to create the target data from their inputs
		(<arg>convert</arg>), write the data to disk (<arg>write</arg>), read the
		data from disk (<arg>read</arg>) or reuse an up-to-date target in another
		target.</par>
		<par>Each must be an <pyref class="Action"><class>Action</class></pyref> object,
		which will be executed in order to create the target. If might be a
		<pyref class="ChainedAction"><class>ChainedAction</class></pyref> object,
		so that multiple atomic actions are executed sequentially.</par>
		"""
		self.project = project
		self.id = id

		if convertaction is None:
			convertaction = NullAction()
		self.convertaction = convertaction

		if writeaction is None:
			writeaction = NullAction()
		self.writeaction = writeaction

		if readaction is None:
			readaction = NullAction()
		self.readaction = readaction

		if useaction is None:
			useaction = NullAction()
		self.useaction = useaction

		self.uptodate = False # Is this target up to date?
		self.cache = cache
		self.data = _nodata # The data generated either by readaction of self or by readaction + convertaction of the inputs

		self._inputs = []
		self._outputs = []

		self.project[self.id] = self

	def lastmodified(self):
		"""
		<par>return the timestamp, when this target was last modified or <lit>None</lit>
		when the target does not exist. The timestamp will be cached and will be updated
		when a target is remade.</par>
		"""
		try:
			return self._lastmodified
		except AttributeError:
			lm = self.getlastmodified()
			now = datetime.datetime.utcnow()
			if lm is not None and lm>now:
				self.project.reportWarning(ClockSkewWarning(self, lm, now), 2)
			self._lastmodified = lm
			return lm

	@misc.notimplemented
	def getlastmodified(self):
		"""
		<par>return the timestamp of the last modification.
		Overwrite in subclasses.</par>
		"""

	def touch(self):
		"""
		<par>Marks <self/> as <z>has been updated now</z>.</par>
		"""
		self._lastmodified = datetime.datetime.utcnow()
		self.uptodate = True

	def clear(self):
		"""
		<par>Reset the build status, so the target may be rebuilt on subsequent calls.</par>
		"""
		try:
			del self._lastmodified
		except AttributeError:
			pass
		self.uptodate = False
		self.convertaction.clear()
		self.writeaction.clear()
		self.readaction.clear()
		self.useaction.clear()

	def destroy(self):
		"""
		<par>Called by <pyref class="Project" method="destroy"><method>Project.destroy</method></pyref>
		to get rid of all the old targets.</par>
		"""
		self._inputs = []
		self._outputs = []

	def _reportaction(self, desc, data, time, chainchars):
		if self.project.showaction:
			self.project.report(ansistyle.Text(len(self.project.stack)*(self.project.color4tree, self.project.chars4tree, self.project.color4chain, chainchars)))
			self.project.report(desc)

			if self.project.showtime:
				self.project.report(ansistyle.Text(self.project.color4progress, " ", self.project.strseconds(time)))

			if self.project.showdata and data is not None:
				self.project.report(ansistyle.Text(self.project.color4progress, " "))
				display = repr(data)
				if len(display) > 40:
					display = ansistyle.Text(self.project.color4data, display[:20], (self.project.color4ellipsis, "..."), display[-20:])
				else:
					display = ansistyle.Text(self.project.color4data, display)
				self.project.report(display)
			self.project.report("\n")

	def _reporttarget(self, inputtime, selftime):
		if self.project.showtarget:
			self.project.report(ansistyle.Text(len(self.project.stack)*(self.project.color4tree, self.project.chars4tree, self.project.color4chain, self.project.chars4target)))
			self.project.report(self.project.strtarget(self))
			if self.project.showtime:
				self.project.report(ansistyle.Text(self.project.color4progress, " ", self.project.strseconds(inputtime), " inputs; ", self.project.strseconds(selftime), " self"))
			self.project.report("\n")

	def _callchain(self, data, chain, chainchars):
		for action in chain:
			desc = None
			if self.project.showactionfull:
				desc = action.fulldesc(self, data)
			elif self.project.showaction:
				desc = action.desc()
			t1 = datetime.datetime.utcnow()
			data = action.execute(self, data)
			t2 = datetime.datetime.utcnow()
			self._reportaction(desc, data, t2-t1, chainchars)
		return data

	def dirty(self):
		"""
		Reset timestamp info and drop cached object to force rebuilding of <self/>
		(because some input target has changed).
		"""
		if self.uptodate:
			self._lastmodified = None
			for dep in self._outputs:
				dep.output.dirty()
			self.convertaction.dirty()
			self.writeaction.dirty()
			self.readaction.dirty()
			self.useaction.dirty()
			self.uptodate = False
		self.data = _nodata # remove cached object

	def getdata(self):
		"""
		Return the internal representation of <self/> (either by rebuilding it
		from the inputs, or by reading in from the external representation or simply
		by returning the cached object).
		"""
		self.update()

		try:
			global currentproject
			self.oldproject = currentproject
			currentproject = self.project # Put the project name into a global variable, so imported modules can access it to import other modules
			self.project.stack.append(self)

			data = self.data
			if data is _nodata: # Data hasn't been updated in update() and isn't cached
				data = self._callchain(None, self.readaction, self.project.chars4read)
				# Cache data, if the user wants to
				if self.cache:
					self.data = data
			else: # We already had the data => reuse it (which might record additional dependencies)
				self.data = self._callchain(data, self.useaction, self.project.chars4use)
		finally:
			self.project.stack.pop(-1)
			currentproject = self.oldproject

		return data

	def update(self):
		"""
		<par>Update this target and all of its sources, if necessary. Return whether
		<self/> really had to be updated and the timestamp of the external
		representation.</par>
		"""
		t0 = datetime.datetime.utcnow()
		inputactions = 0
		hastobeupdated = False
		lastmodified = self.lastmodified()

		if lastmodified is None:
			hastobeupdated = True

		try:
			global currentproject
			self.oldproject = currentproject
			currentproject = self.project # Put the project name into a global variable, so imported modules can access it to import other modules
			self.project.stack.append(self)

			for dep in self._inputs:
				(inputupdated, inputtimestamp) = dep.input.update()
				if inputupdated or inputtimestamp is None or (lastmodified is not None and inputtimestamp>lastmodified):
					hastobeupdated = True
	
			# We need to update the file
			if hastobeupdated:
				self.dirty()
				exc_info = None
				try:
					# Start with None
					data = None
					t1 = datetime.datetime.utcnow()
	
					# Execute chain of convert action
					data = self._callchain(data, self.convertaction, self.project.chars4convert)
	
					# We always cache the data even if self.cache is False, because our output targets might need our data.
					# Once the output target is built, the cache is cleared (if self.cache is False)
					self.data = data
	
					# Execute chain of write actions
					data = self._callchain(data, self.writeaction, self.project.chars4write)
	
					t4 = datetime.datetime.utcnow()
					self._reporttarget(t1-t0, t4-t1)
				except SystemExit:
					raise
				except KeyboardInterrupt:
					raise
				except Exception, ex:
					if self.project.ignoreerrors:
						exc_info = sys.exc_info()
					else:
						raise

				t2 = datetime.datetime.utcnow()
				if exc_info is not None:
					import traceback
					self.project.reportError(*traceback.format_exception(*exc_info))
					self.project.reportError("\n", self.project.strerror("failed"), " after ", self.project.strseconds(t2-t1))
					self.project.targetsfailed += 1
				else:
					self.project.targetsrebuilt += 1
				self.touch() # always touch the target, so building can continue even if this target failed
			else:
				# We didn't update the data object, but the read chain is dynamic, so we have to execute it, because it might bring in other dependencies
				if self.data is _nodata:
					for action in self.readaction:
						if action.dynamic:
							dynamic = True
							break
					else:
						dynamic = False
					if dynamic:
						self.data = self._callchain(None, self.readaction, self.project.chars4read)
		finally:
			self.project.stack.pop(-1)
			currentproject = self.oldproject

		# Clear the caches of all inputs that should not be kept
		for dep in self._inputs:
			if not dep.input.cache:
				dep.input._nodata = None
		return (hastobeupdated, lastmodified)

	def iterinputs(self, type=Dep):
		"""
		<par>Iterate through all input targets of <self/> where the dependency is a subtype
		of <arg>type</arg>.</par>
		"""
		for dep in self._inputs:
			if isinstance(dep, type):
				yield dep.input

	def inputs(self, type=Dep):
		"""
		<par>return a list of all the input targets for <self/> where the dependency is a subtype
		of <arg>type</arg>.</par>
		"""
		return list(self.iterinputs(type))

	def iterinputdeps(self, type=Dep):
		"""
		<par>Iterate through all the input dependancies for <self/> that are a subtype
		of <arg>type</arg>.</par>
		"""
		for dep in self._inputs:
			if isinstance(dep, type):
				yield dep

	def inputdeps(self, type=Dep):
		"""
		<par>return a list of all the input dependancies for <self/> that are a subtype
		of <arg>type</arg>.</par>
		"""
		return list(self.iterinputdeps(type))

	def iteroutputs(self, type=Dep):
		"""
		<par>Iterate through all output targets of <self/> where the dependency is a subtype
		of <arg>type</arg>.</par>
		"""
		for dep in self._outputs:
			if isinstance(dep, type):
				yield dep.output

	def outputs(self, type=Dep):
		"""
		<par>return a list of all the target dependancies for <self/> that are a subtype
		of <arg>type</arg>.</par>
		"""
		return list(self.iteroutputs(type))

	def iteroutputdeps(self, type=Dep):
		"""
		<par>Iterate through all the output dependancies for <self/> that are a subtype
		of <arg>type</arg>.</par>
		"""
		for dep in self._outputs:
			if isinstance(dep, type):
				yield dep

	def outputdeps(self, type=Dep):
		"""
		<par>return a list of all the output dependencies for <self/> where the dependency is a subtype
		of <arg>type</arg>.</par>
		"""
		return list(self.iteroutputdeps(type))

	def dependOn(self, *others):
		"""
		<par>add one or more dependencies.</par>

		<par><arg>others</arg> may contain <pyref class="Target"><class>Target</class></pyref>
		instances and subclasses of <pyref class="Dep"><class>Dep</class></pyref>. This will be used to
		create specific dependencies. Initially <pyref class="Dep"><class>Dep</class></pyref> will be used to
		construct input dependencies for every <pyref class="Target"><class>Target</class></pyref> instance
		encountered in the argument list. From the point in the argument list where a
		<pyref class="Dep"><class>Dep</class></pyref> subclass is encountered this new class will be
		used for constructing dependencies. This makes it possible to switch between different
		dependency classes.</par>
		"""
		dependencyClass = Dep
		for other in others:
			if isinstance(other, type) and issubclass(other, Dep):
				dependencyClass = other
			else:
				dependency = dependencyClass(other, self)

	def reportinputs(self, mode="short", stream=None):
		"""
		Recursively print input targets for <self/> to the output stream <arg>stream</arg>
		(which defaults to <lit>sys.stdout</lit>).
		"""
		if stream is None:
			stream = sys.stdout
		if mode == "short":
			seen = {}
			def _report(dep, target, level, counter):
				text = ansistyle.Text(level*(self.project.color4tree, self.project.chars4tree, self.project.color4chain, self.project.chars4inputdep), self.project.strtarget(target))
				if dep is not None:
					text.append(" via ", self.project.strdep(dep))
				counter += 1
				try:
					seenat = seen[target.id]
				except KeyError:
					text.append((self.project.color4ref, " [%d]" % counter), "\n")
					stream.write(str(text))
					seen[target.id] = counter
					for dep in target._inputs:
						counter = _report(dep, dep.input, level+1, counter)
				else:
					if target._inputs:
						text.append((self.project.color4note, " (see ", (self.project.color4ref, "[%d]" % seenat), " for dependencies)"))
					text.append("\n")
					stream.write(str(text))
				return counter
			_report(None, self, 0, 0)
		elif mode == "full":
			def _report(dep, target, level):
				text = ansistyle.Text(level*(self.project.color4tree, self.project.chars4tree, self.project.color4chain, self.project.chars4inputdep), self.project.strtarget(target))
				if dep is not None:
					text.append(" via ", self.project.strdep(dep))
				text.append("\n")
				stream.write(str(text))
				for dep in target._inputs:
					_report(dep, dep.input, level+1)
			_report(None, self, 0)
		else:
			raise ValueError("unknown mode %r" % mode)

	def reportoutputs(self, mode="short", stream=None):
		"""
		Recursively print output targets for <self/> to the output stream <arg>stream</arg>
		(which defaults to <lit>sys.stdout</lit>).
		"""
		if stream is None:
			stream = sys.stdout
		if mode == "short":
			seen = {}
			def _report(dep, target, level, counter):
				text = ansistyle.Text(level*(self.project.color4tree, self.project.chars4tree, self.project.color4chain, self.project.chars4outputdep), self.project.strtarget(target))
				if dep is not None:
					text.append(" via ", self.project.strdep(dep))
				counter += 1
				try:
					seenat = seen[target.id]
				except KeyError:
					text.append((self.project.color4ref, " [%d]" % counter), "\n")
					stream.write(str(text))
					seen[target.id] = counter
					for dep in target._outputs:
						counter = _report(dep, dep.output, level+1, counter)
				else:
					if target._inputs:
						text.append((self.project.color4note, " (see ", (self.project.color4ref, "[%d]" % seenat), " for dependencies)"))
					text.append("\n")
					stream.write(str(text))
				return counter
			_report(None, self, 0, 0)
		elif mode == "full":
			def _report(dep, target, level):
				text = ansistyle.Text(level*(self.project.color4tree, self.project.chars4tree, self.project.color4chain, self.project.chars4outputdep), self.project.strtarget(target))
				if dep is not None:
					text.append(" via ", self.project.strdep(dep))
				text.append("\n")
				stream.write(str(text))
				for dep in target._outputs:
					_report(dep, dep.output, level+1)
			_report(None, self, 0)
		else:
			raise ValueError("unknown mode %r" % mode)

	def __repr__(self):
		return "<%s object id=%r at 0x%x>" % (self.__class__.__name__, self.id, id(self))

	def failed(self):
		"""
		Called by actions when building a target fails when writing the output
		has already begun. Derived classes will overwrite <method>failed</method>
		to remove broken files.
		"""
		self.project.report("Removing broken target %s ...\n" % self)


class FileSystemTarget(Target):
	"""
	<par>A target in the filesystem, i.e. a file or directory.</par>
	"""
	pass


class FileTarget(FileSystemTarget):
	"""
	<par>a file</par>
	"""
	name = "File"

	def getlastmodified(self):
		try:
			return self.id.mtime()
		except OSError:
			return None

	def failed(self):
		super(FileTarget, self).failed()
		if self.id.exists():
			self.id.remove()


class DirectoryTarget(FileSystemTarget):
	"""
	<par>a directory.</par>
	"""
	name = "Dir"

	def getlastmodified(self):
		# only rebuild if it doesn't exist, if it exists do nothing
		try:
			timestamp = self.id.mtime()
		except OSError:
			return None
		else:
			return datetime.datetime(1900, 1, 1) # should be older than any existing file/directory


class ImageTarget(FileTarget):
	"""
	<par>an image file.</par>
	"""
	name = "Image"


class JavascriptTarget(FileTarget):
	"""
	<par>a Javascript source file (extension <lit>.js</lit>)</par>
	"""
	name = "JS"


class CascadingStyleSheetTarget(FileTarget):
	"""
	<par>a Cascading Stylesheet file (extension <lit>.css</lit>)</par>
	"""
	name = "CSS"


class PHPTarget(FileTarget):
	"""
	<par>a PHP include file (extension <lit>.php</lit>)</par>
	"""
	name = "PHP"


class HTMLTarget(FileTarget):
	"""
	<par>a &html; file (extension <lit>.html</lit>, <lit>.phtml</lit>, <lit>.jsp</lit>, etc.)</par>
	"""
	name = "HTML"


class XMLTarget(FileTarget):
	name = "XML"
	"""
	<par>an &xml; file (extension <lit>.xml</lit>)</par>
	"""


class DTDTarget(FileTarget):
	"""
	<par>a Document Type Definition file (extension <lit>.dtd</lit>)</par>
	"""
	name = "DTD"


class PDFTarget(FileTarget):
	"""
	<par>a &pdf; file (extension <lit>.pdf</lit>)</par>
	"""
	name = "PDF"


class JavaPropTarget(FileTarget):
	"""
	<par>a Java properties file (extension <lit>.properties</lit>)</par>
	"""
	name = "JavaProp"


class SQLTarget(FileTarget):
	"""
	<par>an &sql; script (extension <lit>.sql</lit>)</par>
	"""
	name = "SQL"


class PythonTarget(FileTarget):
	"""
	<par>a Python source file (extension <lit>.py</lit>)</par>
	"""
	name = "Python"


class XISTNSTarget(PythonTarget):
	"""
	<par>a Python source file that contains an &xist; <pyref module="ll.xist.xsc" class="Namespace"><class>Namespace</class></pyref>
	object and must be imported to provide element definitions etc. to the &xist; parser.</par>
	"""
	name = "XISTNS"

	def __init__(self, project, id, convertaction=None, writeaction=None, readaction=None, useaction=None, cache=False, prefix=None):
		PythonTarget.__init__(self, project, id, convertaction, writeaction, readaction, useaction, cache)
		self.prefix = prefix


class XISTTarget(FileTarget):
	"""
	<par>an &xist; source file, i.e. a &xml; file that has to be transformed via <pyref module="ll.xist">&xist;</pyref>
	(extensions <lit>.xmlxsc</lit>, <lit>.htmlxsc</lit>, etc.)</par>
	"""
	name = "XIST"


class PhonyTarget(Target):
	"""
	<par>A <class>PhonyTarget</class> does not really exist. It can
	be used as a virtual target for all the real targets that have to be built.</par>
	"""
	name = "Phony"

	def __init__(self, project, id, convertaction=None, writeaction=None, readaction=None, useaction=None, doc=None):
		"""
		<par>Create a new <class>PhonyTarget</class>.</par>

		<par><arg>doc</arg> should be a description of the <class>PhonyTarget</class>
		and will be printed when <pyref class="Project" method="buildwithargs"><method>buildwithargs</method></pyref>
		is called without arguments.</par>
		"""
		Target.__init__(self, project, id, convertaction, writeaction, readaction, useaction)
		self.doc = doc

	def getlastmodified(self):
		"""
		<par>get the <z>last modification</z> timestamp. This will always
		be <lit>None</lit>, as a <class>PhonyTarget</class> does not really exist.
		Note that this means that the associated actions will be executed
		every time the target is updated.</par>
		"""
		return None


class DBTarget(Target):
	"""
	<par>a database procedure or function</par>
	"""
	name = "DB"

	def getlastmodified(self):
		return None


###
### Action classes
###

class Action(object):
	"""
	<par>An <class>Action</class> is responsible for rebuilding or modifying a
	<pyref class="Target"><class>Target</class></pyref>.</par>

	<par>An <class>Action</class> is stateless and may be used by multiple targets.
	Executing the action is done through a call to the method
	<pyref method="execute"><method>execute</method></pyref>.</par>
	"""

	dynamic = False

	def __init__(self):
		"""
		<par>Create a new <class>Action</class> instance.</par>
		"""

	@misc.notimplemented
	def execute(self, target, data):
		"""
		<par>execute the action to rebuild or modify <arg>target</arg>. Depending
		on the action itself, the input data is either read from the input targets
		of <arg>target</arg> or <arg>data</arg> is used (which must be produced by
		the previous action in the action chain). Furthermore the action may
		save the result to <arg>target</arg>, modify it (e.g. change the owner of the
		file) or return modified data (which will be passed to the next action in
		the chain).</par>
		"""
		return data

	def desc(self):
		"""
		Return the name of the action. The default is the class name (without
		<lit>Action</lit>).
		"""
		name = self.__class__.__name__
		if name.endswith("Action"):
			name = name[:-6]
		return name

	def fulldesc(self, target, data):
		return ansistyle.Text((target.project.color4action, self.desc()), "(", target.project.strid(target.id), ")")

	def __iter__(self):
		"""
		Iterate through all subactions of this action. As <self/> is not a chain
		this will only yield <self/>.
		"""
		yield self

	def __add__(self, other):
		"""
		Add <self/> and <arg>other</arg> and return a
		<pyref class="ChainedAction"><class>ChainedAction</class></pyref>.
		"""
		if isinstance(other, ChainedAction):
			return ChainedAction(*([self] + other.actions))
		else:
			return ChainedAction(self, other)

	def clear(self):
		pass

	def dirty(self):
		pass


class ChainedAction(Action):
	"""
	A <class>ChainedAction</class> object is a chain of <class>Action</class>
	objects that will be executed in sequence. The output of one action will
	be the input of the next action.
	"""
	def __init__(self, *actions):
		"""
		Create a <class>ChainedAction</class> instance with action in <arg>actions</arg>
		becoming the <z>subaction</z> of <self/>.
		"""
		Action.__init__(self)
		self.actions = list(actions)

	def execute(self, target, data):
		for action in self:
			data = action.execute(target, data)
		return data

	def __iter__(self):
		"""
		Iterate through all subactions of <self/>.
		"""
		for action in self.actions:
			for subaction in action:
				yield subaction

	def __add__(self, other):
		"""
		Add <self/> and <arg>other</arg> and return a new
		<pyref class="ChainedAction"><class>ChainedAction</class></pyref>.
		"""
		if isinstance(other, ChainedAction):
			return ChainedAction(*(self.actions + other.actions))
		else:
			return ChainedAction(*(self.actions + [other]))

	def __iadd__(self, other):
		if isinstance(other, ChainedAction):
			self.actions.extend(other.actions)
		else:
			self.actions.append(other)
		return self

	def clear(self):
		for action in self.actions:
			action.clear()

	def dirty(self):
		for action in self.actions:
			action.dirty()


class ReadAction(Action):
	"""
	This action can be used as the first action in a read action chain.
	It reads the external representation of the target (e.g. the content
	of the file) into memory.
	"""

	def execute(self, target, data):
		"""
		The input <arg>data</arg> will be ignored, the output data will
		be the content of the file.
		"""
		infile = target.id.openread()
		data = infile.read()
		infile.close()
		return data


class WriteAction(Action):
	"""
	This action can be used in a write action chain. It writes the input
	data into a file.
	"""

	def execute(self, target, data):
		"""
		The input <arg>data</arg> will be written to the file (or other
		object) represented by <arg>target</arg>. The output data will be
		<lit>None</lit>.
		"""
		if not isinstance(data, basestring):
			raise ChainError(target, "need a string as input, got %r" % data)
		outfile = target.id.openwrite()
		outfile.write(data)
		outfile.close()


class UnpickleAction(Action):
	"""
	This action can be used as the first action in a read action chain.
	It unpickles the external representation of the target.
	"""

	def execute(self, target, data):
		"""
		The input <arg>data</arg> will be ignored, the output data will
		be the unpickled content of the file.
		"""
		infile = target.id.openread()
		data = infile.read()
		data = cPickle.loads(s)
		infile.close()
		return data


class PickleAction(Action):
	"""
	This action can be used in a write action chain. It pickles the input data
	into a file.
	"""
	def __init__(self, protocol=0):
		"""
		Create a new <class>PickleAction</class> instance. <arg>protocol</arg>
		is used as the pickle protocol.
		"""
		Action.__init__(self)
		self.protocol = protocol

	def execute(self, target, data):
		"""
		The input <arg>data</arg> will be pickled to the file (or other
		object) represented by <arg>target</arg>. The output data will be
		<lit>None</lit>.
		"""
		if not isinstance(data, basestring):
			raise ChainError(target, "need a string as input, got %r" % data)
		outfile = target.id.openwrite()
		data = cPickle.dump(data, outfile, self.protocol)
		infile.close()
		return data

	def fulldesc(self, target, data):
		return ansistyle.Text((target.project.color4action, self.desc()), "(", target.project.strid(target.id), ", %d)" % self.protocol)


class SelectMainAction(Action):
	"""
	This action can be used as the first action in a convert chain. It fetches
	the data from one of the target's input targets.
	"""
	def execute(self, target, data):
		"""
		The target <arg>target</arg> must have exactly one input target using
		a <pyref class="MainDep"><class>MainDep</class></pyref> dependency. The
		internal representation of this target will be return as the output data.
		The input data is ignored.
		"""
		inputs = target.inputs(MainDep)
		if len(inputs) != 1:
			raise InputError(self, target, inputs)
		return inputs[0].getdata()


class JoinOrderedAction(Action):
	"""
	This action can be used as the first action in a convert chain. It fetches
	the data from several input targets and join it in a specified ordder.
	"""

	def execute(self, target, data):
		"""
		<par>Gets the internal representation from all input targets of
		<arg>target</arg> that depend on <arg>target</arg> via a
		<pyref class="OrderedDep"><class>OrderedDep</class></pyref>
		and joins them in the order specified by these dependencies.</par>
		<par>All internal representations must be simple strings.</par>
		<par>The input data will be ignored. The output data will be the
		joined string.</par>
		"""
		deps = target.inputdeps(OrderedDep)
		deps.sort(key=operator.attrgetter("order"))

		return "".join(dep.input.getdata() for dep in deps)


class MkDirAction(Action):
	"""
	<par>This action can be used in a write chain: It creates the target as a
	directory.</par>
	"""

	def __init__(self, mode=0777):
		"""
		Create a <class>MkDirAction</class> instance. <arg>mode</arg> (which defaults
		to <lit>0777</lit>) will be used as the permission bit pattern for the new directory.
		"""
		super(MkdDirAction, self).__init__()
		self.mode = mode

	def execute(self, target, data):
		"""
		<par>Create the directory with the permission bits specified in the constructor.</par>
		"""
		target.id.makedirs(self.mode)

	def __repr__(self):
		return "<%s.%s mode=%s at 0x%x>" % (self.__class__.__module__, self.__class__.__name__, oct(self.mode), id(self))


class XISTParseAction(Action):
	"""
	<par>This action can be used in a convert chain. It parses a string into an
	<pyref module="ll.xist"><app>&xist;</app></pyref> node.</par>
	"""

	def __init__(self, parser=None, base=None):
		"""
		Create an <class>XISTParseAction</class> object. <arg>parser</arg> must
		be an instance of <pyref class="ll.xist.parsers.Parser"><class>ll.xist.parsers.Parser</class></pyref>.
		If <arg>parser</arg> is <lit>None</lit> a parser will be created for you.
		<arg>base</arg> will be the base &url; used for parsing.
		"""
		super(XISTParseAction, self).__init__()
		if parser is None:
			from ll.xist import parsers
			parser = parsers.Parser()
		self.parser = parser
		self.base = base

	def loadnamespaces(self, target):
		"""
		<par>import all the source namespaces (i.e. all the input targets of <arg>target</arg>
		that are instances of <pyref class="XISTNSTarget"><class>XISTNSTarget</class></pyref>).</par>
		<par>The prefixes and module objects will be returned in a list of tuples.</par>
		"""
		return [ (input.prefix, input.getdata()) for input in target.iterinputs() if isinstance(input, XISTNSTarget) ]

	def execute(self, target, data):
		"""
		Parse the input string <arg>data</arg> into an &xml; node. In addition
		to the namespaces available for parsing in <lit><self/>.parser</lit> all
		namespaces loaded by <pyref method="loadnamespaces"><method>loadnamespaces</method></pyref>
		will be used. The output data is the parsed &xist; node.
		"""
		namespaces = self.loadnamespaces(target)
		if namespaces: # We need additional namespaces
			oldprefixes = self.parser.prefixes # Remember old prefixes
			prefixes = oldprefixes.clone()
			for (prefix, ns) in namespaces:
				prefixes[prefix].insert(0, ns)
			try:
				self.parser.prefixes = prefixes
				node = self.parser.parseString(data, self.base)
			finally:
				self.parser.prefixes = oldprefixes # Restore old prefixes
		else:
			node = self.parser.parseString(data, self.base)
		return node

	def __repr__(self):
		options = []
		for optionname in ("parser", "base"):
			optionvalue = getattr(self, optionname)
			if optionvalue is not None:
				options.append(" %s=%r" % (optionname, optionvalue))
		return "<%s.%s%s at 0x%x>" % (self.__class__.__module__, self.__class__.__name__, "".join(options), id(self))

	def fulldesc(self, target, data):
		options = []
		for optionname in ("parser", "base"):
			optionvalue = getattr(self, optionname)
			if optionvalue is not None:
				options.append("%s=%r" % (optionname, optionvalue))
		return ansistyle.Text((target.project.color4action, self.desc()), "(", target.project.strid(target.id), ", ", ", ".join(options), ")")


class XISTConvertAction(Action):
	"""
	<par>This action can be used in a convert chain to transform an
	<pyref module="ll.xist"><app>&xist;</app></pyref> node.</par>
	"""

	def __init__(self, mode=None, target=None, stage=None, lang=None, targetroot=None):
		"""
		<par>Create a new <class>XISTAction</class> object. The arguments will be
		used the create a <pyref module="ll.xist.converters" class="Converter"><class>Converter</class></pyref>
		for each call to <method>execute</method>.</par>
		"""
		super(XISTConvertAction, self).__init__()
		self.mode = mode
		self.target = target
		self.stage = stage
		self.lang = lang
		self.targetroot = targetroot

	def converter(self, maketarget=None):
		"""
		<par>Create a new <pyref module="ll.xist.converters" class="Converter"><class>Converter</class></pyref>
		object to be used by this action. The attributes of this new converter (<lit>mode</lit>, <lit>target</lit>,
		<lit>stage</lit>, etc.) will correspond to those specified in the constructor.</par>
		<par>When the argument <arg>maketarget</arg> is specified it will be used to initialize the
		attribute <lit>maketarget</lit> of the converter.</par>
		"""
		from ll.xist import converters
		return converters.Converter(root=self.targetroot, mode=self.mode, stage=self.stage, target=self.target, lang=self.lang, makeaction=self, maketarget=maketarget)

	def execute(self, target, data):
		"""
		<par>Convert the &xist; node <arg>data</arg> using a converter provided
		by <pyref method="converter"><method>converter</method></pyref>. and
		return the converted node.</par>
		"""
		from ll.xist import xsc
		if not isinstance(data, xsc.Node):
			raise ChainError(target, "need an XIST node as input, got %r" % data)
		return data.convert(self.converter(target))

	def __repr__(self):
		options = []
		for optionname in ("mode", "target", "stage", "lang", "targetroot"):
			optionvalue = getattr(self, optionname)
			if optionvalue is not None:
				options.append(" %s=%r" % (optionname, optionvalue))
		return "<%s.%s%s at 0x%x>" % (self.__class__.__module__, self.__class__.__name__, "".join(options), id(self))

	def fulldesc(self, target, data):
		options = []
		for optionname in ("mode", "target", "stage", "lang", "targetroot"):
			optionvalue = getattr(self, optionname)
			if optionvalue is not None:
				options.append("%s=%r" % (optionname, optionvalue))
		return ansistyle.Text((target.project.color4action, self.desc()), "(", target.project.strid(target.id), ", ", ", ".join(options), ")")


class XISTPublishAction(Action):
	"""
	<par>This action can be used in a convert or write chain to publishe an
	<pyref module="ll.xist"><app>&xist;</app></pyref> node as a string.</par>
	"""

	def __init__(self, publisher=None, base=None):
		"""
		Create an <class>XISTPublishAction</class> object. <arg>publisher</arg> must
		be an instance of <pyref class="ll.xist.publishers.Publisher"><class>ll.xist.publishers.Publisher</class></pyref>.
		If <arg>publisher</arg> is <lit>None</lit> a publisher will be created for you.
		<arg>base</arg> will be the base &url; used for publishing.
		"""
		super(XISTPublishAction, self).__init__()
		if publisher is None:
			from ll.xist import publishers
			publisher = publishers.Publisher()
		self.publisher = publisher
		self.base = base

	def execute(self, target, data):
		"""
		Use <lit><self/>.publisher</lit> to publish the input &xist; node
		<arg>data</arg>. The output data is the generated &xml; string.
		"""
		from ll.xist import xsc
		if not isinstance(data, xsc.Node):
			raise ChainError(target, "need an XIST node as input, got %r" % data)
		return "".join(self.publisher.publish(data, self.base))

	def __repr__(self):
		options = []
		for optionname in ("publisher", "base"):
			optionvalue = getattr(self, optionname)
			if optionvalue is not None:
				options.append(" %s=%r" % (optionname, optionvalue))
		return "<%s.%s%s at 0x%x>" % (self.__class__.__module__, self.__class__.__name__, "".join(options), id(self))

	def fulldesc(self, target, data):
		options = []
		for optionname in ("publisher", "base"):
			optionvalue = getattr(self, optionname)
			if optionvalue is not None:
				options.append("%s=%r" % (optionname, optionvalue))
		return ansistyle.Text((target.project.color4action, self.desc()), "(", target.project.strid(target.id), ", ", ", ".join(options), ")")


class XISTTextAction(Action):
	"""
	<par>This action can be used in a convert or write chain to create a
	plain text version of an &html; <pyref module="ll.xist"><app>&xist;</app></pyref> node.</par>
	"""

	def execute(self, target, data):
		from ll.xist import xsc
		if not isinstance(data, xsc.Node):
			raise ChainError(target, "need an XIST node as input, got %r" % data)
		return data.asText()


class FOPAction(Action):
	"""
	This action can be used in a convert chain. It transforms an &xml; string
	(containing XSL-FO) into &pdf;. For it to work Apache FOP is required. The
	command line is hardcoded but it's simple to overwrite the class attribute
	<lit>command</lit> in a subclass.
	"""
	command = "/usr/local/src/fop-0.20.5/fop.sh -q -c /usr/local/src/fop-0.20.5/conf/userconfig.xml -fo %s -pdf %s"

	def execute(self, target, data):
		"""
		Convert the input <arg>data</arg> (which must be an &xml; string containing
		XSL-FO into &pdf;. The output data will be the &pdf; file as a string.
		"""
		(infd, inname) = tempfile.mkstemp(suffix=".fo")
		(outfd, outname) = tempfile.mkstemp(suffix=".pdf")
		try:
			infile = os.fdopen(infd, "wb")
			os.fdopen(outfd).close()
			infile.write(data)
			infile.close()
			os.system(self.command % (inname, outname))
			data = open(outname, "rb").read()
		finally:
			os.remove(inname)
			os.remove(outname)
		return data


class DecodeAction(Action):
	"""
	<par>This action decodes an input <class>str</class> object into an output
	<class>unicode</class> object.</par>
	"""

	def __init__(self, encoding=None):
		super(DecodeAction, self).__init__()
		if encoding is None:
			encoding = sys.getdefaultencoding()
		self.encoding = encoding

	def execute(self, target, data):
		if not isinstance(data, str):
			raise ChainError(target, "need a str object as input, got %r" % data)
		return data.decode(self.encoding)

	def fulldesc(self, target, data):
		return ansistyle.Text((target.project.color4action, self.desc()), "(", target.project.strid(target.id), ", encoding=%r)" % self.encoding)


class EncodeAction(Action):
	"""
	<par>This action encodes an input <class>unicode</class> object into an
	output <class>str</class> object.</par>
	"""

	def __init__(self, encoding=None):
		super(EncodeAction, self).__init__()
		if encoding is None:
			encoding = sys.getdefaultencoding()
		self.encoding = encoding

	def execute(self, target, data):
		if not isinstance(data, unicode):
			raise ChainError(target, "need a unicode object as input, got %r" % data)
		return data.encode(self.encoding)

	def fulldesc(self, target, data):
		return ansistyle.Text((target.project.color4action, self.desc()), "(", target.project.strid(target.id), ", encoding=%r)" % self.encoding)


class TOXICAction(Action):
	"""
	<par>This action can be used in a convert chain to transform an &xml; string
	into an Oracle procedure body via <pyref module="ll.toxic"><module>ll.toxic</module></pyref>.</par>
	"""

	def execute(self, target, data):
		"""
		The input <arg>data</arg> must be an &xml; string (as a <class>unicode</class>
		object). The output data will be the Oracle procedure body generated by
		<module>ll.toxic</module>.
		"""
		if not isinstance(data, unicode):
			raise ChainError(target, "need a unicode object as input, got %r" % data)
		from ll import toxic
		return toxic.xml2ora(data)


class TOXICPrettifyAction(Action):
	"""
	<par>This action can be used in a convert chain. It tries to fix the
	indentation of a PL/SQL snippet via
	<pyref module="ll.toxic" function="prettify"><function>prettify</function></pyref>.</par>
	"""

	def execute(self, target, data):
		"""
		The input <arg>data</arg> must be a string containing the body of an
		Oracle PL/SQL procedure. The output data will be the same procedure core
		but with indentation fixed.
		"""
		if not isinstance(data, basestring):
			raise ChainError(target, "need a string as input, got %r" % data)
		from ll import toxic
		return toxic.prettify(data)


class SplatAction(Action):
	"""
	<par>This action transforms an input string by replacing certain regular expressions.</par>
	"""

	def __init__(self, *patterns):
		"""
		<par>Create a new <class>SplatAction</class> instance. <arg>patterns</arg>
		are pattern pairs. Each first entry will be replaced by the corresponding
		second entry.</par>
		"""
		super(SplatAction, self).__init__()
		self.patterns = patterns

	def execute(self, target, data):
		"""
		The input must be a string. The output data will be the new string with
		replacements.
		"""
		if not isinstance(data, basestring):
			raise ChainError(target, "need an string as input, got %r" % data)
		for (search, replace) in self.patterns:
			data = re.sub(search, replace, data)
		return data

	def __repr__(self):
		return "<%s.%s patterns=%r at 0x%x>" % (self.__class__.__module__, self.__class__.__name__, self.patterns, id(self))


class XPITAction(Action):
	"""
	<par>This action transform an input string via <pyref module="ll.xpit"><app>xpit</app></pyref>.</par>
	"""

	def loadnamespace(self, target):
		"""
		<par>Import all the source namespaces (i.e. all the input targets of <arg>target</arg>
		that are instances of <pyref class="PythonTarget"><class>PythonTarget</class></pyref>).</par>
		<par>The first module object in the list will be returned.</par>
		"""
		inputs = [ input.getdata() for input in target.iterinputs() if isinstance(input, PythonTarget) ]
		if len(inputs) > 1:
			raise InputError(self, target, inputs)
		elif not inputs:
			return None
		else:
			return inputs[0]

	def execute(self, target, data):
		"""
		<par>Convert the string <arg>data</arg> using
		<pyref module="ll.xpit"><module>ll.xpit</module></pyref>.</par>

		<par>The project, target and action will be passed to the expressions as
		the global variables <lit>makeproject</lit>, <lit>maketarget</lit> and
		<lit>makeaction</lit>. The local namespace will be the one returned from
		<method>loadnamespace</method>.</par>
		"""
		from ll import xpit
		if not isinstance(data, basestring):
			raise ChainError(target, "need a string input")
		globals = dict(makeproject=target.project, maketarget=target, makeaction=self)
		locals = self.loadnamespace(target)
		return xpit.convert(data, globals, locals)


class CommandAction(Action):
	"""
	<par>This action executes a system command (via <function>os.system</function>).</par>
	"""

	def __init__(self, command):
		"""
		<par>Create a new <class>CommandAction</class>. <arg>command</arg> is the command
		that will executed when <pyref method="execute"><method>execute</method></pyref> is called.</par>
		"""
		super(CommandAction, self).__init__()
		self.command = command

	def execute(self, target, data):
		"""
		Execute the action. (<arg>target</arg> and <arg>data</arg> will be ignored.
		The output data is <lit>None</lit>.
		"""
		os.system(self.command)

	def __repr__(self):
		return "<%s.%s command=%r at 0x%x>" % (self.__class__.__module__, self.__class__.__name__, self.command, id(self))

	def fulldesc(self, target, data):
		return ansistyle.Text((target.project.color4action, self.desc()), "(", target.project.strid(target.id), ", command=%r)" % self.command)


class ModeAction(Action):
	"""
	<class>ModeAction</class> can be used in a write chain to change file permissions.
	"""

	def __init__(self, mode=0644):
		"""
		Create an <class>ModeAction</class> instance. <arg>mode</arg>
		(which defaults to <lit>0644</lit>) will be use as the permission bit pattern.
		"""
		super(ModeAction, self).__init__()
		self.mode = mode

	def execute(self, target, data):
		"""
		Change the permission bits of the external representation of <arg>target</arg>.
		<arg>data</arg> will be ignored. The output data is <lit>None</lit>.
		"""
		target.id.chmod(self.mode)

	def __repr__(self):
		return "<%s.%s mode=%s at 0x%x>" % (self.__class__.__module__, self.__class__.__name__, oct(self.mode), id(self))

	def fulldesc(self, target, data):
		return ansistyle.Text((target.project.color4action, self.desc()), "(", target.project.strid(target.id), ", mode=0%o)" % self.mode)


class OwnerAction(Action):
	"""
	<class>OwnerAction</class> can be used in a write chain to change to change
	the user and/or group ownership of a file.
	"""

	def __init__(self, user=None, group=None):
		"""
		Create a new <class>OwnerAction</class> instance. <arg>user</arg> can either be a numerical
		user id or a user name or <lit>None</lit>. If it is <lit>None</lit> no user ownership will
		be changed. The same applies to <arg>group</arg>.
		"""
		super(OwnerAction, self).__init__()
		self.user = user
		self.group = group

	def execute(self, target, data):
		"""
		Change the ownership of the external representation of <arg>target</arg>.
		<arg>data</arg> will be ignored. The output data is <lit>None</lit>.
		"""
		target.id.chown(self.user, self.group)

	def __repr__(self):
		v = []
		if self.user is not None:
			v.append(" user=%r" % self.user)
		if self.group is not None:
			v.append(" group=%r" % self.group)
		return "<%s.%s%s at 0x%x>" % (self.__class__.__module__, self.__class__.__name__, "".join(v), id(self))

	def fulldesc(self, target, data):
		options = []
		for optionname in ("user", "group"):
			optionvalue = getattr(self, optionname)
			if optionvalue is not None:
				options.append("%s=%r" % (optionname, optionvalue))
		return ansistyle.Text((target.project.color4action, self.desc()), "(", target.project.strid(target.id), ", ", ", ".join(options), ")")


class ImportAction(Action):
	"""
	This action will import the target as a Python module.
	"""
	dynamic = True

	def _import(self, target):
		filename = target.id.real().local()

		(path, name) = os.path.split(filename)
		(name, ext) = os.path.splitext(name)
	
		if ext != ".py":
			raise ValueError("Can only import .py files, not %s" % ext)
	
		oldmod = sys.modules.get(name, None) # get any existing module out of the way
		sys.modules[name] = mod = new.module(name) # create module and make sure it can find itself in sys.module
		mod.__file__ = filename

		execfile(filename, mod.__dict__)

		mod = sys.modules.pop(name) # refetch the module if it has replaced itself with a custom object
		if oldmod is not None: # put old module back
			sys.modules[name] = oldmod
		return mod

	def execute(self, target, data):
		"""
		The input <arg>data</arg> will be ignored, the output data will
		be the imported module. All dependencies for this module will be dropped
		(because the module might import different modules now), but the can be recreated
		through <pyref class="UseModuleAction"><class>UseModuleAction</class>s</pyref>.
		"""
		# The module will be reloaded => drop all dependencies (they will be rebuilt during import)
		for dep in target._inputs[:]:
			if isinstance(dep, ImportDep):
				target._inputs.remove(dep)
				dep.input._outputs.remove(dep)

		# Load the module
		try:
			target.project.importstack.append(target)
			module = self._import(target)
		finally:
			target.project.importstack.pop(-1)

		return module


class UseModuleAction(Action):
	"""
	This action will record dependencies if an imported module gets used.
	"""
	dynamic = True

	def execute(self, target, data):
		"""
		Add an <pyref class="ImportDep"><class>ImportDep</class></pyref> dependency
		from <arg>target</arg> to the last target on the import stack. The input
		data will be returned unchanged.
		"""
		if target.project.importstack:
			ImportDep(target, target.project.importstack[-1])
		return data


class NullAction(Action):
	"""
	This action does nothing (it is used as a default, when no action is
	specified in the <pyref class="Target"><class>Target</class></pyref>
	constructor).
	"""
	def __iter__(self):
		if False:
			yield self


class CacheAction(Action):
	"""
	A <class>CacheAction</class> action is a <z>stateful</z> action that will
	cache the result of calling another action
	"""
	def __init__(self, action):
		Action.__init__(self)
		self.action = action
		self.data = _nodata

	def __iter__(self):
		if self.data is _nodata: # we don't have the data yet => call real action
			for action in self.action:
				yield action
		yield self # give ourself the chance to either cache the data or reuse it

	def execute(self, target, data):
		if self.data is _nodata: # We don't have the data yet
			self.data = data # the incoming data is the ouput of the real action
		return self.data

	def dirty(self):
		self.data = _nodata

	def clear(self):
		self.data = _nodata

	def desc(self):
		if self.data is not _nodata:
			return "UseCache"
		else:
			return "Cache"


###
### Classes for target ids (apart from strings for PhonyTargets and URLs for file targets)
###

class DBID(object):
	"""
	<par>This class provides a unique identifier for database content. This
	can be used as an id for <pyref class="Target"><class>Target</class></pyref>
	objects that are not files, but database records, function, procedures etc.</par>
	"""
	name = None

	def __init__(self, connection, type, name, key=None):
		"""
		<par>Create a new <class>DBID</class> instance. Arguments are:</par>
		<dlist>
		<term><arg>connection</arg></term>
		<item>A string that specifies the connection to the database.
		E.g. <lit>"user/pwd@db.host.com"</lit> for Oracle.</item>
		<term><arg>type</arg></term>
		<item>The type of the object. Values may be <lit>"table"</lit>,
		<lit>"view"</lit>, <lit>"function"</lit>, <lit>"procedure"</lit> etc.</item>
		<term><arg>name</arg></term>
		<item>The name of the object</item>
		<term><arg>key</arg></term>
		<item>If <arg>name</arg> refers to a table, <arg>key</arg> can be used
		to specify a row in this table.</item>
		</dlist>
		"""
		self.connection = connection
		self.type = type
		self.name = name
		self.key = key

	def __eq__(self, other):
		res = self.__class__ == other.__class__
		if not res:
			res = self.connection==other.connection and self.type==other.type and self.name==other.name and self.key==other.key
		return res

	def __hash__(self):
		return hash(self.connection) ^ hash(self.type) ^ hash(self.name) ^ hash(self.key)

	def __repr__(self):
		args = []
		for attrname in ("connection", "type", "name", "key"):
			attrvalue = getattr(self, attrname)
			if attrvalue is not None:
				args.append("%s=%r" % (attrname, attrvalue))
		return "%s(%s)" % (self.__class__.__name__, ", ".join(args))

	def __str__(self):
		s = "%s:%s|%s:%s" % (self.__class__.name, self.connection, self.type, self.name)
		if self.key is not None:
			s += "|%s" % (self.key,)
		return s


class OracleID(DBID):
	name = "oracle"

	def openwrite(self):
		return OracleWriteResource(self)

	def openread(self):
		return OracleReadResource(self)


class OracleResource(object):
	def __init__(self, loc):
		self.loc = loc

	def _cursor(self):
		"""
		Create a database cursor for this connection
		"""
		import cx_Oracle
		db = cx_Oracle.connect(self.loc.connection)
		return db.cursor()

	def __repr__(self):
		return "<%s instance for %r at 0x%x>" % (self.__class__.__name__, self.loc, id(self))


class OracleWriteResource(OracleResource):
	def __init__(self, loc):
		OracleResource.__init__(self, loc)
		self.stream = None

	def __getattr__(self, attrname):
		if self.stream is None:
			self.stream = cStringIO.StringIO()
			if self.loc.type in ("function", "procedure"):
				self.stream.write("create or replace %s %s\n" % (self.loc.type, self.loc.name))
			else:
				raise ValueError("don't know how to handle %r" % self.loc)
		return getattr(self.stream, attrname)

	def __del__(self):
		self.close()

	def close(self):
		if self.stream is not None:
			c = self._cursor()
			c.execute(self.stream.getvalue())
			self.stream = None


class OracleReadResource(OracleResource):
	def __init__(self, loc):
		OracleResource.__init__(self, loc)
		self.stream = None

	def __getattr__(self, attrname):
		if self.stream is None:
			if self.loc.type not in ("function", "procedure"):
				raise ValueError("don't know how to handle %r" % self.loc)
			c = self._cursor()
			c.execute("select text from user_source where lower(name)=lower(:name) and type='%s' and line>1 order by line" % self.loc.type.upper(), name=self.loc.name)
			rows = c.fetchall()
			if not rows:
				raise IOError(errno.ENOENT, "no such %s: %s" % (self.loc.type, self.loc.name))
			self.stream = cStringIO.StringIO("".join([row[0] for row in rows]))
		return getattr(self.stream, attrname)


###
### The project class
###

class Project(dict):
	"""
	<par>A <class>Project</class> collects all <pyref class="Target"><class>Target</class></pyref>s
	from a project. It is responsible for initiating the build process and for generating a report about
	the progress of the build process.</par>
	"""
	def __init__(self, showsummary=None, showtarget=None, showaction=None, showactionfull=None, showtime=None, showdata=None):
		super(Project, self).__init__()
		self.targetsrebuilt = 0
		self.targetsfailed = 0
		self.showsummary = self._getenvbool("LL_MAKE_SHOWSUMMARY", showsummary, True)
		self.showtarget = self._getenvbool("LL_MAKE_SHOWTARGET", showtarget, True)
		self.showaction = self._getenvbool("LL_MAKE_SHOWACTION", showaction, True)
		self.showactionfull = self._getenvbool("LL_MAKE_SHOWACTIONFULL", showactionfull, True)
		self.showdata = self._getenvbool("LL_MAKE_SHOWDATA", showdata, False)
		self.showtime = self._getenvbool("LL_MAKE_SHOWTIME", showtime, True)
		self.ignoreerrors = False
		repransi = os.getenv("LL_MAKE_REPRANSI")
		if repransi is None:
			repransi = 0
		else:
			repransi = int(repransi)
			if not sys.platform.startswith("linux") and not sys.platform.startswith("darwin"):
				repransi = 0
		self.repransi = repransi
		self._initcolors()
		self.maxinputreport = 2
		self.__built = False # remember whether build() has been called, so we can reset timestamps on the second call
		self.here = None # cache the current directory during builds (used for shortening URLs)
		self.home = None # cache the home directory during builds (used for shortening URLs)
		self.stack = [] # keep track of the recursion during calls to Target.update()/Target.getdata()
		self.importstack = [] # keep track of recursive imports
		self.chars4tree = "|"
		self.chars4target = "=="
		self.chars4convert = "@@"
		self.chars4write = "<<"
		self.chars4read = ">>"
		self.chars4use = "--"
		self.chars4inputdep = "<<"
		self.chars4outputdep = ">>"

	def __repr__(self):
		return "<%s.%s with %d targets at 0x%x>" % (self.__module__, self.__class__.__name__, len(self), id(self))

	def _getenvbool(self, name, value, default):
		if value is not None:
			return value
		return bool(int(os.environ.get(name, default)))

	def _getenvcolors(self, name, default1, default2):
		if name in os.environ:
			return int(os.environ.get(name), 0)
		elif self.repransi == 1: # light background
			return default1
		elif self.repransi == 2: # dark background
			return default2
		else:
			return -1

	def _initcolors(self):
		"""
		<par>initialize the color classes which are used for the various formatting
		methods.</par>
		"""
		self.color4tree = self._getenvcolors("LL_MAKE_REPRANSI_TREE", 0170, 0170)
		self.color4chain = self._getenvcolors("LL_MAKE_REPRANSI_CHAIN", 0100, 0100)
		self.color4progress = self._getenvcolors("LL_MAKE_REPRANSI_PROGRESS", -1, -1)
		self.color4dep = self._getenvcolors("LL_MAKE_REPRANSI_DEP", 0070, 0070)
		self.color4target = self._getenvcolors("LL_MAKE_REPRANSI_TARGET", 0110, 0110)
		self.color4id = self._getenvcolors("LL_MAKE_REPRANSI_ID", 0140, 0120)
		self.color4action = self._getenvcolors("LL_MAKE_REPRANSI_ACTION", 0020, 0130)
		self.color4time = self._getenvcolors("LL_MAKE_REPRANSI_TIME", 0050, 0030)
		self.color4data = self._getenvcolors("LL_MAKE_REPRANSI_DATA", 0060, 0160)
		self.color4ellipsis = self._getenvcolors("LL_MAKE_REPRANSI_ELLIPSIS", 0100, 0100)
		self.color4size = self._getenvcolors("LL_MAKE_REPRANSI_SIZE", 0060, 0160)
		self.color4done = self._getenvcolors("LL_MAKE_REPRANSI_DONE", 0170, 0170)
		self.color4error = self._getenvcolors("LL_MAKE_REPRANSI_ERROR", 0110, 0110)
		self.color4note = self._getenvcolors("LL_MAKE_REPRANSI_NOTE", 0170, 0170)
		self.color4ref = self._getenvcolors("LL_MAKE_REPRANSI_NOTE", 0060, 0160)

	def strseconds(self, delta):
		"""
		<par>return a nicely formatted and colored string for
		the <class>datetime.timedelta</class> value <arg>delta</arg>. <arg>delta</arg>
		may also be <lit>None</lit> in with case <lit>"0"</lit> will be returned.</par>
		"""
		if delta is None:
			text = "0"
		else:
			rest = delta.seconds
	
			(rest, secs) = divmod(rest, 60)
			(rest, mins) = divmod(rest, 60)
			rest += delta.days*24
	
			secs += delta.microseconds/1000000.
			if rest:
				text = "%d:%02d:%06.3fh" % (rest, mins, secs)
			elif mins:
				text = "%02d:%06.3fm" % (mins, secs)
			else:
				text = "%.3fs" % secs
		return ansistyle.Text(self.color4time, text)

	def strsize(self, bytes):
		"""
		<par>return a nicely formatted and colored string for
		the byte count value <arg>bytes</arg>.</par>
		"""
		return ansistyle.Text(self.color4size, "%db" % bytes)

	def strerror(self, text):
		"""
		<par>return a nicely formatted and colored string for
		the error text <arg>text</arg>.</par>
		"""
		return ansistyle.Text(self.color4error, text)

	def strdep(self, dep):
		"""
		<par>return a nicely formatted and colored string for
		the dependency <arg>dep</arg>.</par>
		"""
		if isinstance(dep, OrderedDep):
			s = "OrderedDep(%s)" % dep.order
		else:
			s = dep.__class__.__name__
		return ansistyle.Text(self.color4dep, s)

	def strid(self, id):
		"""
		<par>return a nicely formatted and colored string for
		the target id <arg>id</arg>.</par>
		"""
		if isinstance(id, url.URL) and id.islocal():
			if self.here is None:
				self.here = url.here()
			if self.home is None:
				self.home = url.home()
			s = str(id)
			test = str(id.relative(self.here))
			if len(test) < len(s):
				s = test
			test = "~/%s" % id.relative(self.home)
			if len(test) < len(s):
				s = test
		else:
			s = str(id)
		return ansistyle.Text(self.color4id, s)

	def strtarget(self, target):
		"""
		<par>return a nicely formatted and colored string for
		the target <arg>target</arg>.</par>
		"""
		try:
			name = target.__class__.name
		except AttributeError:
			name = target.__class__.__name__

		return ansistyle.Text(self.color4target, name, "(", self.strid(target.id), ")")

	def __setitem__(self, id, target):
		"""
		<par>set the target with the id <arg>name</arg>.</par>
		"""
		if id in self:
			self.reportWarning(RedefinedTargetWarning(id), 5)
		if isinstance(id, url.URL) and id.islocal():
			id = id.abs(scheme="file")
		super(Project, self).__setitem__(id, target)

	def __candidates(self, id):
		"""
		Return candidates for alternative forms of <arg>id</arg>.
		This is a generator, so when the first suitable candidate is used, the
		rest of the candidates won't have to be created at all.
		"""
		yield id
		id2 = id
		if isinstance(id, basestring):
			id2 = url.URL(id)
			yield id2
		if isinstance(id2, url.URL):
			id2 = id2.abs(scheme="file")
			yield id2
			id2 = id2.real(scheme="file")
			yield id2
		if isinstance(id, basestring) and ":" in id:
			(prefix, rest) = id.split(":", 1)
			if prefix == "oracle":
				if "|" in rest:
					(connection, rest) = rest.split("|", 1)
					if ":" in rest:
						(type, name) = rest.split(":", 1)
						if "|" in rest:
							(name, key) = rest.split("|")
						else:
							key = None
						yield OracleID(connection, type, name, key)

	def __getitem__(self, id):
		"""
		<par>return the target with the id <arg>id</arg>.</par>
		<par>If an id can't be found, it will be wrapped in a
		<pyref module="ll.url" class="URL"><class>URL</class></pyref> instance and retried.</par>
		"""
		sup = super(Project, self)
		for id2 in self.__candidates(id):
			try:
				return sup.__getitem__(id2)
			except KeyError:
				pass
		raise UndefinedTargetError(id)

	def has_key(self, id):
		"""
		<par>Return whether the target with the id <arg>id</arg>
		exists in the project.</par>
		"""
		return id in self

	def __contains__(self, id):
		"""
		<par>Return whether the target with the id <arg>id</arg>
		exists in the project.</par>
		"""
		sup = super(Project, self)
		for id2 in self.__candidates(id):
			has = sup.has_key(id2)
			if has:
				return True
		return False

	def destroy(self):
		"""
		<par>Removes all targets from <self/>. If you keep external references
		to targets they will be worthless, because the dependencies between
		target will have been removed.</par>
		"""
		for target in self.itervalues():
			target.destroy()
		dict.clear(self)

	def create(self):
		"""
		<par>Create all dependencies for the project. Overwrite in subclasses.</par>

		<par>This method should only be called once, otherwise you'll get lots of
		<pyref class="RedefinedTargetWarning"><class>RedefinedTargetWarning</class>s</pyref>.
		But you can call <pyref method="destroy"><method>destroy</method></pyref> to
		remove all targets before calling <method>create</method>. You can also
		use the method <pyref method="recreate"><method>recreate</method></pyref> for that.</par>
		"""

	def recreate(self):
		"""
		<par>Calls <pyref method="destroy"><method>destroy</method></pyref> and
		<pyref method="create"><method>create</method></pyref> to recreate
		all project dependencies.</par>
		"""
		self.destroy()
		self.create()

	def optionparser(self):
		"""
		Return an <module>optparse</module> parser from parsing the command line
		options. This can be overwritten in subclasses to add more options.
		"""
		p = optparse.OptionParser(usage="usage: %prog [options] [targets]", version="%%prog %s" % __version__)
		p.add_option("-v", "--verbosity", dest="verbosity", metavar="VERB", help="Verbosity of progress report: 'ioactds' lowercase activates, uppercase deactivates (t=targets, a=actions, f=full actions, z=time, d=data, s=summary)", default="")
		p.add_option("-x", "--ignore", dest="ignoreerrors", help="Ignore errors", action="store_true", default=None)
		p.add_option("-X", "--noignore", dest="ignoreerrors", help="Don't ignore errors", action="store_false", default=None)
		p.add_option("-c", "--color", dest="color", help="Use colored output", action="store_true", default=None)
		p.add_option("-C", "--nocolor", dest="color", help="No colored output", action="store_false", default=None)
		return p

	def parseoptions(self, commandline=None):
		"""
		Use the parser returned by <pyref method="optionparser"><method>optionparser</method></pyref>
		to parse the option sequence <arg>commandline</arg>, modify <self/> accordingly and return
		the result of <module>optparse</module>s <method>parse_args</method> call.
		"""
		p = self.optionparser()
		(options, args) = p.parse_args(commandline)
		for c in options.verbosity:
			if c=="t":
				self.showtarget = True
			elif c=="T":
				self.showtarget = False
			elif c=="a":
				self.showaction = True
			elif c=="A":
				self.showaction = False
			elif c=="f":
				self.showactionfull = True
			elif c=="F":
				self.showactionfull = False
			elif c=="z":
				self.showtime = True
			elif c=="Z":
				self.showtime = False
			elif c=="d":
				self.showdata = True
			elif c=="D":
				self.showdata = False
			elif c=="s":
				self.showsummary = True
			elif c=="S":
				self.showsummary = False
		if options.ignoreerrors is not None:
			self.ignoreerrors = options.ignoreerrors
		if options.color is not None:
			self.color = options.color
		return (options, args)

	def clear(self):
		"""
		Reset build info.
		"""
		self.targetsrebuilt = 0
		self.targetsfailed = 0
		if self.__built:
			for target in self.itervalues():
				target.clear()

	def build(self, *targets):
		"""
		<par>build all targets in <arg>targets</arg>.</par>
		
		<par>Items in <arg>targets</arg> must be <pyref class="Target"><class>Target</class></pyref>
		instances or target ids.</par>

		<par>This method can be called multiple times and will recheck modification timestamp
		on each call.</par>
		"""
		t1 = datetime.datetime.utcnow()
		self.clear()
		self.stack = []
		self.importstack = []
		try:
			for target in targets:
				if not isinstance(target, Target):
					target = self[target]
				target.update()
			t2 = datetime.datetime.utcnow()
			if self.showsummary:
				self.report(
					ansistyle.Text(
						self.color4progress,
						"built ",
						(self.color4target, self.__class__.__name__),
						" ",
						self.strseconds(t2-t1),
						" (",
						(self.color4data, str(len(self))),
						" targets; ",
						(self.color4data, str(self.targetsrebuilt)),
						" rebuilt; ",
						(self.color4data, str(self.targetsfailed)),
						" failed)\n",
					)
				)
		finally:
			self.__built = True # remember the call here, so targets will be set cleared on the next call
			self.here = None
			self.home = None
			self.stack = []
			self.importstack = []

	def reportphonytargets(self, stream=None):
		"""
		Show a list of all <pyref class="PhonyTarget"><class>PythonTarget</class></pyref>
		and their documentation.
		"""
		if stream is None:
			stream = sys.stdout
		phonies = []
		maxlen = 0
		for id in self:
			if isinstance(id, basestring):
				maxlen = max(maxlen, len(id))
				phonies.append(self[id])
		phonies.sort(key=operator.attrgetter("id"))
		for phony in phonies:
			text = ansistyle.Text(self.strtarget(phony))
			if phony.doc:
				text.append(" ", (self.color4tree, "."*(maxlen+3-len(phony.id))), " ", phony.doc)
			text.append("\n")
			stream.write(str(text))

	def buildwithargs(self, commandline=None):
		"""
		For calling make scripts from the command line. <arg>commandline</arg> defaults to <lit>sys.argv[1:]</lit>.
		"""
		if not commandline:
			commandline = sys.argv[1:]
		(options, args) = self.parseoptions(commandline)

		if args:
			self.build(*args)
		else:
			print "Available phony targets are:"
			self.reportphonytargets()

	def report(self, *texts):
		"""
		All screen output is done through this method. This makes it possible to redirect
		the output (e.g. to logfiles) in subclasses.
		"""
		for text in texts:
			sys.stderr.write(str(text))
		sys.stderr.flush()

	def reportError(self, *texts):
		"""
		Report an error
		"""
		self.report(*texts)

	def reportWarning(self, warning, stacklevel):
		"""
		Issue a warning through the Python warnings framework
		"""
		warnings.warn(warning, stacklevel=stacklevel)


# This will be set to the project in build()
currentproject = None
