#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

## Copyright 2002-2006 by LivingLogic AG, Bayreuth/Germany.
## Copyright 2002-2006 by Walter Dörwald
##
## All Rights Reserved
##
## See __init__.py for the license


"""
<par><module>ll.make</module> provides tools for building projects.</par>

<par>Like <app>make</app> it allows you to specify dependencies between files
and actions to be executed when files don't exist or are out of date with
respect to one of their sources. But unlike <app>make</app> you can do this
in an object oriented way and targets are not only limited to files.</par>

<par>Relevant classes are:</par>
<ulist>
<item><pyref class="Project"><class>Project</class></pyref>, which is the
container for all actions in a project,</item>
<item><pyref class="Action"><class>Action</class></pyref> (and subclasses),
which are used to transform input data and read and write files (or other
entities like database records).</item>
</ulist>

<par>A simple script that copies a file <filename>foo.txt</filename> to
<filename>bar.txt</filename> reencoding it from <lit>"latin-1"</lit> to
<lit>"utf-8"</lit> in the process looks like this:</par>

<prog>
from ll import make, url

class MyProject(make.Project):
	def create(self):
		make.Project.create(self)
		source = self.add(make.FileAction(url.File("foo.txt")))
		target = self.add(
			source /
			make.DecodeAction("iso-8859-1") /
			make.EncodeAction("utf-8") /
			make.FileAction(url.File("bar.txt"))
		)
		self.writecreatedone()

p = MyProject()
p.create()

if __name__ == "__main__":
	p.build("bar.txt")
</prog>
"""

__version__ = "$Revision: 1.82 $"[11:-1]


import sys, os, os.path, optparse, warnings, re, datetime, cStringIO, errno, tempfile, operator, new, cPickle

from ll import misc, astyle, url


###
### Constants and helpers
###

nodata = misc.Const("nodata") # marker object for "no new data available"
newdata = misc.Const("newdata") # marker object for "new data available"

bigbang = datetime.datetime(1900, 1, 1) # there can be no timestamp before this one
bigcrunch = datetime.datetime(3000, 1, 1) # there can be no timestamp after this one


def filechanged(key):
	"""
	Get the last modified date (or <lit>bigbang</lit>, if the file doesn't exist).
	"""
	try:
		return key.mdate()
	except (IOError, OSError):
		return bigbang


class Level(object):
	"""
	Stores information about the recursive execution of <pyref class="Action"><class>Action</class>s</pyref>.
	"""
	__slots__ = ("action", "since", "infoonly", "reported")

	def __init__(self, action, since, infoonly, reported=False):
		self.action = action
		self.since = since
		self.infoonly = infoonly
		self.reported = reported

	def __repr__(self):
		return "<%s.%s object action=%r since=%r infoonly=%r reported=%r at 0x%x>" % (self.__class__.__module__, self.__class__.__name__, self.action, self.since, self.infoonly, self.reported, id(self))


def report(func):
	"""
	<par>Standard decorator for <pyref class="Action" method="get"><method>Action.get</method></pyref> methods.</par>

	<par>This decorator handles proper reporting of nested action calls.
	If it isn't used, only the output of calls to
	<pyref class="Project" method="writestep"><method>Project.writestep</method></pyref>
	will be visible to the user.
	"""
	def reporter(self, project, since, infoonly):
		reported = False
		show = project.showaction is not None and isinstance(self, project.showaction)
		if show:
			if project.showidle and (not infoonly or project.showinfoonly):
				args = ["Starting ", project.straction(self)]
				if project.showtimestamps:
					args.append(" since ")
					args.append(project.strdatetime(since))
					if infoonly:
						args.append(" (info only)")
				project.writestack(*args)
				reported = True
			project.stack.append(Level(self, since, infoonly, reported))
		t1 = datetime.datetime.utcnow()
		try:
			data = func(self, project, since, infoonly)
		except (KeyboardInterrupt, SystemExit):
			raise
		except Exception, exc:
			project.actionsfailed += 1
			if project.ignoreerrors: # ignore changes in failed subgraphs
				data = nodata # Return "everything is up to date" in this case
				error = exc.__class__
			else:
				raise
		else:
			project.actionscalled += 1
			error = None
		t2 = datetime.datetime.utcnow()
		if show or error is not None:
			if (not project.showidle and data is not nodata and (data is not newdata or project.showinfoonly)) or error is not None:
				project._writependinglevels() # Only outputs something if the action hasn't called writestep()
			reported = project.stack[-1].reported
			if show:
				project.stack.pop(-1)
			if reported:
				if error is not None:
					text = "Canceled"
				else:
					text = "Finished"
				args = [text, " ", project.straction(self)]
				if project.showtime:
					args.append(" in ")
					args.append(project.strtimedelta(t2-t1))
				if project.showdata:
					args.append(": ")
					if error is not None:
						if error.__module__ != "exceptions":
							text = "%s.%s" % (error.__module__, error.__name__)
						else:
							text = error.__name__
						args.append(s4error(text))
					elif data is nodata:
						args.append("nodata")
					elif data is newdata:
						args.append("newdata")
					elif isinstance(data, str):
						args.append(s4data("str (%db)" % len(data)))
					elif isinstance(data, unicode):
						args.append(s4data("unicode (%dc)" % len(data)))
					else:
						dataclass = data.__class__
						if dataclass.__module__ != "__builtin__":
							text = "%s.%s @ 0x%x" % (dataclass.__module__, dataclass.__name__, id(data))
						else:
							text = "%s @ 0x%x" % (dataclass.__name__, id(data))
						args.append(s4data(text))
				project.writestack(*args)
		return data
	reporter.__dict__.update(func.__dict__)
	reporter.__doc__ = func.__doc__
	reporter.__name__ = func.__name__
	return reporter


###
### exceptions & warnings
###

class MakeWarning(Warning):
	"""
	Base class for all warnings in <module>ll.make</module>.
	"""


class RedefinedTargetWarning(MakeWarning):
	"""
	Warning that will be issued when a target is added to a project and a target
	with the same key already exists.
	"""

	def __init__(self, key):
		self.key = key

	def __str__(self):
		return "target with key=%r redefined" % self.key


class UndefinedTargetError(KeyError):
	"""
	Exception that will be raised when a target with the specified key doesn't
	exist within the project.
	"""

	def __init__(self, key):
		self.key = key

	def __str__(self):
		return "target %r undefined" % self.key


###
### Actions
###

def _ipipe_type(obj):
	try:
		return obj.type
	except AttributeError:
		return "%s.%s" % (obj.__class__.__module__, obj.__class__.__name__)
_ipipe_type.__xname__ = "type"


def _ipipe_key(obj):
	return obj.getkey()
_ipipe_key.__xname__ = "key"


class Action(object):
	"""
	<par>An <class>Action</class> is responsible for transforming input data
	into output data.</par>
	"""

	def __init__(self):
		"""
		<par>Create a new <class>Action</class> instance.</par>
		"""

	def __div__(self, output):
		return output.__rdiv__(self)

	@misc.notimplemented
	def get(self, project, since, infoonly):
		"""
		<par>This method (i.e. the implementations in subclasses) is the workhorse
		of <module>ll.make</module>. <method>get</method> must return the output
		data of the action if this data has changed since <arg>since</arg>
		(which is a <class>datetime.datetime</class> object in UTC). If the data
		hasn't changed since <arg>since</arg> the special object <lit>nodata</lit>
		must be returned.</par>
		
		<par>In both cases the action must make sure that the data is internally
		consistent, i.e. if the input data is the output data of other actions
		<self/> has to ensure that those other actions update their data too,
		independent from the fact whether <method>get</method> will return new
		data or not.</par>

		<par>Two special values can be passed for <arg>since</arg>:</par>

		<dlist>
		<term><lit>bigbang</lit></term>
		<item>This timestamp is older than any timestamp that can appear in
		real life. Since all data is newer than this, <method>get</method> must
		always return output data.</item>
		<term><lit>bigcrunch</lit></term>
		<item>This timestamp is newer than any timestamp that can appear in
		real life. Since there can be no data newer than this, <method>get</method>
		can only return output data in this case if ensuring internal consistency
		resulted in new data.</item>
		</dlist>
	
		<par>If <arg>infoonly</arg> is true <method>get</method> must return the
		constant <lit>newdata</lit> instead of real data, if any new data is
		available.</par>
		"""

	def getkey(self):
		"""
		Get the nearest key from <self/> or its inputs. This is used by
		<pyref class="ModuleAction"><class>ModuleAction</class></pyref> for the
		filename.
		"""
		return getattr(self, "key", None)

	@misc.notimplemented
	def __iter__(self):
		"""
		Return an iterator over the input actions of <self/>.
		"""

	def iterallinputs(self):
		"""
		Return an iterator over all input actions of <self/> (i.e. recursively).
		"""
		for input in self:
			yield input
			for subinput in input.iterallinputs():
				yield subinput

	def findpaths(self, input):
		"""
		Find dependency paths leading from <self/> to the other action <arg>input</arg>.
		I.e. if <self/> depends directly or indirectly on <arg>input</arg>, this
		generator will produce all paths <lit>p</lit> where <lit>p[0] is <self/></lit>
		and <lit>p[-1] is <arg>input</arg></lit> and <lit>p[i+1] in p[i]</lit> for all
		<lit>i</lit> in <lit>xrange(len(p)-1)</lit>.
		"""
		if input is self:
			yield [self]
		else:
			for myinput in self:
				for path in myinput.findpaths(input):
					yield [self] + path

	def __xattrs__(self, mode="default"):
		if mode == "default":
			return (_ipipe_type, _ipipe_key)
		return dir(self)

	def __xrepr__(self, mode="default"):
		if mode in ("cell", "default"):
			name = self.__class__.__name__
			if name.endswith("Action"):
				name = name[:-6]
			yield (s4action, name)
			if hasattr(self, "key"):
				yield (astyle.style_default, "(")
				key = self.key
				if isinstance(key, url.URL) and key.islocal():
					here = url.here()
					home = url.home()
					s = str(key)
					test = str(key.relative(here))
					if len(test) < len(s):
						s = test
					test = "~/%s" % key.relative(home)
					if len(test) < len(s):
						s = test
				else:
					s = str(key)
				yield (s4key, s)
				yield (astyle.style_default, ")")
		else:
			yield (astyle.style_default, repr(self))


class PipeAction(Action):
	"""
	A <class>PipeAction</class> depends on exactly one input action and transforms
	the input data into output data.
	"""
	def __init__(self, input=None):
		Action.__init__(self)
		self.input = input

	def __rdiv__(self, input):
		"""
		Register the action <arg>input</arg> as the input action for <self/> and
		return <self/> (which enables chaining <class>PipeAction</class> objects).
		"""
		self.input = input
		return self

	def getkey(self):
		return self.input.getkey()

	def __iter__(self):
		if self.input is not None:
			yield self.input

	@misc.notimplemented
	def execute(self, project, data):
		"""
		Execute the action: transform the input data <arg>data</arg> and return
		the resulting output data. This method must be implemented in subclasses.
		"""

	@report
	def get(self, project, since, infoonly):
		data = self.input.get(project, since, infoonly)
		if data is not nodata and not infoonly:
			data = self.execute(project, data)
		return data


class CollectAction(PipeAction):
	"""
	A <class>CollectAction</class> is a <class>PipeAction</class> that simply
	outputs its input data unmodified, but updates a number of other actions
	in the process.
	"""
	def __init__(self, input=None):
		PipeAction.__init__(self, input)
		self.inputs = []

	def addinputs(self, *inputs):
		"""
		Register all actions in <arg>inputs</arg> as additional actions that
		have to be updated before <self/> is updated.
		"""
		self.inputs.extend(inputs)
		return self

	def __iter__(self):
		if self.input is not None:
			yield self.input
		for input in self.inputs:
			yield input

	@report
	def get(self, project, since, infoonly):
		inputsince = since
		for input in self.inputs:
			# We don't need the data itself, so pass True for infoonly
			data = input.get(project, since, True)
			if data is not nodata:
				inputsince = bigbang
		data = self.input.get(project, inputsince, infoonly)
		return data

	def __repr__(self):
		return "<%s.%s object at 0x%x>" % (self.__class__.__module__, self.__class__.__name__, id(self))


class PhonyAction(Action):
	"""
	A <class>PhonyAction</class> doesn't do anything. It may depend on any
	number of additonal input actions which will be updated when this action
	gets updated. If there's new data from any of these actions, a
	<class>PhonyAction</class> will return <lit>None</lit> (and <lit>nodata</lit>
	otherwise as usual).
	"""
	def __init__(self, doc=None):
		"""
		Create a <class>PhonyAction</class> object. <arg>doc</arg> describes the
		action and is printed by
		<pyref class="Project" method="writephonytargets"><method>Project.writephonytargets</method></pyref>.
		"""
		Action.__init__(self)
		self.doc = doc
		self.inputs = []
		self.data = nodata
		self.buildno = None

	def addinputs(self, *inputs):
		"""
		Register all actions in <arg>inputs</arg> as additional actions that
		have to be updated once <self/> is updated.
		"""
		self.inputs.extend(inputs)
		return self

	def __iter__(self):
		for input in self.inputs:
			yield input

	@report
	def get(self, project, since, infoonly):
		# Caching the result object of a PhonyAction is cheap (it's either None or nodata),
		# so we always do the caching as this optimizes away the traversal of a complete subgraph
		# for subsequent calls to get() during the same build round
		if self.buildno != project.buildno:
			result = nodata
			for input in self.inputs:
				data = input.get(project, since, True)
				if data is not nodata:
					self.data = None
					result = None
					if infoonly:
						result = newdata
			self.buildno = project.buildno
			return result
		return self.data

	def __repr__(self):
		s = "<%s.%s object" % (self.__class__.__module__, self.__class__.__name__)
		if hasattr(self, "key"):
			s += " with key=%r" % self.key
		s += " at 0x%x>" % id(self)
		return s


class FileAction(PipeAction):
	"""
	A <class>FileAction</class> is used for reading and writing files
	(and other objects providing the appropriate interface).
	"""
	def __init__(self, key, input=None):
		"""
		Create a <class>FileAction</class> object with <arg>key</arg> as the <z>filename</z>.
		<arg>key</arg> must be an object that provides a method <method>open</method>
		for opening readable and writable streams to the file.
		
		"""
		PipeAction.__init__(self, input)
		self.key = key
		self.buildno = None

	def getkey(self):
		return self.key

	def write(self, project, data):
		"""
		Write <arg>data</arg> to the file and return it.
		"""
		project.writestep(self, "Writing data to ", project.strkey(self.key))
		file = self.key.open("wb")
		try:
			file.write(data)
			self.changed = datetime.datetime.utcnow() # This isn't 100% correct, but that's unproblematic, because nothing relevant happened between the real timestamp and now
			project.fileswritten += 1
		finally:
			file.close()

	def read(self, project):
		"""
		Read the content from the file and return it.
		"""
		args = ["Reading data from ", project.strkey(self.key)]
		if project.showtimestamps:
			args.append(" (changed ")
			args.append(project.strdatetime(self.changed))
			args.append(")")
		project.writestep(self, *args)
		file = self.key.open("rb")
		try:
			return file.read()
		finally:
			file.close()

	@report
	def get(self, project, since, infoonly):
		"""
		<par>If a <class>FileAction</class> object doesn't have an input action it reads the input file
		and returns the content if the file has changed since <arg>since</arg> (otherwise <lit>nodata</lit> is returned).

		<par>If a <class>FileAction</class> object does have an input action and the output data from
		this input action is newer than the file <lit><self/>.key</lit> the data will be written
		to the file. Otherwise (i.e. the file is up to date) the data will be read from the file.</par>
		"""
		if self.buildno != project.buildno: # a new build round
			# Get timestamp of the file (or bigbang if it doesn't exist)
			self.changed = filechanged(self.key)
			self.buildno = project.buildno

		if self.input is not None:
			data = self.input.get(project, self.changed, False)
			if data is not nodata: # We've got new data from our input =>
				self.write(project, data) # write new data to disk
				if infoonly: # no need for the real data
					data = newdata
				return data
		else: # We have no inputs (i.e. this is a "source" file)
			if self.changed is bigbang:
				raise ValueError("source file %r doesn't exist" % self.key)
		if self.changed > since: # We are up to date now and newer than the output action
			if infoonly:
				if project.showinfoonly:
					args = ["Have new data for ", project.strkey(self.key)]
					if project.showtimestamps:
						args.append(" (changed ")
						args.append(project.strdatetime(self.changed))
						args.append(")")
					project.writestep(self, *args)
				return newdata
			return self.read(project) # return file data (to output action or client)
		# else fail through and return nodata
		return nodata

	def __repr__(self):
		return "<%s.%s object with key=%r at 0x%x>" % (self.__class__.__module__, self.__class__.__name__, self.key, id(self))


class UnpickleAction(PipeAction):
	"""
	This action unpickles a string.
	"""
	def execute(self, project, data):
		project.writestep(self, "Unpickling")
		return cPickle.loads(data)

	def __repr__(self):
		return "<%s.%s object at 0x%x>" % (self.__class__.__module__, self.__class__.__name__, id(self))


class PickleAction(PipeAction):
	"""
	This action pickles the input data into a string.
	"""
	def __init__(self, protocol=0, input=None):
		"""
		Create a new <class>PickleAction</class> instance. <arg>protocol</arg>
		is used as the pickle protocol.
		"""
		PipeAction.__init__(self, input)
		self.protocol = protocol

	def execute(self, project, data):
		project.writestep(self, "Unpickling")
		return cPickle.dumps(data, self.protocol)

	def __repr__(self):
		return "<%s.%s object with protocol=%r at 0x%x>" % (self.__class__.__module__, self.__class__.__name__, self.protocol, id(self))


class JoinAction(Action):
	"""
	This action joins the input of all its input actions.
	"""
	def __init__(self):
		Action.__init__(self)
		self.inputs = []

	def addinputs(self, *inputs):
		"""
		Register all actions in <arg>inputs</arg> as input actions, whose data
		gets joined (in the order in which they have been passed to <method>addinputs</method>).
		"""
		self.inputs.extend(inputs)
		return self

	def __iter__(self):
		for input in self.inputs:
			yield input

	@report
	def get(self, project, since, infoonly):
		alldata = []
		changed = False
		for input in self.inputs:
			data = input.get(project, since, infoonly)
			if data is not nodata:
				changed = True
			alldata.append(data)

		data = nodata
		if changed:
			if infoonly:
				project.writestep(self, "Have new data for join")
				data = newdata
			else:
				for (i, input) in enumerate(self.inputs):
					if alldata[i] is nodata: # we didn't get data before, but we need it now
						alldata[i] = input.get(project, bigbang, False)
				project.writestep(self, "Joining data")
				data = "".join(alldata)
		return data


class ExternalAction(PipeAction):
	"""
	<class>ExternalAction</class> is like its baseclass <class>PipeAction</class>
	except that <method>execute</method> will be called even if <arg>infoonly</arg>
	is true.
	"""
	@misc.notimplemented
	def execute(self, project):
		"""
		Will be called to execute the action (even if <arg>infoonly</arg> is true).
		<method>execute</method> doesn't get passed the data object.
		"""

	@report
	def get(self, project, since, infoonly):
		data = self.input.get(project, since, infoonly)
		if data is not nodata:
			self.execute(project)
		return data


class MkDirAction(ExternalAction):
	"""
	This action creates the a directory (passing through its input data).
	"""

	def __init__(self, key, mode=0777, input=None):
		"""
		Create a <class>MkDirAction</class> instance. <arg>mode</arg> (which defaults
		to <lit>0777</lit>) will be used as the permission bit pattern for the new directory.
		"""
		PipeAction.__init__(self, input)
		self.key = key
		self.mode = mode

	def execute(self, project):
		"""
		<par>Create the directory with the permission bits specified in the constructor.</par>
		"""
		project.writestep(self, "Making directory ", project.strkey(self.key), " with mode ", oct(self.mode))
		self.key.makedirs(self.mode)

	def __repr__(self):
		return "<%s.%s object with mode=0%03o at 0x%x>" % (self.__class__.__module__, self.__class__.__name__, self.mode, id(self))


class CacheAction(PipeAction):
	"""
	A <class>CacheAction</class> is a <class>PipeAction</class> that passes
	through its input data, but caches it, so that it can
	be reused during the same build round.
	"""
	def __init__(self, input=None):
		PipeAction.__init__(self, input)
		self.since = bigcrunch
		self.data = nodata
		self.buildno = None

	@report
	def get(self, project, since, infoonly):
		if self.buildno != project.buildno or (since < self.since and self.data is nodata): # If this is a new build round or we're asked about an earlier date and didn't return data last time
			self.data = self.input.get(project, since, False)
			self.since = since
			self.buildno = project.buildno
			if infoonly:
				return newdata
		elif self.data is not nodata:
			if infoonly:
				if project.showinfoonly:
					project.writestep(self, "New data is cached")
				return newdata
			project.writestep(self, "Reusing cached data")
		return self.data


class PrefixNS(object):
	"""
	A <class>PrefixNS</class> object stores an &xist; namespace and a prefix
	for this namespace used for parsing.
	"""
	__slots__ = ("prefix", "ns")

	def __init__(self, prefix, ns):
		self.prefix = prefix
		self.ns = ns


class XISTNSPrefixAction(PipeAction):
	def __init__(self, prefix=None, input=None):
		PipeAction.__init__(self, input)
		self.prefix = prefix

	def execute(self, project, data):
		project.writestep(self, "Adding prefix ", self.prefix)
		return PrefixNS(self.prefix, data)

	def __repr__(self):
		return "<%s.%s object with prefix=%r at 0x%x>" % (self.__class__.__module__, self.__class__.__name__, self.prefix, id(self))


class GetAttrAction(PipeAction):
	"""
	This action gets an attribute from its input object.
	"""

	def __init__(self, attrname, input=None):
		PipeAction.__init__(self, input)
		self.attrname = attrname

	def execute(self, project, data):
		project.writestep(self, "Getting attribute ", self.attrname)
		return getattr(data, self.attrname)

	def __repr__(self):
		return "<%s.%s object with attrname=%r at 0x%x>" % (self.__class__.__module__, self.__class__.__name__, self.attrname, id(self))


class XISTParseAction(PipeAction):
	"""
	This action parses the input data (a string) into an
	<pyref module="ll.xist"><app>&xist;</app></pyref> node.
	"""

	def __init__(self, parser=None, base=None, input=None):
		"""
		Create an <class>XISTParseAction</class> object. <arg>parser</arg> must
		be an instance of <pyref class="ll.xist.parsers.Parser"><class>ll.xist.parsers.Parser</class></pyref>.
		If <arg>parser</arg> is <lit>None</lit> a parser will be created for you.
		<arg>base</arg> will be the base &url; used for parsing.
		"""
		PipeAction.__init__(self, input)
		if parser is None:
			from ll.xist import parsers
			parser = parsers.Parser()
		self.parser = parser
		self.base = base
		self.inputs = []

	def addinputs(self, *inputs):
		"""
		Register all actions in <arg>inputs</arg> (which must be
		<pyref class="XISTNSPrefixAction"><class>XISTNSPrefixAction</class></pyref>
		or <pyref class="ModuleAction"><class>ModuleAction</class></pyref> objects)
		as namespaces to use for parsing the input data.
		"""
		self.inputs.extend(inputs)
		return self

	def __iter__(self):
		if self.input is not None:
			yield self.input
		for input in self.inputs:
			yield input

	@report
	def get(self, project, since, infoonly):
		if infoonly:
			data = nodata
			if self.input.get(project, since, infoonly) is not nodata:
				data = newdata
			for input in self.inputs:
				if input.get(project, since, infoonly) is not nodata:
					data = newdata
			return data

		# We really have to do some work
		from ll.xist import xsc

		prefixes = xsc.Prefixes()

		def addns(input, since):
			output = input.get(project, since, False)
			if output is not nodata:
				if isinstance(output, PrefixNS):
					prefixes[output.prefix].insert(0, output.ns)
					output = output.ns
				elif isinstance(output, type) and issubclass(output, xsc.Namespace):
					prefixes[None].insert(0, output)
				else:
					raise TypeError("need a PrefixNS or namespace; got %r from %r" % (type(output), input))
			return output

		data = self.input.get(project, since, False)
		haschanged = False
		if data is not nodata:
			haschanged = True
			for input in self.inputs:
				addns(input, bigbang)
		else:
			alldata = []
			inputsince = since
			for input in self.inputs:
				output = addns(input, inputsince)
				alldata.append(output)
				if output is not nodata:
					haschanged = True
					inputsince = bigbang # force module to be loaded for the rest
			if haschanged:
				data = self.input.get(project, bigbang, False)
				# Fill in the rest of the modules
				for (i, input) in enumerate(self.inputs):
					output = alldata[i]
					if output is nodata:
						addns(input, bigbang)

		if haschanged:
			oldprefixes = self.parser.prefixes
			try:
				if prefixes:
					for (prefix, nss) in oldprefixes.iteritems():
						prefixes[prefix] = nss + prefixes[prefix]
					self.parser.prefixes = prefixes

				project.writestep(self, "Parsing XIST input with base ", self.base)
				data = self.parser.parseString(data, self.base)
			finally:
				self.parser.prefixes = oldprefixes # Restore old prefixes
		return data

	def __repr__(self):
		return "<%s.%s object with base=%r at 0x%x>" % (self.__class__.__module__, self.__class__.__name__, self.base, id(self))


class XISTConvertAction(PipeAction):
	"""
	This action transform an <pyref module="ll.xist"><app>&xist;</app></pyref> node.
	"""

	def __init__(self, mode=None, target=None, stage=None, lang=None, targetroot=None, input=None):
		"""
		<par>Create a new <class>XISTConvertAction</class> object. The arguments will be
		used to create a <pyref module="ll.xist.converters" class="Converter"><class>Converter</class></pyref>
		for each call to <method>execute</method>.</par>
		"""
		PipeAction.__init__(self, input)
		self.mode = mode
		self.target = target
		self.stage = stage
		self.lang = lang
		self.targetroot = targetroot

	def converter(self, project):
		"""
		<par>Create a new <pyref module="ll.xist.converters" class="Converter"><class>Converter</class></pyref>
		object to be used by this action. The attributes of this new converter (<lit>mode</lit>, <lit>target</lit>,
		<lit>stage</lit>, etc.) will correspond to those specified in the constructor.</par>
		<par>The <lit>makeaction</lit> attribute of the converter will be set to <self/> and
		the <lit>makeproject</lit> attribute will be set to <arg>project</arg>.</par>
		"""
		from ll.xist import converters
		return converters.Converter(root=self.targetroot, mode=self.mode, stage=self.stage, target=self.target, lang=self.lang, makeaction=self, makeproject=project)

	def execute(self, project, data):
		"""
		<par>Convert the &xist; node <arg>data</arg> using a converter provided
		by <pyref method="converter"><method>converter</method></pyref> and
		return the converted node.</par>
		"""
		args = []
		for argname in ("mode", "target", "stage", "lang", "targetroot"):
			arg = getattr(self, argname, None)
			if arg is not None:
				args.append("%s=%r" % (argname, arg))
		if args:
			args = " with %s" % ", ".join(args)
		else:
			args = ""
		project.writestep(self, "Converting XIST node", args)
		return data.convert(self.converter(project))

	def __repr__(self):
		args = []
		for argname in ("mode", "target", "stage", "lang", "targetroot"):
			arg = getattr(self, argname, None)
			if arg is not None:
				args.append("%s=%r" % (argname, arg))
		if args:
			args = " with %s" % ", ".join(args)
		else:
			args = ""
		return "<%s.%s object%s at 0x%x>" % (self.__class__.__module__, self.__class__.__name__, "".join(args), id(self))


class XISTPublishAction(PipeAction):
	"""
	This action publishes an <pyref module="ll.xist"><app>&xist;</app></pyref> node as a string.
	"""

	def __init__(self, publisher=None, base=None, input=None):
		"""
		Create an <class>XISTPublishAction</class> object. <arg>publisher</arg> must
		be an instance of <pyref class="ll.xist.publishers.Publisher"><class>ll.xist.publishers.Publisher</class></pyref>.
		If <arg>publisher</arg> is <lit>None</lit> a publisher will be created for you.
		<arg>base</arg> will be the base &url; used for publishing.
		"""
		PipeAction.__init__(self, input)
		if publisher is None:
			from ll.xist import publishers
			publisher = publishers.Publisher()
		self.publisher = publisher
		self.base = base

	def execute(self, project, data):
		"""
		Use the publisher specified in the constructor to publish the input &xist;
		node <arg>data</arg>. The output data is the generated &xml; string.
		"""
		project.writestep(self, "Publishing XIST node with base ", self.base)
		return "".join(self.publisher.publish(data, self.base))

	def __repr__(self):
		return "<%s.%s object with base=%r at 0x%x>" % (self.__class__.__module__, self.__class__.__name__, self.base, id(self))


class XISTTextAction(PipeAction):
	"""
	<par>This action creates a plain text version of an &html;
	<pyref module="ll.xist"><app>&xist;</app></pyref> node.</par>
	"""
	def __init__(self, encoding="iso-8859-1", width=72):
		self.encoding = encoding
		self.width = width

	def execute(self, project, data):
		project.writestep(self, "Converting XIST node to text with encoding=%r, width=%r" % (self.encoding, self.width))
		from ll.xist.ns import html
		return html.astext(data, encoding=self.encoding, width=self.width)


class FOPAction(PipeAction):
	"""
	This action transforms an &xml; string (containing XSL-FO) into &pdf;.
	For it to work Apache FOP is required. The command line is hardcoded but
	it's simple to overwrite the class attribute <lit>command</lit> in a subclass.
	"""
	command = "/usr/local/src/fop-0.20.5/fop.sh -q -c /usr/local/src/fop-0.20.5/conf/userconfig.xml -fo %s -pdf %s"

	def execute(self, project, data):
		project.writestep(self, "FOPping input")
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


class DecodeAction(PipeAction):
	"""
	This action decodes an input <class>str</class> object into an output <class>unicode</class> object.
	"""

	def __init__(self, encoding=None, input=None):
		"""
		Create a <class>DecodeAction</class> object with <arg>encoding</arg> as the name of the encoding.
		If <arg>encoding</arg> is <lit>None</lit> the system default encoding will be used.
		"""
		PipeAction.__init__(self, input)
		if encoding is None:
			encoding = sys.getdefaultencoding()
		self.encoding = encoding

	def execute(self, project, data):
		project.writestep(self, "Decoding input with encoding ", self.encoding)
		return data.decode(self.encoding)

	def __repr__(self):
		return "<%s.%s object with encoding=%r at 0x%x>" % (self.__class__.__module__, self.__class__.__name__, self.encoding, id(self))


class EncodeAction(PipeAction):
	"""
	This action encodes an input <class>unicode</class> object into an output <class>str</class> object.
	"""

	def __init__(self, encoding=None, input=None):
		"""
		Create an <class>EncodeAction</class> object with <arg>encoding</arg> as the name of the encoding.
		If <arg>encoding</arg> is <lit>None</lit> the system default encoding will be used.
		"""
		PipeAction.__init__(self, input)
		if encoding is None:
			encoding = sys.getdefaultencoding()
		self.encoding = encoding

	def execute(self, project, data):
		project.writestep(self, "Encoding input with encoding ", self.encoding)
		return data.encode(self.encoding)

	def __repr__(self):
		return "<%s.%s object with encoding=%r at 0x%x>" % (self.__class__.__module__, self.__class__.__name__, self.encoding, id(self))


class TOXICAction(PipeAction):
	"""
	This action transforms an &xml; string into an Oracle procedure body via
	<pyref module="ll.toxic"><module>ll.toxic</module></pyref>.
	"""

	def execute(self, project, data):
		project.writestep(self, "Toxifying input")
		from ll import toxic
		return toxic.xml2ora(data)


class TOXICPrettifyAction(PipeAction):
	"""
	This action tries to fix the indentation of a PL/SQL snippet via
	<pyref module="ll.toxic" function="prettify"><function>ll.toxic.prettify</function></pyref>.
	"""

	def execute(self, project, data):
		project.writestep(self, "Prettifying input")
		from ll import toxic
		return toxic.prettify(data)


class SplatAction(PipeAction):
	"""
	This action transforms an input string by replacing regular expressions.
	"""

	def __init__(self, patterns, input=None):
		"""
		<par>Create a new <class>SplatAction</class> object. <arg>patterns</arg>
		are pattern pairs. Each first entry will be replaced by the corresponding
		second entry.</par>
		"""
		PipeAction.__init__(self, input)
		self.patterns = patterns

	def execute(self, project, data):
		for (search, replace) in self.patterns:
			project.writestep(self, "Replacing ", search, " with ", replace)
			data = re.sub(search, replace, data)
		return data


class XPITAction(PipeAction):
	"""
	This action transform an input string via <pyref module="ll.xpit"><app>xpit</app></pyref>.
	"""

	def __init__(self, nsinput=None, input=None):
		PipeAction.__init__(self, input)
		self.nsinput = nsinput

	def addnsinput(self, input):
		"""
		Register <arg>input</arg> as the namespace action. This action must return
		a namespace to be used in evaluating the input string from the normal
		input action.
		"""
		self.nsinput = input
		return self

	def __iter__(self):
		if self.input is not None:
			yield self.input
		if self.nsinput is not None:
			yield self.nsinput

	def execute(self, project, data, ns):
		from ll import xpit
		globals = dict(makeaction=self, makeproject=project)
		project.writestep(self, "Converting XPIT input")
		return xpit.convert(data, globals, ns)

	@report
	def get(self, project, since, infoonly):
		data = self.input.get(project, since, infoonly)
		if data is not nodata:
			ns = self.nsinput
			if ns is not None:
				ns = self.nsinput.get(project, bigbang, infoonly)
			if infoonly:
				data = newdata
			else:
				data = self.execute(project, data, ns)
		else:
			ns = self.nsinput
			if ns is not None:
				ns = self.nsinput.get(project, since, infoonly)
			if ns is not nodata:
				if infoonly:
					data = newdata
				else:
					data = self.input.get(project, bigbang, False) # Refetch input data
					data = self.execute(project, data, ns)
		return data


class CommandAction(ExternalAction):
	"""
	This action executes a system command (via <function>os.system</function>)
	and passes through the input data.
	"""

	def __init__(self, command, input=None):
		"""
		<par>Create a new <class>CommandAction</class> object. <arg>command</arg> is the command
		that will executed when <pyref method="execute"><method>execute</method></pyref> is called.</par>
		"""
		PipeAction.__init__(self, input)
		self.command = command

	def execute(self, project):
		project.writestep(self, "Executing command ", self.command)
		os.system(self.command)

	def __repr__(self):
		return "<%s.%s object with command=%r at 0x%x>" % (self.__class__.__module__, self.__class__.__name__, self.command, id(self))


class ModeAction(ExternalAction):
	"""
	<class>ModeAction</class> changes file permissions and passes through the input data.
	"""

	def __init__(self, mode=0644, input=None):
		"""
		Create an <class>ModeAction</class> object. <arg>mode</arg>
		(which defaults to <lit>0644</lit>) will be use as the permission bit pattern.
		"""
		PipeAction.__init__(self, input)
		self.mode = mode

	def execute(self, project):
		"""
		Change the permission bits of the file <lit><self/>.getkey()</lit>.
		"""
		key = self.getkey()
		project.writestep(self, "Changing mode of ", project.strkey(key), " to 0%03o" % self.mode)
		key.chmod(self.mode)


class OwnerAction(ExternalAction):
	"""
	<class>OwnerAction</class> changes the user and/or group ownership of a file and passes through the input data.
	"""

	def __init__(self, user=None, group=None, input=None):
		"""
		Create a new <class>OwnerAction</class> object. <arg>user</arg> can either be a numerical
		user id or a user name or <lit>None</lit>. If it is <lit>None</lit> no user ownership will
		be changed. The same applies to <arg>group</arg>.
		"""
		PipeAction.__init__(self, input)
		self.id = id
		self.user = user
		self.group = group
		self.mode = mode

	def execute(self, project):
		"""
		Change the ownership of the file <lit><self/>.getkey()</lit>.
		"""
		key = self.getkey()
		project.writestep(self, "Changing owner of ", project.strkey(key), " to ", self.user, " and group to ", self.user)
		key.chown(self.user, self.group)


class ModuleAction(PipeAction):
	"""
	This action will turn the input string into a Python module.
	"""
	def __init__(self, input=None):
		"""
		<par>Create an <class>ModuleAction</class>.</par>

		<par>This object must have an input action (which might be a <class>FileAction</class>
		that creates the source file).</par>
		"""
		PipeAction.__init__(self, input)
		self.inputs = []
		self.changed = bigbang
		self.data = nodata
		self.buildno = None

	def addinputs(self, *inputs):
		"""
		<par>Register all actions in <arg>inputs</arg> as modules used by this
		module. These actions must be <class>ModuleAction</class>s too.</par>

		<par>Normally it isn't neccessary to call the method explicitely. Instead
		fetch the required module inside your module like this:</par>

		<prog>
		from ll import make

		mymodule = make.currentproject.get("mymodule.py")
		</prog>

		<par>This will record your module as depending on <module>mymodule</module>,
		so if <module>mymodule</module> changes your module will be reloaded too.
		For this to work you need to have an <class>ModuleAction</class>
		added to the project with the key <lit>"mymodule.py"</lit>.</par>
		"""
		self.inputs.extend(inputs)
		return self

	def __iter__(self):
		if self.input is not None:
			yield self.input
		for input in self.inputs:
			yield input

	def execute(self, project, data):
		key = self.getkey()
		project.writestep(self, "Importing module as ", project.strkey(key))

		if key is None:
			filename = name = "<string>"
		elif isinstance(key, url.URL):
			try:
				filename = key.local()
			except ValueError: # is not local
				filename = str(key)
			name = key.withoutext().file.encode("ascii", "ignore")
		else:
			filename = name = str(key)

		del self.inputs[:] # The module will be reloaded => drop all dependencies (they will be rebuilt during import)

		# Normalized line feeds, so that compile() works (normally done by import)
		data = "\n".join(data.splitlines())

		oldmod = sys.modules.get(name, None) # get any existing module out of the way

		mod = new.module(name)
		mod.__file__ = filename

		try:
			project.importstack.append(self)
			sys.modules[name] = mod # create module and make sure it can find itself in sys.module

			code = compile(data, filename, "exec")

			exec code in mod.__dict__
	
			mod = sys.modules.pop(name) # refetch the module if it has replaced itself with a custom object
		finally:
			if oldmod is not None: # put old module back
				sys.modules[name] = oldmod
			project.importstack.pop(-1)
		return mod

	@report
	def get(self, project, since, infoonly):
		# Is this module required by another?
		if project.importstack:
			if self not in project.importstack[-1].inputs:
				project.importstack[-1].addinputs(self) # Append to inputs of other module

		# Is this a new build round?
		if self.buildno != project.buildno:
			data = self.input.get(project, self.changed, False) # Get the source code
			if data is not nodata or self.data is nodata: # The file itself has changed or this is the first call
				needimport = True
			else:
				needimport = False
				for input in self.inputs:
					if input.get(project, self.changed, False) is not nodata:
						needimport = True

			if needimport:
				if data is nodata:
					data = self.input.get(project, bigbang, infoonly) # We *really* need the source
				self.data = self.execute(project, data) # This will (re)create dependencies
				# Timestamp of import is the timestamp of the newest module file
				self.changed = filechanged(self.getkey())
				if self.inputs:
					self.changed = max(self.changed, max(input.changed for input in self.inputs))
			self.buildno = project.buildno
			if self.changed > since:
				if infoonly:
					return newdata
				return self.data
		# Are we newer then the specified date?
		elif self.changed > since:
			if not infoonly or project.showinfoonly:
				key = self.getkey()
				project.writestep(self, "Reusing cached module ", project.strkey(key))
			if infoonly:
				return newdata
			return self.data
		return nodata

	def __repr__(self):
		return "<%s.%s object with 0x%x>" % (self.__class__.__module__, self.__class__.__name__, id(self))


class AlwaysAction(Action):
	"""
	This action always returns <lit>None</lit> as new data.
	"""
	def __iter__(self):
		if False:
			yield None

	@report
	def get(self, project, since, infoonly):
		if infoonly:
			return newdata
		project.writestep(self, "Returning None")
		return None
alwaysaction = AlwaysAction() # this action can be reused as it has no inputs


class NeverAction(Action):
	"""
	This action never returns new data.
	"""
	def __iter__(self):
		if False:
			yield None

	@report
	def get(self, project, since, infoonly):
		return nodata
neveraction = NeverAction() # this action can be reused as it has no inputs


###
### Classes for target keys (apart from strings for PhonyActions and URLs for FileActions)
###

class DBKey(object):
	"""
	<par>This class provides a unique identifier for database content. This
	can be used as an key for <pyref class="Action"><class>Action</class></pyref>
	objects that are not files, but database records, function, procedures etc.</par>
	"""
	name = None

	def __init__(self, connection, type, name, key=None):
		"""
		<par>Create a new <class>DBKey</class> instance. Arguments are:</par>
		<dlist>
		<term><arg>connection</arg></term>
		<item>A string that specifies the connection to the database.
		E.g. <lit>"user/pwd@db.example.com"</lit> for Oracle.</item>
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
		self.type = type.lower()
		self.name = name.lower()
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


class OracleConnection(url.Connection):
	def __init__(self, context, connection):
		self.context = context
		import cx_Oracle
		self.cursor = cx_Oracle.connect(connection).cursor()

	def open(self, url, mode="rb"):
		return OracleResource(self, url, mode)

	def mimetype(self, url):
		return "text/x-oracle-%s" % url.type

	def cdate(self, url):
		# FIXME: This isn't the correct time zone, but Oracle doesn't provide anything else
		self.cursor.execute("select created, to_number(to_char(systimestamp, 'TZH')), to_number(to_char(systimestamp, 'TZM')) from user_objects where lower(object_type)=:type and lower(object_name)=:name", type=url.type, name=url.name)
		row = self.cursor.fetchone()
		if row is None:
			raise IOError(errno.ENOENT, "no such %s: %s" % (url.type, url.name))
		return row[0]-datetime.timedelta(seconds=60*(row[1]*60+row[2]))

	def mdate(self, url):
		# FIXME: This isn't the correct time zone, but Oracle doesn't provide anything else
		self.cursor.execute("select last_ddl_time, to_number(to_char(systimestamp, 'TZH')), to_number(to_char(systimestamp, 'TZM')) from user_objects where lower(object_type)=:type and lower(object_name)=:name", type=url.type, name=url.name)
		row = self.cursor.fetchone()
		if row is None:
			raise IOError(errno.ENOENT, "no such %s: %s" % (url.type, url.name))
		return row[0]-datetime.timedelta(seconds=60*(row[1]*60+row[2]))

	def __repr__(self):
		return "<%s.%s to %r at 0x%x>" % (self.__class__.__module__, self.__class__.__name__, self.cursor.connection.connectstring(), id(self))


class OracleKey(DBKey):
	name = "oracle"

	def connect(self, context=None):
		context = url.getcontext(context)
		if context is url.defaultcontext:
			raise ValueError("oracle URLs need a custom context")

		# Use one OracleConnection for each connectstring
		try:
			connections = context.schemes["oracle"]
		except KeyError:
			connections = context.schemes["oracle"] = {}
		try:
			connection = connections[self.connection]
		except KeyError:
			connection = connections[self.connection] = OracleConnection(context, self.connection)
		return connection

	def __getattr__(self, name):
		def realattr(*args, **kwargs):
			try:
				context = kwargs["context"]
			except KeyError:
				context = None
			else:
				kwargs = kwargs.copy()
				del kwargs["context"]
			connection = self.connect(context=context)
			return getattr(connection, name)(self, *args, **kwargs)
		return realattr

	def mimetype(self):
		return "text/x-oracle-%s" % self.type

	def open(self, mode="rb", context=None, *args, **kwargs):
		connection = self.connect(context=context)
		return connection.open(self, mode, *args, **kwargs)


class OracleResource(url.Resource):
	"""
	An <class>OracleResource</class> wraps a function or procedure in an Oracle
	database in a file-like API.
	"""
	def __init__(self, connection, url, mode="rb"):
		self.connection = connection
		self.url = url
		self.mode = mode
		self.closed = False
		self.name = str(self.url)

		if self.url.type not in ("function", "procedure"):
			raise ValueError("don't know how to handle %r" % self.url)
		if "w" in self.mode:
			self.stream = cStringIO.StringIO()
			self.stream.write("create or replace %s %s\n" % (self.url.type, self.url.name))
		else:
			cursor = self.connection.cursor
			cursor.execute("select text from user_source where lower(name)=lower(:name) and type='%s' order by line" % self.url.type.upper(), name=self.url.name)
			code = "\n".join((row[0] or "").rstrip() for row in cursor)
			if not code:
				raise IOError(errno.ENOENT, "no such %s: %s" % (self.url.type, self.url.name))
			# drop type
			code = code.split(None, 1)[1]
			# skip name
			for (i, c) in enumerate(code):
				if not c.isalpha() and c != "_":
					break
			code = code[i:]
			self.stream = cStringIO.StringIO(code)

	def __getattr__(self, name):
		if self.closed:
			raise ValueError("I/O operation on closed file")
		return getattr(self.stream, name)

	def mimetype(self):
		return "text/x-oracle-%s" % self.url.type

	def cdate(self):
		return self.connection.cdate(self.url)

	def mdate(self):
		return self.connection.mdate(self.url)

	def close(self):
		if not self.closed:
			if "w" in self.mode:
				c = self._cursor()
				c.execute(self.stream.getvalue())
			self.stream = None
			self.closed = True


###
### Colors for output
###

s4indent = astyle.Style.fromenv("LL_MAKE_REPRANSI_INDENT", "black:black:bold")
s4key = astyle.Style.fromenv("LL_MAKE_REPRANSI_KEY", "green:black")
s4action = astyle.Style.fromenv("LL_MAKE_REPRANSI_ACTION", "yellow:black")
s4time = astyle.Style.fromenv("LL_MAKE_REPRANSI_TIME", "magenta:black")
s4data = astyle.Style.fromenv("LL_MAKE_REPRANSI_DATA", "cyan:black")
s4size = astyle.Style.fromenv("LL_MAKE_REPRANSI_SIZE", "magenta:black")
s4counter = astyle.Style.fromenv("LL_MAKE_REPRANSI_COUNTER", "red:black:bold")
s4error = astyle.Style.fromenv("LL_MAKE_REPRANSI_ERROR", "red:black:bold")


###
### The project class
###

class Project(dict):
	"""
	<par>A <class>Project</class> collects all <pyref class="Actions"><class>Action</class>s</pyref>
	from a project. It is responsible for initiating the build process and for generating a report
	about the progress of the build process.</par>
	"""
	def __init__(self):
		super(Project, self).__init__()
		self.actionscalled = 0
		self.actionsfailed = 0
		self.stepsexecuted = 0
		self.fileswritten = 0
		self.starttime = None
		self.ignoreerrors = False
		self.here = None # cache the current directory during builds (used for shortening URLs)
		self.home = None # cache the home directory during builds (used for shortening URLs)
		self.stack = [] # keep track of the recursion during calls to Action.get()
		self.importstack = [] # keep track of recursive imports
		self.indent = os.environ.get("LL_MAKE_INDENT", "   ") # Indentation string to use for output of nested actions
		self.buildno = 0 # Build number; This gets incremented on each call to build(). Can be used by actions to determine the start of a new build round

		self.showsummary = self._getenvbool("LL_MAKE_SHOWSUMMARY", True)
		self.showaction = os.environ.get("LL_MAKE_SHOWACTION", "filephony")
		self.showstep = os.environ.get("LL_MAKE_SHOWSTEP", "all")
		self.showregistration = os.environ.get("LL_MAKE_SHOWREGISTRATION", "phony")
		self.showtime = self._getenvbool("LL_MAKE_SHOWTIME", True)
		self.showtimestamps = self._getenvbool("LL_MAKE_SHOWTIMESTAMPS", False)
		self.showdata = self._getenvbool("LL_MAKE_SHOWDATA", True)
		self.showidle = self._getenvbool("LL_MAKE_SHOWIDLE", False)
		self.showinfoonly = self._getenvbool("LL_MAKE_SHOWINFOONLY", False)

	def __repr__(self):
		return "<%s.%s with %d targets at 0x%x>" % (self.__module__, self.__class__.__name__, len(self), id(self))

	class showaction(misc.propclass):
		"""
		<par>This property specifies which actions should be reported during the
		build process. On setting, the value can be:</par>
		<dlist>
		<term><lit>None</lit> or <lit>"none"</lit></term><item>No actions will be reported;</item>
		<term><lit>"file"</lit></term><item>Only <pyref class="FileAction"><class>FileAction</class>s</pyref> will be reported;</item>
		<term><lit>"phony"</lit></term><item>Only <pyref class="PhonyAction"><class>PhonyAction</class>s</pyref> will be reported;</item>
		<term><lit>"filephony"</lit></term><item>Only <pyref class="FileAction"><class>FileAction</class>s</pyref>
		and <pyref class="PhonyAction"><class>PhonyAction</class>s</pyref> will be reported;</item>
		<term>a class or tuple of classes</term><item>Only actions that are instances of those classes will be reported.</item>
		</dlist>
		"""
		def __get__(self):
			return self._showaction
		def __set__(self, value):
			if value == "none":
				self._showaction = None
			elif value == "file":
				self._showaction = FileAction
			elif value == "phony":
				self._showaction = PhonyAction
			elif value == "filephony":
				self._showaction = (PhonyAction, FileAction)
			elif value == "all":
				self._showaction = Action
			else:
				self._showaction = value

	class showstep(misc.propclass):
		"""
		This property specifies which for which actions tranformation steps should be reported
		during the build process. For allowed values on setting see
		<pyref property="showaction"><property>showaction</property></pyref>.
		"""
		def __get__(self):
			return self._showstep
		def __set__(self, value):
			if value == "none":
				self._showstep = None
			elif value == "file":
				self._showstep = FileAction
			elif value == "phony":
				self._showstep = PhonyAction
			elif value == "filephony":
				self._showstep = (PhonyAction, FileAction)
			elif value == "all":
				self._showstep = Action
			else:
				self._showstep = value

	class showregistration(misc.propclass):
		"""
		This property specifies for which actions registration (i.e. call to the
		<pyref method="add"><method>add</method></pyref> should be reported.
		For allowed values on setting see
		<pyref property="showaction"><property>showaction</property></pyref>.
		"""
		def __get__(self):
			return self._showregistration
		def __set__(self, value):
			if value == "none":
				self._showregistration = None
			elif value == "file":
				self._showregistration = FileAction
			elif value == "phony":
				self._showregistration = PhonyAction
			elif value == "filephony":
				self._showregistration = (PhonyAction, FileAction)
			elif value == "all":
				self._showregistration = Action
			else:
				self._showregistration = value

	def _getenvbool(self, name, default):
		return bool(int(os.environ.get(name, default)))

	def strtimedelta(self, delta):
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
		return s4time(text)

	def strdatetime(self, dt):
		"""
		<par>return a nicely formatted and colored string for
		the <class>datetime.datetime</class> value <arg>dt</arg>.
		"""
		return s4time(dt.strftime("%Y-%m-%d %H:%M:%S"), ".%06d" % (dt.microsecond))

	def strcounter(self, counter):
		"""
		<par>return a nicely formatted and colored string for
		the counter value <arg>counter</arg>.</par>
		"""
		return s4counter("%d." % counter)

	def strerror(self, text):
		"""
		<par>return a nicely formatted and colored string for
		the error text <arg>text</arg>.</par>
		"""
		return s4error(text)

	def strkey(self, key):
		"""
		<par>return a nicely formatted and colored string for
		the action key <arg>key</arg>.</par>
		"""
		s = str(key)
		if isinstance(key, url.URL) and key.islocal():
			if self.here is None:
				self.here = url.here()
			if self.home is None:
				self.home = url.home()
			test = str(key.relative(self.here))
			if len(test) < len(s):
				s = test
			test = "~/%s" % key.relative(self.home)
			if len(test) < len(s):
				s = test
		return s4key(s)

	def straction(self, action):
		"""
		<par>return a nicely formatted and colored string for
		the action <arg>action</arg>.</par>
		"""
		name = action.__class__.__name__
		if name.endswith("Action"):
			name = name[:-6]

		if hasattr(action, "key"):
			return s4action(name, "(", self.strkey(action.key), ")")
		else:
			return s4action(name)

	def __setitem__(self, key, target):
		"""
		Add the action <arg>target</arg> to <self/> as a target and register it
		under the key <arg>key</arg>.
		"""
		if key in self:
			self.warn(RedefinedTargetWarning(key), 5)
		if isinstance(key, url.URL) and key.islocal():
			key = key.abs(scheme="file")
		target.key = key
		super(Project, self).__setitem__(key, target)

	def add(self, target, key=None):
		"""
		Add the action <arg>target</arg> as a target to <self/>. If <arg>key</arg>
		is not <lit>None</lit>, <arg>target</arg> will be registered under this key
		(and <lit><arg>target</arg>.key</lit> will be set to it), otherwise it will
		be registered under its own key (i.e. <lit><arg>target</arg>.key</lit>).
		"""
		if key is None: # Use the key from the target
			key = target.getkey()

		self[key] = target

		self.stepsexecuted += 1
		if self.showregistration is not None and isinstance(target, self.showregistration):
			self.writestacklevel(0, self.strcounter(self.stepsexecuted), " Registered ", self.strkey(target.key))

		return target

	def _candidates(self, key):
		"""
		Return candidates for alternative forms of <arg>key</arg>.
		This is a generator, so when the first suitable candidate is found,
		the rest of the candidates won't have to be created at all.
		"""
		yield key
		key2 = key
		if isinstance(key, basestring):
			key2 = url.URL(key)
			yield key2
		if isinstance(key2, url.URL):
			key2 = key2.abs(scheme="file")
			yield key2
			key2 = key2.real(scheme="file")
			yield key2
		if isinstance(key, basestring) and ":" in key:
			(prefix, rest) = key.split(":", 1)
			if prefix == "oracle":
				if "|" in rest:
					(connection, rest) = rest.split("|", 1)
					if ":" in rest:
						(type, name) = rest.split(":", 1)
						if "|" in rest:
							(name, key) = rest.split("|")
						else:
							key = None
						yield OracleKey(connection, type, name, key)

	def __getitem__(self, key):
		"""
		<par>return the target with the key <arg>key</arg>.</par>
		<par>If an key can't be found, it will be wrapped in a
		<pyref module="ll.url" class="URL"><class>URL</class></pyref> instance and retried.</par>
		<par>If <arg>key</arg> still can't be found a <class>UndefinedTargetError</class>
		will be raised.
		"""
		sup = super(Project, self)
		for key2 in self._candidates(key):
			try:
				return sup.__getitem__(key2)
			except KeyError:
				pass
		raise UndefinedTargetError(key)

	def has_key(self, key):
		"""
		Return whether the target with the key <arg>key</arg> exists in the project.
		"""
		return key in self

	def __contains__(self, key):
		"""
		Return whether the target with the key <arg>key</arg> exists in the project.
		"""
		sup = super(Project, self)
		for key2 in self._candidates(key):
			has = sup.has_key(key2)
			if has:
				return True
		return False

	def create(self):
		"""
		<par>Create all dependencies for the project. Overwrite in subclasses.</par>

		<par>This method should only be called once, otherwise you'll get lots of
		<pyref class="RedefinedTargetWarning"><class>RedefinedTargetWarning</class>s</pyref>.
		But you can call <pyref method="clear"><method>clear</method></pyref> to
		remove all targets before calling <method>create</method>. You can also
		use the method <pyref method="recreate"><method>recreate</method></pyref> for that.</par>
		"""
		self.stepsexecuted = 0
		self.starttime = datetime.datetime.utcnow()
		self.writeln("Creating targets...")

	def recreate(self):
		"""
		<par>Calls <pyref method="destroy"><method>destroy</method></pyref> and
		<pyref method="create"><method>create</method></pyref> to recreate
		all project dependencies.</par>
		"""
		self.clear()
		self.create()

	def optionparser(self):
		"""
		Return an <module>optparse</module> parser for parsing the command line options.
		This can be overwritten in subclasses to add more options.
		"""
		p = optparse.OptionParser(usage="usage: %prog [options] [targets]", version="%%prog %s" % __version__)
		p.add_option("-x", "--ignore", dest="ignoreerrors", help="Ignore errors", action="store_true", default=None)
		p.add_option("-X", "--noignore", dest="ignoreerrors", help="Don't ignore errors", action="store_false", default=None)
		p.add_option("-c", "--color", dest="color", help="Use colored output", action="store_true", default=None)
		p.add_option("-C", "--nocolor", dest="color", help="No colored output", action="store_false", default=None)
		p.add_option("-a", "--showaction", dest="showaction", help="Show actions?", choices=["all", "file", "filephony", "none"], default="filephony")
		p.add_option("-s", "--showstep", dest="showstep", help="Show steps?", choices=["all", "file", "filephony", "none"], default="all")
		p.add_option("-i", "--showidle", dest="showidle", help="Show idle actions?", action="store_true", default=False)
		p.add_option(      "--showinfoonly", dest="showinfoonly", help="Show info only actions?", action="store_true", default=False)
		return p

	def parseoptions(self, commandline=None):
		"""
		Use the parser returned by <pyref method="optionparser"><method>optionparser</method></pyref>
		to parse the option sequence <arg>commandline</arg>, modify <self/> accordingly and return
		the result of <module>optparse</module>s <method>parse_args</method> call.
		"""
		p = self.optionparser()
		(options, args) = p.parse_args(commandline)
		if options.ignoreerrors is not None:
			self.ignoreerrors = options.ignoreerrors
		if options.color is not None:
			self.color = options.color
		if options.showaction is not None:
			self.showaction = options.showaction
		if options.showstep is not None:
			self.showstep = options.showstep
		self.showidle = options.showidle
		self.showinfoonly = options.showinfoonly
		return (options, args)

	def _get(self, target, since, infoonly):
		"""
		<arg>target</arg> must be an action registered in <self/> (or the id of one).
		For this target the <pyref class="Action" method="get"><method>get</method></pyref>
		will be called with <arg>since</arg> and <arg>infoonly</arg> as the
		arguments.
		"""
		global currentproject

		if not isinstance(target, Action):
			target = self[target]

		oldproject = currentproject
		try:
			currentproject = self
			data = target.get(self, since, infoonly)
		finally:
			currentproject = oldproject
		return data

	def get(self, target):
		"""
		Get uptodate output data from the target <arg>target</arg> (which must
		be an action registered with <self/> (or the id of one). During the call
		the global variable <lit>currentproject</lit> will be set to <self/>.
		"""
		return self._get(target, bigbang, False)

	def build(self, *targets):
		"""
		Rebuild all targets in <arg>targets</arg>. Items in <arg>targets</arg> must
		be actions registered with <self/> (or their ids).
		"""
		global currentproject

		self.starttime = datetime.datetime.utcnow()

		context = url.Context()
		try:
			# Use the context manager in a Python 2.4 compatible way.
			context.__enter__()
			self.stack = []
			self.importstack = []
			self.actionscalled = 0
			self.actionsfailed = 0
			self.stepsexecuted = 0
			self.fileswritten = 0
	
			self.buildno += 1 # increment build number so that actions that stored the old one can detect a new build round
	
			for target in targets:
				data = self._get(target, bigcrunch, True)
			now = datetime.datetime.utcnow()
	
			if self.showsummary:
				args = []
				self.write(
					"built ",
					s4action(self.__class__.__module__, ".", self.__class__.__name__),
					": ",
					s4data(str(len(self))),
					" registered targets; ",
					s4data(str(self.actionscalled)),
					" actions called; ",
					s4data(str(self.stepsexecuted)),
					" steps executed; ",
					s4data(str(self.fileswritten)),
					" files written; ",
					s4data(str(self.actionsfailed)),
					" actions failed",
				)
				if self.showtime and self.starttime is not None:
					self.write(" [t+", self.strtimedelta(now-self.starttime), "]")
				self.writeln()
		finally:
			context.__exit__(None, None, None)

	def buildwithargs(self, commandline=None):
		"""
		For calling make scripts from the command line.
		<arg>commandline</arg> defaults to <lit>sys.argv[1:]</lit>. Any positional
		arguments in the command line will be treated as target ids. If there are
		no possitional arguments, a list of all registered <pyref class="PhonyAction"><class>PhonyAction</class></pyref>
		objects will be output.
		"""
		if not commandline:
			commandline = sys.argv[1:]
		(options, args) = self.parseoptions(commandline)

		if args:
			self.build(*args)
		else:
			self.writeln("Available phony targets are:")
			self.writephonytargets()

	def write(self, *texts):
		"""
		All screen output is done through this method. This makes it possible to redirect
		the output (e.g. to logfiles) in subclasses.
		"""
		astyle.stderr.write(*texts)

	def writeln(self, *texts):
		"""
		All screen output is done through this method. This makes it possible to redirect
		the output (e.g. to logfiles) in subclasses.
		"""
		astyle.stderr.writeln(*texts)
		astyle.stderr.flush()

	def writeerror(self, *texts):
		"""
		Output an error.
		"""
		self.write(*texts)

	def warn(self, warning, stacklevel):
		"""
		Issue a warning through the Python warnings framework
		"""
		warnings.warn(warning, stacklevel=stacklevel)

	def writestacklevel(self, level, *texts):
		"""
		Output <arg>texts</arg> indented <arg>level</arg> levels.
		"""
		self.write(s4indent(level*self.indent), *texts)
		if self.showtime and self.starttime is not None:
			self.write(" [t+", self.strtimedelta(datetime.datetime.utcnow() - self.starttime), "]")
		self.writeln()

	def writestack(self, *texts):
		"""
		Output <arg>texts</arg> indented properly for the current nesting of
		action execution.
		"""
		self.writestacklevel(len(self.stack), *texts)

	def _writependinglevels(self):
		for (i, level) in enumerate(self.stack):
			if not level.reported:
				args = ["Started  ", self.straction(level.action)]
				if self.showtimestamps:
					args.append(" since ")
					args.append(self.strdatetime(level.since))
					if level.infoonly:
						args.append(" (info only)")
				self.writestacklevel(i, *args)
				level.reported = True

	def writestep(self, action, *texts):
		"""
		Output <arg>texts</arg> as the description of the data transformation
		done by the action <arg>arction</arg>.
		"""
		self.stepsexecuted += 1
		if self.showstep is not None and isinstance(action, self.showstep):
			if not self.showidle:
				self._writependinglevels()
			self.writestack(self.strcounter(self.stepsexecuted), " ", *texts)

	def writecreatedone(self):
		"""
		Can be called at the end of an overwritten <method>create</method> to
		report the number of registered targets.
		"""
		self.writestacklevel(0, "done: ", s4data(str(len(self))), " registered targets")

	def writephonytargets(self):
		"""
		Show a list of all <pyref class="PhonyAction"><class>PhonyAction</class></pyref>
		objects in the project and their documentation.
		"""
		phonies = []
		maxlen = 0
		for key in self:
			if isinstance(key, basestring):
				maxlen = max(maxlen, len(key))
				phonies.append(self[key])
		phonies.sort(key=operator.attrgetter("key"))
		for phony in phonies:
			text = astyle.Text(self.straction(phony))
			if phony.doc:
				text.append(" ", s4indent("."*(maxlen+3-len(phony.key))), " ", phony.doc)
			self.writeln(text)

	def findpaths(self, target, source):
		"""
		Find dependency paths leading from <arg>target</arg> to <arg>source</arg>.
		<arg>target</arg> and <arg>source</arg> may be <pyref class="Action">actions</pyref>
		or the ids of registered actions. For more info see
		<pyref class="Action" method="findpaths"><method>Action.findpaths</method></pyref>.
		"""
		if not isinstance(target, Action):
			target = self[target]
		if not isinstance(source, Action):
			source = self[source]
		return target.findpaths(source)


# This will be set to the project in build() and get()
currentproject = None
