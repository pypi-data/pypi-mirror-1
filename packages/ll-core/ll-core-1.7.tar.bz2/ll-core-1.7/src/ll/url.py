#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

## Copyright 1999-2006 by LivingLogic AG, Bayreuth/Germany.
## Copyright 1999-2006 by Walter Dörwald
##
## All Rights Reserved
##
## See __init__.py for the license


"""
<par><module>ll.url</module> contains an <link href="http://www.ietf.org/rfc/rfc2396.txt">RFC2396</link>
compliant implementation of &url;s and classes for accessing resource metadata
as well as file like classes for reading and writing resource data.</par>

<par>These three levels of functionality are implemented in three classes:</par>

<dlist>
<term><pyref class="URL"><class>URL</class></pyref></term>
<item><class>URL</class>s are the names of resources and can be used and modified,
regardless of the fact whether these resources actually exits. <class>URL</class>s
never hits the hard drive or the net.</item>

<term><pyref class="Connection"><class>Connection</class></pyref></term>
<item>Connection objects contain functionality that accesses and changes file
metadata (like last modified date, permission bits, directory structure etc.).
A connection object can be created by calling the
<pyref class="URL" method="connect"><method>connect</method></pyref>
method on a <class>URL</class> object.</item>

<term><pyref class="Resource"><class>Resource</class></pyref></term>
<item><class>Resource</class>s are file like objects that work with the actual
bytes that make up the file data. This functionality lives in the
<class>Resource</class> class and it's subclasses. Creating a resource is done
by calling the <method>open</method> method on a
<pyref class="Connection" method="open">connection</pyref>
or a <pyref class="URL" method="open"><class>URL</class></pyref>.</item>
</dlist>
"""


__version__ = tuple(map(int, "$Revision: 1.53 $"[11:-2].split(".")))
# $Source: /data/cvsroot/LivingLogic/Python/core/src/ll/url.py,v $

import sys, os, urllib, urllib2, new, mimetypes, mimetools, cStringIO, warnings
import datetime, cgi, fnmatch, cPickle, errno, threading

try:
	from email import utils as emutils
except ImportError:
	from email import Utils as emutils

# don't fail when pwd or grp can't be imported, because if this doesn't work,
# we're probably on Windows and os.chown won't work anyway
try:
	import pwd, grp
except ImportError:
	pass

try:
	import py
except ImportError:
	py = None

try:
	import Image
except ImportError:
	pass

from ll import misc, astyle


os.stat_float_times(True)


def mime2dt(s):
	return datetime.datetime(*emutils.parsedate(s)[:7])


weekdayname = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
monthname = [None, "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def httpdate(dt):
	"""
	<par>Return a string suitable for a <z>Last-Modified</z> and <z>Expires</z> header.</par>
	
	<par><arg>dt</arg> is a <class>datetime.datetime</class> object in UTC.
	"""
	return "%s, %02d %3s %4d %02d:%02d:%02d GMT" % (weekdayname[dt.weekday()], dt.day, monthname[dt.month], dt.year, dt.hour, dt.minute, dt.second)


from _url import escape as _escape, unescape as _unescape, normalizepath as _normalizepath

alpha = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
alphanum = alpha + "0123456789"
mark = "-_.!~*'()"
additionalsafe = "[]"
safe = alphanum + mark + additionalsafe
pathsafe = safe + ":@&=+$," + "|" # add "|" for Windows paths
querysafe = alphanum
fragsafe = alphanum

schemecharfirst = alpha
schemechar = alphanum + "+-."


def _urlencode(query_parts):
	if query_parts is not None:
		res = []
		items = query_parts.items()
		# generate a canonical order for the names
		items.sort()
		for (name, values) in items:
			if not isinstance(values, (list, tuple)):
				values = (values,)
			else:
				# generate a canonical order for the values
				values.sort()
			for value in values:
				res.append("%s=%s" % (_escape(name, querysafe), _escape(value, querysafe)))
		return "&".join(res)
	else:
		return None


contextstack = threading.local()

class Context(object):
	"""
	<par>Calling <pyref class="URL" method="open"><method>URL.open</method></pyref>
	or <pyref class="URL" method="connect"><method>URL.connect</method></pyref>
	creates a <pyref class="Connection">connection object</pyref>. To avoid
	constantly creating new connections you can pass a <class>Context</class>
	object to those methods. Connections will be stored in the <class>Context</class>
	object and will be reused by those methods.</par>

	<par>A <class>Context</class> object can also be used as a context manager
	(see <link href="http://www.python.org/dev/peps/pep-0346/">PEP 346</link> for
	more info). This context object will be used for all <method>open</method>
	and <method>connect</method> calls inside the <lit>with</lit> block.</par>
	"""
	def __init__(self):
		self.schemes = {}

	def __enter__(self):
		try:
			stack  = getattr(contextstack, "ll.url.contexts")
		except AttributeError:
			stack = []
			setattr(contextstack, "ll.url.contexts", stack)
		stack.append(self)

	def __exit__(self, type, value, traceback):
		stack = getattr(contextstack, "ll.url.contexts")
		stack.pop()


defaultcontext = Context()


def getcontext(context):
	if context is None:
		try:
			stack  = getattr(contextstack, "ll.url.contexts")
		except AttributeError:
			return defaultcontext
		try:
			return stack[-1]
		except IndexError:
			return defaultcontext
	return context


class Connection(object):
	"""
	A <class>Connection</class> object is used for accessing and modifying the
	metadata associated with a file. It it created by calling the
	<pyref class="URL" method="connect"><method>connect</method></pyref>
	method on a <pyref class="URL"><class>URL</class></pyref> object.
	"""

	@misc.notimplemented
	def stat(self, url):
		"""
		Return the result of a <lit>stat()</lit> call on the file <arg>url</arg>.
		"""

	@misc.notimplemented
	def lstat(self, url):
		"""
		Return the result of a <lit>stat()</lit> call on the file
		<arg>url</arg>. Like <pyref method="stat"><method>stat</method></pyref>,
		but does not follow symbolic links.
		"""

	@misc.notimplemented
	def chmod(self, url, mode):
		"""
		Set the access mode of the file <arg>url</arg> to <arg>mode</arg>.
		"""

	@misc.notimplemented
	def chown(self, url, owner=None, group=None):
		"""
		Change the owner and/or group of the file <arg>url</arg>.
		"""

	@misc.notimplemented
	def lchown(self, url, owner=None, group=None):
		"""
		Change the owner and/or group of the file <arg>url</arg>
		(ignoring symbolic links).
		"""

	@misc.notimplemented
	def uid(self, url):
		"""
		Return the user id of the owner of the file <arg>url</arg>.
		"""

	@misc.notimplemented
	def gid(self, url):
		"""
		Return the group id the file <arg>url</arg> belongs to.
		"""

	@misc.notimplemented
	def owner(self, url):
		"""
		Return the name of the owner of the file <arg>url</arg>.
		"""

	@misc.notimplemented
	def group(self, url):
		"""
		Return the name of the group the file <arg>url</arg> belongs to.
		"""

	def mimetype(self, url):
		"""
		Return the mimetype of the file <arg>url</arg>.
		"""
		name = self._url2filename(url)
		mimetype = mimetypes.guess_type(name)[0]
		return mimetype or "application/octet-stream"

	@misc.notimplemented
	def exists(self, url):
		"""
		Test whether the file <arg>url</arg> exists.
		"""

	@misc.notimplemented
	def isfile(self, url):
		"""
		Test whether the resource <arg>url</arg> is a file.
		"""

	@misc.notimplemented
	def isdir(self, url):
		"""
		Test whether the resource <arg>url</arg> is a directory.
		"""

	@misc.notimplemented
	def islink(self, url):
		"""
		Test whether the resource <arg>url</arg> is a link.
		"""

	@misc.notimplemented
	def ismount(self, url):
		"""
		Test whether the resource <arg>url</arg> is a mount point.
		"""

	@misc.notimplemented
	def access(self, url, mode):
		"""
		Test for access to the file/resource <arg>url</arg>.
		"""

	def size(self, url):
		"""
		Return the size of the file <arg>url</arg>.
		"""
		return self.stat(url).st_size

	def imagesize(self, url):
		"""
		Return the size of the image <arg>url</arg> (if the resource is an image file)
		as a <lit>(<rep>width</rep>, <rep>height</rep>)</lit> tuple. This requires
		<app moreinfo="http://www.pythonware.com/products/pil/">PIL</app>.
		"""
		stream = self.open(url, "rb")
		img = Image.open(stream) # Requires PIL
		imagesize = img.size
		stream.close()
		return imagesize

	def cdate(self, url):
		"""
		Return the <z>metadate change</z> date of the file/resource <arg>url</arg>
		as a <class>datetime.datetime</class> object in UTC.
		"""
		return datetime.datetime.utcfromtimestamp(self.stat(url).st_ctime)

	def adate(self, url):
		"""
		Return the last access date of the file/resource <arg>url</arg> as a
		<class>datetime.datetime</class> object in UTC.
		"""
		return datetime.datetime.utcfromtimestamp(self.stat(url).st_atime)

	def mdate(self, url):
		"""
		Return the last modification date of the file/resource <arg>url</arg>
		as a <class>datetime.datetime</class> object in UTC.
		"""
		return datetime.datetime.utcfromtimestamp(self.stat(url).st_mtime)

	def resheaders(self, url):
		"""
		Return the &mime; headers for the file/resource <arg>url</arg>.
		"""
		return mimetools.Message(
			cStringIO.StringIO(
				"Content-Type: %s\nContent-Length: %d\nLast-modified: %s\n" %
				(self.mimetype(url), self.size(url), httpdate(self.mdate(url)))
			)
		)

	@misc.notimplemented
	def remove(self, url):
		"""
		Remove the file <arg>url</arg>.
		"""

	@misc.notimplemented
	def rmdir(self, url):
		"""
		Remove the directory <arg>url</arg>.
		"""

	@misc.notimplemented
	def rename(self, url, target):
		"""
		Renames <arg>url</arg> to <arg>target</arg>. This might not work if
		<arg>target</arg> has a different scheme than <arg>url</arg> (or is
		on a different server).
		"""

	@misc.notimplemented
	def link(self, url, target):
		"""
		Create a hard link from <arg>url</arg> to <arg>target</arg>. This
		will not work if <arg>target</arg> has a different scheme than <arg>url</arg>
		(or is on a different server).
		"""

	@misc.notimplemented
	def symlink(self, url, target):
		"""
		Create a symbolic link from <arg>url</arg> to <arg>target</arg>. This
		will not work if <arg>target</arg> has a different scheme than <arg>url</arg>
		(or is on a different server).
		"""

	@misc.notimplemented
	def chdir(self, url):
		"""
		Change the current directory to <arg>url</arg>.
		"""
		os.chdir(self.name)

	@misc.notimplemented
	def mkdir(self, url, mode=0777):
		"""
		Create the directory <arg>url</arg>.
		"""
		
	@misc.notimplemented
	def makedirs(self, url, mode=0777):
		"""
		Create the directory <arg>url</arg> and all intermediate ones.
		"""

	@misc.notimplemented
	def listdir(self, url, pattern=None):
		"""
		Return a list of items in the directory <arg>url</arg>. The elements of the
		list are <class>URL</class> objects relative to <arg>url</arg>. With the
		optional <arg>pattern</arg> argument, this only lists items whose names
		match the given pattern.
		"""

	@misc.notimplemented
	def files(self, url, pattern=None):
		"""
		Return a list of files in the directory <arg>url</arg>. The elements of
		the list are <class>URL</class> objects relative to <arg>url</arg>. With
		the optional <arg>pattern</arg> argument, this only lists items whose
		names match the given pattern.
		"""

	@misc.notimplemented
	def dirs(self, url, pattern=None):
		"""
		Return a list of directories in the directory <arg>url</arg>. The elements
		of the list are <class>URL</class> objects relative to <arg>url</arg>.
		With the optional <arg>pattern</arg> argument, this only lists items
		whose names match the given pattern.
		"""

	@misc.notimplemented
	def walk(self, url, pattern=None):
		"""
		Return a recursive iterator over files and subdirectories. The iterator
		yields <class>URL</class> objects naming each child &url; of the directory
		<arg>url</arg> and its descendants relative to <arg>url</arg>. This performs
		a depth-first traversal, returning each directory before all its children.
		With the optional <arg>pattern</arg> argument, only yield items whose
		names match the given pattern.
		"""

	@misc.notimplemented
	def walkfiles(self, url, pattern=None):
		"""
		Return a recursive iterator over files in the directory <arg>url</arg>.
		With the optional <arg>pattern</arg> argument, only yield files whose
		names match the given pattern.
		"""

	@misc.notimplemented
	def walkdirs(self, url, pattern=None):
		"""
		Return a recursive iterator over subdirectories in the directory <arg>url</arg>.
		With the optional <arg>pattern</arg> argument, only yield directories whose
		names match the given pattern.
		"""

	@misc.notimplemented
	def open(self, url, *args, **kwargs):
		"""
		<par>Open <arg>url</arg> for reading or writing. <method>open</method> returns
		a <pyref class="Resource"><class>Resource</class></pyref> object.</par>

		<par>Which additional parameters are supported depends on the actual
		resource created. Some common parameters are:</par>

		<dlist>
		<term><arg>mode</arg></term>
		<item>A string indicating how the file is to be opened (just like the mode
		argument for the builtin <function>open</function> (e.g. <lit>"rb"</lit>
		or <lit>"wb"</lit>).</item>

		<term><arg>headers</arg></term>
		<item>Additional headers to use for an &http; request.</item>

		<term><arg>data</arg></term>
		<item>Request body to use for an &http; POST request.</item>

		<term><arg>remotepython</arg></term>
		<item>Name of the Python interpreter to use on the remote side
		(used by <lit>ssh</lit> &url;s)</item>
		</dlist>
		"""


class LocalConnection(Connection):
	def _url2filename(self, url):
		return os.path.expanduser(url.local())

	def stat(self, url):
		return os.stat(self._url2filename(url))

	def lstat(self, url):
		return os.lstat(self._url2filename(url))

	def chmod(self, url, mode):
		name = self._url2filename(url)
		os.chmod(name, mode)

	def _chown(self, func, url, owner, group):
		name = self._url2filename(url)
		if owner is not None or group is not None:
			if owner is None or group is None:
				stat = os.stat(name)
			if owner is None:
				owner = stat.st_uid
			elif isinstance(owner, basestring):
				owner = pwd.getpwnam(owner)[2]
			if group is None:
				group = stat.st_gid
			elif isinstance(group, basestring):
				group = grp.getgrnam(group)[2]
			func(name, owner, group)

	def chown(self, url, owner=None, group=None):
		self._chown(os.chown, url, owner, group)

	def lchown(self, url, owner=None, group=None):
		self._chown(os.lchown, url, owner, group)

	def chdir(self, url):
		os.chdir(self._url2filename(url))

	def mkdir(self, url, mode=0777):
		os.mkdir(self._url2filename(url), mode)

	def makedirs(self, url, mode=0777):
		os.makedirs(self._url2filename(url), mode)

	def uid(self, url):
		return self.stat(url).st_uid

	def gid(self, url):
		return self.stat(url).st_gid

	def owner(self, url):
		return pwd.getpwuid(self.uid(url))[0]

	def group(self, url):
		return grp.getgrgid(self.gid(url))[0]

	def exists(self, url):
		return os.path.exists(self._url2filename(url))

	def isfile(self, url):
		return os.path.isfile(self._url2filename(url))

	def isdir(self, url):
		return os.path.isdir(self._url2filename(url))

	def islink(self, url):
		return os.path.islink(self._url2filename(url))

	def ismount(self, url):
		return os.path.ismount(self._url2filename(url))

	def access(self, url, mode):
		return os.access(self._url2filename(url), mode)

	def remove(self, url):
		return os.remove(self._url2filename(url))

	def rmdir(self, url):
		return os.rmdir(self._url2filename(url))

	def rename(self, url, target):
		name = self._url2filename(url)
		if not isinstance(target, URL):
			target = URL(target)
		targetname = self._url2filename(target)
		os.rename(name, target)

	def link(self, url, target):
		name = self._url2filename(url)
		if not isinstance(target, URL):
			target = URL(target)
		target = self._url2filename(target)
		os.link(name, target)

	def symlink(self, url, target):
		name = self._url2filename(url)
		if not isinstance(target, URL):
			target = URL(target)
		target = self._url2filename(target)
		os.symlink(name, target)

	def listdir(self, url, pattern=None):
		name = self._url2filename(url)
		result = []
		for childname in os.listdir(name):
			if pattern is None or fnmatch.fnmatch(childname, pattern):
				if os.path.isdir(os.path.join(name, childname)):
					result.append(Dir(childname, scheme=url.scheme))
				else:
					result.append(File(childname, scheme=url.scheme))
		return result

	def files(self, url, pattern=None):
		name = self._url2filename(url)
		result = []
		for childname in os.listdir(name):
			if pattern is None or fnmatch.fnmatch(childname, pattern):
				if os.path.isfile(os.path.join(name, childname)):
					result.append(File(childname, scheme=url.scheme))
		return result

	def dirs(self, url, pattern=None):
		name = self._url2filename(url)
		result = []
		for childname in os.listdir(name):
			if pattern is None or fnmatch.fnmatch(childname, pattern):
				if os.path.isdir(os.path.join(name, childname)):
					result.append(Dir(childname, scheme=url.scheme))
		return result

	def _walk(self, base, name, pattern, which):
		if name:
			fullname = os.path.join(base, name)
		else:
			fullname = base
		for childname in os.listdir(fullname):
			fullchildname = os.path.join(fullname, childname)
			relchildname = os.path.join(name, childname)
			isdir = os.path.isdir(fullchildname)
			if (pattern is None or fnmatch.fnmatch(childname, pattern)) and which[isdir]:
				url = urllib.pathname2url(relchildname)
				if isdir:
					url += "/"
				yield URL(url)
			if isdir:
				for subchild in self._walk(base, relchildname, pattern, which):
					yield subchild

	def walk(self, url, pattern=None):
		return self._walk(self._url2filename(url), "", pattern, (True, True))

	def walkfiles(self, url, pattern=None):
		return self._walk(self._url2filename(url), "", pattern, (True, False))

	def walkdirs(self, url, pattern=None):
		return self._walk(self._url2filename(url), "", pattern, (False, True))

	def open(self, url, mode="rb"):
		return FileResource(url, mode)


if py is not None:
	class SshConnection(Connection):
		remote_code = py.code.Source("""
			import os, urllib, cPickle, fnmatch

			os.stat_float_times(True)
			files = {}
			iterators = {}

			def ownergroup(filename, owner=None, group=None):
				if owner is not None or group is not None:
					if owner is None or group is None:
						if isinstance(filename, basestring):
							stat = os.stat(filename)
						else:
							stat = os.fstat(files[filename].fileno())
					if owner is None:
						owner = stat.st_uid
					elif isinstance(owner, basestring):
						import pwd
						owner = pwd.getpwnam(owner)[2]

					if group is None:
						group = stat.st_gid
					elif isinstance(group, basestring):
						import grp
						group = grp.getgrnam(group)[2]
				return (owner, group)

			def _walk(base, name, pattern, which):
				if name:
					fullname = os.path.join(base, name)
				else:
					fullname = base
				for childname in os.listdir(fullname):
					fullchildname = os.path.join(fullname, childname)
					relchildname = os.path.join(name, childname)
					isdir = os.path.isdir(fullchildname)
					if (pattern is None or fnmatch.fnmatch(childname, pattern)) and which[isdir]:
						url = urllib.pathname2url(relchildname)
						if isdir:
							url += "/"
						yield url
					if isdir:
						for subchild in _walk(base, relchildname, pattern, which):
							yield subchild
		
			def walk(filename, pattern=None):
				return _walk(filename, "", pattern, (True, True))

			def walkfiles(filename, pattern=None):
				return _walk(filename, "", pattern, (True, False))

			def walkdirs(filename, pattern=None):
				return _walk(filename, "", pattern, (False, True))

			while True:
				(filename, cmdname, args, kwargs) = channel.receive()
				if isinstance(filename, basestring):
					filename = os.path.expanduser(filename)
				data = None
				try:
					if cmdname == "open":
						try:
							stream = open(filename, *args, **kwargs)
						except IOError, exc:
							if "w" not in args[0] or exc[0] != 2: # didn't work for some other reason than a non existing directory
								raise
							(splitpath, splitname) = os.path.split(filename)
							if splitpath:
								os.makedirs(splitpath)
								stream = open(filename, *args, **kwargs)
							else:
								raise # we don't have a directory to make so pass the error on
						data = id(stream)
						files[data] = stream
					elif cmdname == "stat":
						if isinstance(filename, basestring):
							data = os.stat(filename)
						else:
							data = os.fstat(files[filename].fileno())
					elif cmdname == "lstat":
						data = os.lstat(filename)
					elif cmdname == "close":
						try:
							stream = files[filename]
						except KeyError:
							pass
						else:
							stream.close()
							del files[filename]
					elif cmdname == "chmod":
						data = os.chmod(filename, *args, **kwargs)
					elif cmdname == "chown":
						(owner, group) = ownergroup(filename, *args, **kwargs)
						if owner is not None:
							data = os.chown(filename, owner, group)
					elif cmdname == "lchown":
						(owner, group) = ownergroup(filename, *args, **kwargs)
						if owner is not None:
							data = os.lchown(filename, owner, group)
					elif cmdname == "uid":
						stat = os.stat(filename)
						data = stat.st_uid
					elif cmdname == "gid":
						stat = os.stat(filename)
						data = stat.st_gid
					elif cmdname == "owner":
						import pwd
						stat = os.stat(filename)
						data = pwd.getpwuid(stat.st_uid)[0]
					elif cmdname == "group":
						import grp
						stat = os.stat(filename)
						data = grp.getgrgid(stat.st_gid)[0]
					elif cmdname == "exists":
						data = os.path.exists(filename)
					elif cmdname == "isfile":
						data = os.path.isfile(filename)
					elif cmdname == "isdir":
						data = os.path.isdir(filename)
					elif cmdname == "islink":
						data = os.path.islink(filename)
					elif cmdname == "ismount":
						data = os.path.ismount(filename)
					elif cmdname == "access":
						data = os.access(filename, *args, **kwargs)
					elif cmdname == "remove":
						data = os.remove(filename)
					elif cmdname == "rmdir":
						data = os.rmdir(filename)
					elif cmdname == "rename":
						data = os.rename(filename, os.path.expanduser(args[0]))
					elif cmdname == "link":
						data = os.link(filename, os.path.expanduser(args[0]))
					elif cmdname == "symlink":
						data = os.symlink(filename, os.path.expanduser(args[0]))
					elif cmdname == "chdir":
						data = os.chdir(filename)
					elif cmdname == "mkdir":
						data = os.mkdir(filename)
					elif cmdname == "makedirs":
						data = os.makedirs(filename)
					elif cmdname == "makefifo":
						data = os.makefifo(filename)
					elif cmdname == "listdir":
						data = []
						for f in os.listdir(filename):
							if args[0] is None or fnmatch.fnmatch(f, args[0]):
								data.append((os.path.isdir(os.path.join(filename, f)), f))
					elif cmdname == "files":
						data = []
						for f in os.listdir(filename):
							if args[0] is None or fnmatch.fnmatch(f, args[0]):
								if os.path.isfile(os.path.join(filename, f)):
									data.append(f)
					elif cmdname == "dirs":
						data = []
						for f in os.listdir(filename):
							if args[0] is None or fnmatch.fnmatch(f, args[0]):
								if os.path.isdir(os.path.join(filename, f)):
									data.append(f)
					elif cmdname == "walk":
						iterator = walk(filename, *args, **kwargs)
						data = id(iterator)
						iterators[data] = iterator
					elif cmdname == "walkfiles":
						iterator = walkfiles(filename, *args, **kwargs)
						data = id(iterator)
						iterators[data] = iterator
					elif cmdname == "walkdirs":
						iterator = walkdirs(filename, *args, **kwargs)
						data = id(iterator)
						iterators[data] = iterator
					elif cmdname == "iteratornext":
						try:
							data = iterators[filename].next()
						except StopIteration:
							del iterators[filename]
							raise
					else:
						data = getattr(files[filename], cmdname)
						data = data(*args, **kwargs)
				except Exception, exc:
					if exc.__class__.__module__ != "exceptions":
						raise
					channel.send((True, cPickle.dumps(exc)))
				else:
					channel.send((False, data))
		""")
		def __init__(self, context, server, remotepython="python"):
			self.context = context
			self.server = server
			gateway = py.execnet.SshGateway(server, remotepython=remotepython)
			self._channel = gateway.remote_exec(self.remote_code)

		def _url2filename(self, url):
			if url.scheme != "ssh":
				raise ValueError("URL %r is not an ssh URL" % url)
			filename = str(url.path)
			if filename.startswith("/~"):
				filename = filename[1:]
			return filename

		def _send(self, filename, cmd, *args, **kwargs):
			self._channel.send((filename, cmd, args, kwargs))
			(isexc, data) = self._channel.receive()
			if isexc:
				raise cPickle.loads(data)
			else:
				return data

		def stat(self, url):
			filename = self._url2filename(url)
			data = self._send(filename, "stat")
			return os.stat_result(data) # channel returned a tuple => wrap it

		def lstat(self):
			filename = self._url2filename(url)
			data = self._send(filename, "lstat")
			return os.stat_result(data) # channel returned a tuple => wrap it

		def chmod(self, url, mode):
			return self._send(self._url2filename(url), "chmod", mode)

		def chown(self, url, owner=None, group=None):
			return self._send(self._url2filename(url), "chown", owner, group)

		def lchown(self, url, owner=None, group=None):
			return self._send(self._url2filename(url), "lchown", owner, group)

		def chdir(self, url):
			return self._send(self._url2filename(url), "chdir")

		def mkdir(self, url, mode=0777):
			return self._send(self._url2filename(url), "mkdir", mode)

		def makedirs(self, url, mode=0777):
			return self._send(self._url2filename(url), "makedirs", mode)

		def uid(self, url):
			return self._send(self._url2filename(url), "uid")

		def gid(self, url):
			return self._send(self._url2filename(url), "gid")

		def owner(self, url):
			return self._send(self._url2filename(url), "owner")

		def group(self, url):
			return self._send(self._url2filename(url), "group")

		def exists(self, url):
			return self._send(self._url2filename(url), "exists")

		def isfile(self, url):
			return self._send(self._url2filename(url), "isfile")

		def isdir(self, url):
			return self._send(self._url2filename(url), "isdir")

		def islink(self, url):
			return self._send(self._url2filename(url), "islink")

		def ismount(self, url):
			return self._send(self._url2filename(url), "ismount")

		def access(self, url, mode):
			return self._send(self._url2filename(url), "access", mode)

		def remove(self, url):
			return self._send(self._url2filename(url), "remove")

		def rmdir(self, url):
			return self._send(self._url2filename(url), "rmdir")

		def _cmdwithtarget(self, cmdname, url, target):
			filename = self._url2filename(url)
			if not isinstance(target, URL):
				target = URL(target)
			targetname = self._url2filename(target)
			if target.server != url.server:
				raise OSError(errno.EXDEV, os.strerror(errno.EXDEV))
			return self._send(filename, cmdname, targetname)

		def rename(self, url, target):
			return self._cmdwithtarget("rename", url, target)

		def link(self, url, target):
			return self._cmdwithtarget("link", url, target)

		def symlink(self, url, target):
			return self._cmdwithtarget("symlink", url, target)

		def listdir(self, url, pattern=None):
			filename = self._url2filename(url)
			result = []
			for (isdir, name) in self._send(filename, "listdir", pattern):
				name = urllib.pathname2url(name)
				if isdir:
					name += "/"
				result.append(URL(name))
			return result

		def files(self, url, pattern=None):
			filename = self._url2filename(url)
			return [URL(urllib.pathname2url(name)) for name in self._send(filename, "files", pattern)]

		def dirs(self, url, pattern=None):
			filename = self._url2filename(url)
			return [URL(urllib.pathname2url(name)+"/") for name in self._send(filename, "dirs", pattern)]

		def walk(self, url, pattern=None):
			filename = self._url2filename(url)
			iterator = self._send(filename, "walk", pattern)
			while True:
				yield URL(self._send(iterator, "iteratornext"))

		def walkfiles(self, url, pattern=None):
			filename = self._url2filename(url)
			iterator = self._send(filename, "walkfiles", pattern)
			while True:
				yield URL(self._send(iterator, "iteratornext"))

		def walkdirs(self, url, pattern=None):
			filename = self._url2filename(url)
			iterator = self._send(filename, "walkdirs", pattern)
			while True:
				yield URL(self._send(iterator, "iteratornext"))

		def open(self, url, mode="rb"):
			return RemoteFileResource(self, url, mode)

		def __repr__(self):
			return "<%s.%s to %r at 0x%x>" % (self.__class__.__module__, self.__class__.__name__, self.server, id(self))


class URLConnection(Connection):
	def mimetype(self, url):
		return url.open().mimetype()

	def size(self, url):
		return url.open().size()

	def imagesize(self, url):
		return url.open().imagesize()

	def mdate(self, url):
		return url.open().mdate()

	def resheaders(self, url):
		return url.open().resheaders()

	def open(self, url, mode="rb", headers=None, data=None):
		if mode != "rb":
			raise NotImplementedError("mode %r not supported" % mode)
		return URLResource(url, headers=headers, data=data)


def here(scheme="file"):
	"""
	<par>Return the current directory as an <pyref class="URL"><class>URL</class></pyref>.</par>
	"""
	return Dir(os.getcwd(), scheme)


def home(user="", scheme="file"):
	"""
	<par>Return the home directory of the current user (or the user named <arg>user</arg>,
	if <arg>user</arg> is specified) as an <pyref class="URL"><class>URL</class></pyref>.</par>
	<prog>
	<prompt>&gt;&gt;&gt;</prompt> <input>url.home()</input>
	URL('file:/home/walter/')
	<prompt>&gt;&gt;&gt;</prompt> <input>url.home("andreas")</input>
	URL('file:/home/andreas/')
	</prog>
	"""
	return Dir("~%s" % user, scheme)


def root():
	"""
	<par>Return a blank <lit>root</lit> <pyref class="URL"><class>URL</class></pyref>,
	i.e. <lit>URL("root:")</lit>.</par>
	"""
	return URL("root:")


def File(name, scheme="file"):
	"""
	<par>Turn a filename into an <pyref class="URL"><class>URL</class></pyref>:</par>
	<prog>
	<prompt>&gt;&gt;&gt;</prompt> <input>url.File("a#b")</input>
	URL('file:a%23b')
	</prog>
	"""
	name = urllib.pathname2url(os.path.expanduser(name.encode("utf-8")))
	if name.startswith("///"):
		name = name[2:]
	url = URL(name)
	url.scheme = scheme
	return url


def Dir(name, scheme="file"):
	"""
	<par>Turns a directory name into an <pyref class="URL"><class>URL</class></pyref>, just like
	<pyref function="File"><function>File</function></pyref>, but ensures that the path
	is terminated with a <lit>/</lit>:</par>
	<prog>
	<prompt>&gt;&gt;&gt;</prompt> <input>url.Dir("a#b")</input>
	URL('file:a%23b/')
	</prog>
	"""
	name = urllib.pathname2url(os.path.expanduser(name.encode("utf-8")))
	if not name.endswith("/"):
		name += "/"
	if name.startswith("///"):
		name = name[2:]
	url = URL(name)
	url.scheme = scheme
	return url


def Ssh(user, host, path="~/"):
	"""
	<par>Return a ssh <pyref class="URL"><class>URL</class></pyref> for the user
	<arg>user</arg> on the host <arg>host</arg> with the path <arg>path</arg>.
	<arg>path</arg> (defaulting to the users home directory) must be a path in
	&url; notation (i.e. use <lit>/</lit> as directory separator):</par>
	<prog>
	<prompt>&gt;&gt;&gt;</prompt> <input>url.Ssh("root", "www.example.com", "~joe/public_html/index.html")</input>
	URL('ssh://root@www.example.com/~joe/public_html/index.html')
	</prog>
	<par>If the path starts with <lit>~/</lit> it is relative to this users
	home directory, if it starts with <lit>~/<rep>user</rep></lit> it's relative
	to the home directory of the user <lit><rep>user</rep></lit>. In all other
	cases the path is considered to be absolute.</par>
	"""
	url = URL()
	url.scheme = "ssh"
	url.userinfo = user
	url.host = host
	if path.startswith("~"):
		path = "/" + path
	url.path = path
	return url


def first(urls):
	"""
	<par>Return the first &url; from <arg>urls</arg> that exists as a real file or directory.</par>
	<par><lit>None</lit> entries in <arg>urls</arg> will be skipped.</par>
	"""
	for url in urls:
		if url is not None:
			if url.exists():
				return url


def firstdir(urls):
	"""
	<par>Return the first &url; from <arg>urls</arg> that exists as a real directory.</par>
	<par><lit>None</lit> entries in <arg>urls</arg> will be skipped.</par>
	"""
	for url in urls:
		if url is not None:
			if url.isdir():
				return url


def firstfile(urls):
	"""
	<par>Return the first &url; from <arg>urls</arg> that exists as a real file.</par>
	<par><lit>None</lit> entries in <arg>urls</arg> will be skipped.</par>
	"""
	for url in urls:
		if url is not None:
			if url.isfile():
				return url


class importcache(dict):
	def remove(self, mod):
		try:
			dict.__delitem__(self, mod.__file__)
		except KeyError:
			pass

importcache = importcache()


def _import(filename):
	(path, name) = os.path.split(filename)
	(name, ext) = os.path.splitext(name)

	if ext != ".py":
		raise ImportError("Can only import .py files, not %s" % ext)

	oldmod = sys.modules.get(name, None) # get any existing module out of the way
	sys.modules[name] = mod = new.module(name) # create module and make sure it can find itself in sys.module
	mod.__file__ = filename
	execfile(filename, mod.__dict__)
	mod = sys.modules.pop(name) # refetch the module if it has replaced itself with a custom object
	if oldmod is not None: # put old module back
		sys.modules[name] = oldmod
	return mod


class Resource(object):
	"""
	<par>A <class>Resource</class> is a base class that provides a file-like interface
	to local and remote files, &url;s and other resources.</par>
	
	<section><title>Attributes</title>
	<par>Each resource object has the following attributes:</par>

	<dlist>
	<term><lit>url</lit></term>
	<item>The &url; for which this resource has been opened (i.e.
	<lit><rep>foo</rep>.open().url is <rep>foo</rep></lit> if
	<lit><rep>foo</rep></lit> is a <pyref class="URL"><class>URL</class></pyref>
	object);</item>

	<term><lit>name</lit></term>
	<item>A string version of <lit>url</lit>;</item>

	<term><lit>closed</lit></term>
	<item>A <class>bool</class> specifying whether the resource has been closed
	(i.e. whether the <method>close</method> method has been called).</item>
	</dlist>
	</section>

	<section><title>Methods</title>
	<par>In addition to file methods
	(like <method>read</method>, <method>readlines</method>, <method>write</method>
	and <method>close</method>) a resource object might provide the following
	methods:</par>

	<dlist>
	<term><method>finalurl</method></term>
	<item>Return the real &url; of the resource (this might be different from the
	<lit>url</lit> attribute in case of a redirect).</item>

	<term><method>size</method></term>
	<item>Return the size of the file/resource.</item>

	<term><method>mdate</method></term>
	<item>Return the last modification date of the file/resource as a
	<class>datetime.datetime</class> object in UTC.</item>

	<term><method>mimetype</method></term>
	<item>Return the mimetype of the file/resource.</item>

	<term><method>imagesize</method></term>
	<item>Return the size of the image (if the resource is an image file) as a
	<lit>(<rep>width</rep>, <rep>height</rep>)</lit> tuple. This requires
	<app moreinfo="http://www.pythonware.com/products/pil/">PIL</app>.</item>
	</dlist>
	</section>
	"""

	def finalurl(self):
		return self.url

	def imagesize(self):
		pos = self.tell()
		self.seek(0)
		img = Image.open(self) # Requires PIL
		imagesize = img.size
		self.seek(pos)
		return imagesize

	def __repr__(self):
		if self.closed:
			state = "closed"
		else:
			state = "open"
		return "<%s %s.%s %r, mode %r at 0x%x>" % (state, self.__class__.__module__, self.__class__.__name__, self.name, self.mode, id(self))


class FileResource(Resource, file):
	"""
	A subclass of <pyref class="Resource"><class>Resource</class></pyref> that
	handles local files.
	"""
	def __init__(self, url, mode="rb"):
		url = URL(url)
		name = os.path.expanduser(url.local())
		try:
			file.__init__(self, name, mode)
		except IOError, exc:
			if "w" not in mode or exc[0] != 2: # didn't work for some other reason than a non existing directory
				raise
			(splitpath, splitname) = os.path.split(name)
			if splitpath:
				os.makedirs(splitpath)
				file.__init__(self, name, mode)
			else:
				raise # we don't have a directory to make so pass the error on
		self.url = url

	def size(self):
		# Forward to the connection
		return LocalSchemeDefinition._connection.size(self.url)

	def mdate(self):
		# Forward to the connection
		return LocalSchemeDefinition._connection.mdate(self.url)

	def mimetype(self):
		# Forward to the connection
		return LocalSchemeDefinition._connection.mimetype(self.url)


if py is not None:
	class RemoteFileResource(Resource):
		"""
		A subclass of <pyref class="Resource"><class>Resource</class></pyref> that
		handles remote files (those with the <lit>ssh</lit> scheme).
		"""
		def __init__(self, connection, url, mode="rb"):
			self.connection = connection
			self.url = URL(url)
			self.mode = mode
			self.closed = False
			filename = self.connection._url2filename(url)
			self.name = str(self.url)
			self.remoteid = self._send(filename, "open", mode)

		def _send(self, filename, cmd, *args, **kwargs):
			if self.closed:
				raise ValueError("I/O operation on closed file")
			return self.connection._send(filename, cmd, *args, **kwargs)
	
		def close(self):
			if not self.closed:
				self._send(self.remoteid, "close")
				self.connection = None # close the channel too as there are no longer any meaningful operations
				self.closed = True

		def read(self, size=-1):
			return self._send(self.remoteid, "read", size)

		def readline(self, size=-1):
			return self._send(self.remoteid, "readline", size)

		def readlines(self, size=-1):
			return self._send(self.remoteid, "readlines", size)

		def __iter__(self):
			return self

		def next(self):
			return self._send(self.remoteid, "next")

		def seek(self, offset, whence=0):
			return self._send(self.remoteid, "seek", offset, whence)

		def tell(self):
			return self._send(self.remoteid, "tell")

		def truncate(self, size=None):
			if size is None:
				return self._send(self.remoteid, "truncate")
			else:
				return self._send(self.remoteid, "truncate", size)

		def write(self, string):
			return self._send(self.remoteid, "write", string)

		def writelines(self, strings):
			return self._send(self.remoteid, "writelines", strings)

		def flush(self):
			return self._send(self.remoteid, "flush")

		def size(self):
			# Forward to the connection
			return self.connection.size(self.url)

		def mdate(self):
			# Forward to the connection
			return self.connection.mdate(self.url)

		def mimetype(self):
			# Forward to the connection
			return self.connection.mimetype(self.url)


class URLResource(Resource):
	"""
	A subclass of <pyref class="Resource"><class>Resource</class></pyref> that
	handles &http;, &ftp; and other &url;s (i.e. those that are not handled by
	<pyref class="FileResource"><class>FileResource</class></pyref> or
	<pyref class="RemoteFileResource"><class>RemoteFileResource</class></pyref>.
	"""
	def __init__(self, url, mode="rb", headers=None, data=None):
		if "w" in mode:
			raise ValueError("writing mode %r not supported" % mode)
		self.url = URL(url)
		self.name = str(self.url)
		self.mode = mode
		self.reqheaders = headers
		self.reqdata = data
		self._finalurl = None
		self.closed = False
		self._stream = None
		if data is not None:
			data = urllib.urlencode(data)
		if headers is None:
			headers = {}
		req = urllib2.Request(url=self.name, data=data, headers=headers)
		self._stream = urllib2.urlopen(req)
		self._finalurl = URL(self._stream.url) # Remember the final URL in case of a redirect
		self._resheaders = self._stream.info()
		self._mimetype = None
		self._encoding = None
		contenttype = self._resheaders.getheader("Content-Type")
		if contenttype is not None:
			(mimetype, options) = cgi.parse_header(contenttype)
			self._mimetype = mimetype
			self._encoding = options.get("charset")

		cl = self._resheaders.get("Content-Length")
		if cl:
			cl = int(cl)
		self._size = cl
		lm = self._resheaders.get("Last-Modified")
		if lm is not None:
			lm = mime2dt(lm)
		self._mdate = lm
		self._buffer = cStringIO.StringIO()

	def __getattr__(self, name):
		function = getattr(self._stream, name)
		def call(*args, **kwargs):
			return function(*args, **kwargs)
		return call

	def close(self):
		if not self.closed:
			self._stream.close()
			self._stream = None
			self.closed = True

	def __iter__(self):
		return iter(self._stream)

	def finalurl(self):
		return self._finalurl

	def mimetype(self):
		return self._mimetype

	def resheaders(self):
		return self._resheaders

	def encoding(self):
		return self._encoding

	def mdate(self):
		return self._mdate

	def size(self):
		return self._size

	def read(self, size=-1):
		data = self._stream.read(size)
		self._buffer.write(data)
		return data

	def readline(self, size=-1):
		data = self._stream.readline(size)
		self._buffer.write(data)
		return data

	def resdata(self):
		data = self._stream.read()
		self._buffer.write(data)
		return self._buffer.getvalue()

	def imagesize(self):
		img = Image.open(cStringIO.StringIO(self.resdata())) # Requires PIL
		return img.size

	def __iter__(self):
		while True:
			data = self._stream.readline()
			if not data:
				break
			self._buffer.write(data)
			yield data


class SchemeDefinition(object):
	"""
	<par>A <class>SchemeDefinition</class> instance defines the properties
	of a particular &url; scheme.</par>
	"""
	_connection = URLConnection()

	def __init__(self, scheme, usehierarchy, useserver, usefrag, islocal=False, isremote=False, defaultport=None):
		"""
		<par>Create a new <class>SchemeDefinition</class> instance. Arguments are:</par>
		<ulist>
		<item><arg>scheme</arg>: The name of the scheme;</item>
		<item><arg>usehierarchy</arg>: Specifies whether this scheme uses hierarchical &url;s
		or opaque &url;s (i.e. whether <lit>hier_part</lit> or <lit>opaque_part</lit> from the
		&bnf; in <link href="http://www.ietf.org/rfc/rfc2396.txt">RFC2396</link> is used);</item>
		<item><arg>useserver</arg>: Specifies whether this scheme uses an Internet-based server
		<pyref property="authority"><property>authority</property></pyref> component or a registry
		of naming authorities (only for hierarchical &url;s);</item>
		<item><arg>usefrag</arg>: Specifies whether this scheme uses fragments
		(according to the &bnf; in <link href="http://www.ietf.org/rfc/rfc2396.txt">RFC2396</link>
		every scheme does, but it doesn't make sense for e.g. <lit>"javascript"</lit>,
		<lit>"mailto"</lit> or <lit>"tel"</lit>);</item>
		<item><arg>islocal</arg>: Specifies whether &url;s with this scheme refer to
		local files;</item>
		<item><arg>isremote</arg>: Specifies whether &url;s with this scheme refer to
		remote files (there may be schemes which are neither local nor remote,
		e.g. <lit>"mailto"</lit>);</item>
		<item><arg>defaultport</arg>: The default port for this scheme (only for schemes
		using server based authority).</item>
		</ulist>
		"""
		self.scheme = scheme
		self.usehierarchy = usehierarchy
		self.useserver = useserver
		self.usefrag = usefrag
		self.islocal = islocal
		self.isremote = isremote
		self.defaultport = defaultport

	def connect(self, url, context=None):
		# We can always use the same connection, because the connection for local
		# files and real URLs doesn't use any resources.
		# This will be overwritten by SshSchemeDefinition
		return self._connection

	def open(self, *args, **kwargs):
		return URLConnection(*args, **kwargs)

	def __repr__(self):
		return "<%s instance scheme=%r usehierarchy=%r useserver=%r usefrag=%r at 0x%x>" % (self.__class__.__name__, self.scheme, self.usehierarchy, self.useserver, self.usefrag, id(self))


class LocalSchemeDefinition(SchemeDefinition):
	# Use a different connection then the base class (but still one single connection for all URLs)
	_connection = LocalConnection()

	def open(self, *args, **kwargs):
		return FileResource(*args, **kwargs)


class SshSchemeDefinition(SchemeDefinition):
	def connect(self, url, context=None, remotepython="python"):
		context = getcontext(context)
		if context is defaultcontext:
			raise ValueError("ssh URLs need a custom context")
		# Use one SshConnection for each user/host/remotepython combination
		server = url.server
		try:
			connections = context.schemes["ssh"]
		except KeyError:
			connections = context.schemes["ssh"] = {}
		try:
			connection = connections[(server, remotepython)]
		except KeyError:
			connection = connections[(server, remotepython)] = SshConnection(context, server, remotepython)
		return connection

	def open(self, url, mode="rb", context=None, remotepython="python"):
		connection = self.connect(url, context, remotepython)
		return RemoteFileResource(connection, url, mode)


schemereg = {
	"http": SchemeDefinition("http", usehierarchy=True, useserver=True, usefrag=True, isremote=True, defaultport=80),
	"https": SchemeDefinition("https", usehierarchy=True, useserver=True, usefrag=True, isremote=True, defaultport=443),
	"ftp": SchemeDefinition("ftp", usehierarchy=True, useserver=True, usefrag=True, isremote=True, defaultport=21),
	"file": LocalSchemeDefinition("file", usehierarchy=True, useserver=False, usefrag=True, islocal=True),
	"root": SchemeDefinition("root", usehierarchy=True, useserver=False, usefrag=True, islocal=True),
	"javascript": SchemeDefinition("javascript", usehierarchy=False, useserver=False, usefrag=False),
	"mailto": SchemeDefinition("mailto", usehierarchy=False, useserver=False, usefrag=False),
	"tel": SchemeDefinition("tel", usehierarchy=False, useserver=False, usefrag=False),
	"fax": SchemeDefinition("fax", usehierarchy=False, useserver=False, usefrag=False),
	"ssh": SshSchemeDefinition("ssh", usehierarchy=True, useserver=True, usefrag=True, islocal=False, isremote=True),
}
defaultreg = LocalSchemeDefinition("", usehierarchy=True, useserver=True, islocal=True, usefrag=True)


class Path(object):
	__slots__ = ("_path", "_segments")

	def __init__(self, path=None):
		self._path = ""
		self._segments = []
		self.path = path

	@classmethod
	def _fixsegment(cls, segment):
		if isinstance(segment, basestring):
			if isinstance(segment, unicode):
				segment = _escape(segment)
			return tuple(_unescape(name) for name in segment.split(";", 1))
		else:
			assert 1 <= len(segment) <= 2, "path segment %r must have length 1 or 2, not %d" % (segment, len(segment))
			return tuple(map(unicode, segment))

	def _prefix(cls, path):
		if path.startswith("/"):
			return "/"
		else:
			return ""

	def insert(self, index, *others):
		segments = self.segments
		segments[index:index] = map(self._fixsegment, others)
		self.segments = segments

	def startswith(self, prefix):
		"""
		Return whether <self/> starts with the path <arg>prefix</arg>. <arg>prefix</arg> will be converted
		to a <class>Path</class> if it isn't one.
		"""
		if not isinstance(prefix, Path):
			prefix = Path(prefix)
		segments = prefix.segments
		if self.isabs != prefix.isabs:
			return False
		if segments and segments[-1] == (u"",) and len(self.segments)>len(segments):
			return self.segments[:len(segments)-1] == segments[:-1]
		else:
			return self.segments[:len(segments)] == segments

	def endswith(self, suffix):
		"""
		Return whether <self/> ends with the path <arg>suffix</arg>. <arg>suffix</arg> will be converted
		to a <class>Path</class> if it isn't one. If <arg>suffix</arg> is absolute a normal
		comparison will be done.
		"""
		if not isinstance(suffix, Path):
			suffix = Path(suffix)
		if suffix.isabs:
			return self == suffix
		else:
			segments = suffix.segments
			return self.segments[-len(segments):] == segments

	def clone(self):
		return Path(self)

	def __repr__(self):
		return "Path(%r)" % self._path

	def __str__(self):
		return self.path

	def __eq__(self, other):
		if not isinstance(other, Path):
			other = Path(other)
		return self._path == other._path

	def __ne__(self, other):
		return not self == other

	def __hash__(self):
		return hash(self._path)

	def __len__(self):
		return len(self.segments)

	def __getitem__(self, index):
		return self.segments[index]

	def __setitem__(self, index, value):
		segments = self.segments
		segments[index] = self._fixsegment(value)
		self._path = self._prefix(self._path) + self._segments2path(segments)
		self._segments = segments

	def __delitem__(self, index):
		segments = self.segments
		del segments[index]
		self._path = self._segments2path(segments)
		self._segments = segments

	def __contains__(self, item):
		return self._fixsegment(item) in self.segments

	def __getslice__(self, index1, index2):
		"""
		Return of slice of the path. The resulting path will always be relative, i.e.
		the leading <lit>/</lit> will be dropped.
		"""
		return Path(self.segments[index1:index2])

	def __setslice__(self, index1, index2, seq):
		segments = self.segments
		segments[index1:index2] = map(self._fixsegment, seq)
		self._path = self._prefix(self._path) + self._segments2path(segments)
		self._segments = segments

	def __delslice__(self, index1, index2):
		del self.segments[index1:index2]

	class isabs(misc.propclass):
		"""
		<par>Is the path absolute?</par>
		"""
		def __get__(self):
			return self._path.startswith("/")
	
		def __set__(self, isabs):
			isabs = bool(isabs)
			if isabs != self._path.startswith("/"):
				if isabs:
					self._path = "/" + self._path
				else:
					self._path = self._path[1:]
	
		def __delete__(self):
			if self._path.startswith("/"):
				self._path = self._path[1:]

	@classmethod
	def _segments2path(cls, segments):
		return "/".join(";".join(_escape(value, pathsafe) for value in segment) for segment in segments)

	@classmethod
	def _path2segments(cls, path):
		if path.startswith("/"):
			path = path[1:]
		return map(cls._fixsegment, path.split("/"))

	def _setpathorsegments(self, path):
		if path is None:
			self._path = ""
			self._segments = []
		elif isinstance(path, Path):
			self._path = path._path
			self._segments = None
		elif isinstance(path, (list, tuple)):
			self._segments = map(self._fixsegment, path)
			self._path = self._prefix(self._path) + self._segments2path(self._segments)
		else:
			if isinstance(path, unicode):
				path = _escape(path)
			prefix = self._prefix(path)
			if prefix:
				path = path[1:]
			self._segments = self._path2segments(path)
			self._path = prefix + self._segments2path(self._segments)

	class path(misc.propclass):
		"""
		<par>The complete path as a string.</par>
		"""
		def __get__(self):
			return self._path

		def __set__(self, path):
			self._setpathorsegments(path)
	
		def __delete__(self):
			self.clear()

	class segments(misc.propclass):
		"""
		<par>The path as a list of (name, param) tuples.</par>
		"""
		def __get__(self):
			if self._segments is None:
				self._segments = self._path2segments(self._path)
			return self._segments
	
		def __set__(self, path):
			self._setpathorsegments(path)

		def __delete__(self):
			self._path = self._prefix(self._path)
			self._segments = []

	class file(misc.propclass):
		"""
		<par>The filename without the path, i.e. the name part of the last component of
		<pyref property="path"><property>path</property></pyref>.
		The <lit>baz.html</lit> part of
		<lit>http://user@www.example.com/bar/baz.html;xyzzy?spam=eggs#frag</lit>.</par>
		"""
		def __get__(self):
			try:
				return self[-1][0]
			except IndexError:
				return None
	
		def __set__(self, file):
			"""
			<par>Setting the filename preserves the parameter in the last segment.</par>
			"""
			if file is None:
				del self.file
			segments = self.segments
			if segments:
				if len(segments[-1]) == 1:
					self[-1] = (file, )
				else:
					self[-1] = (file, segments[-1][1])
			else:
				self.segments = [(file,)]
	
		def __delete__(self):
			"""
			<par>Deleting the filename preserves the parameter in the last segment.</par>
			"""
			segments = self.segments
			if segments:
				if len(segments[-1]) == 1:
					self[-1] = ("", )
				else:
					self[-1] = ("", segments[-1][1])

	class ext(misc.propclass):
		"""
		<par>The filename extension of the last segment of the path. The <lit>html</lit> part of
		<lit>http://user@www.example.com/bar/baz.html;xyzzy?spam=eggs#frag</lit>.</par>
		"""
		def __get__(self):
			ext = None
			segments = self.segments
			if segments:
				name = segments[-1][0]
				pos = name.rfind(".")
				if pos != -1:
					ext = name[pos+1:]
			return ext
	
		def __set__(self, ext):
			"""
			<par>Setting the extension preserves the parameter in the last segment.</par>
			"""
			if ext is None:
				del self.ext
			segments = self.segments
			if segments:
				segment = segments[-1]
				name = segment[0]
				pos = name.rfind(".")
				if pos != -1:
					name = name[:pos+1] + ext
				else:
					name = name + "." + ext
				if len(segment)>1:
					self[-1] = (name, segment[1])
				else:
					self[-1] = (name, )
	
		def __delete__(self):
			"""
			<par>Deleting the extension preserves the parameter in the last segment.</par>
			"""
			segments = self.segments
			if segments:
				segment = segments[-1]
				name = segment[0]
				pos = name.rfind(".")
				if pos != -1:
					name = name[:pos]
					if len(segment)>1:
						self[-1] = (name, segment[1])
					else:
						self[-1] = (name, )

	def withext(self, ext):
		"""
		<par>Return a new <class>Path</class> where the filename extension
		has been replaced with <arg>ext</arg>.</par>
		"""
		path = self.clone()
		path.ext = ext
		return path

	def withoutext(self):
		"""
		<par>Return a new <class>Path</class> where the filename extension
		has been removed.</par>
		"""
		if "/" not in self._path and self._path.rfind(".")==0:
			return Path("./")
		else:
			path = self.clone()
			del path.ext
			return path

	def withfile(self, file):
		"""
		<par>Return a new <class>Path</class> where the filename (i.e. the <rep>name</rep>
		of last component of
		<pyref property="segments"><property>segments</property></pyref>)
		has been replaced with <arg>file</arg>.</par>
		"""
		path = self.clone()
		path.file = file
		return path

	def withoutfile(self):
		"""
		<par>Return a new <class>Path</class> where the filename (i.e. the <rep>name</rep>
		of last component of
		<pyref property="segments"><property>segments</property></pyref>)
		has been removed.</par>
		"""
		if "/" not in self._path:
			return Path("./")
		else:
			path = Path(self)
			del path.file
			return path

	def clear(self):
		self._path = ""
		self._segments = []

	def __div__(self, other):
		"""
		join two paths.
		"""
		if isinstance(other, basestring):
			other = Path(other)
		if isinstance(other, Path):
			newpath = Path()
			# RFC2396, Section 5.2 (5)
			if other.isabs:
				newpath._path = other._path
				newpath._segments = None
			else:
				# the following should be equivalent to RFC2396, Section 5.2 (6) (c)-(f)
				newpath._path = self._prefix(self._path) + self._segments2path(
					_normalizepath(
						self.segments[:-1] + # RFC2396, Section 5.2 (6) (a)
						other.segments # RFC2396, Section 5.2 (6) (b)
					)
				)
				newpath._segments = None
			return newpath
		elif isinstance(other, (list, tuple)): # this makes path/list possible
			return other.__class__(self/path for path in other)
		else: # this makes path/generator possible
			return (self/path for path in other)

	def __rdiv__(self, other):
		"""
		<par>Right hand version of <pyref method="__div__"><method>__div__</method></pyref>.</par>
		<par>This supports list and generators as the left hand side too.</par>
		"""
		if isinstance(other, basestring):
			other = Path(other)
		if isinstance(other, Path):
			return other/self
		elif isinstance(other, (list, tuple)):
			return other.__class__(path/self for path in other)
		else:
			return (path/self for path in other)

	def relative(self, basepath):
		"""
		<par>Return an relative <class>Path</class> <rep>rel</rep> such that
		<lit><arg>basepath</arg>/<rep>rel</rep> == <self/></lit>, i.e. this is the
		inverse operation of <pyref method="__div__"><method>__div__</method></pyref>.</par>
		<par>If <self/> is relative, an identical copy of <self/> will be returned.</par>
		"""
		# if self is relative don't do anything
		if not self.isabs:
			pass # FIXME return self.clone()
		basepath = Path(basepath) # clone/coerce
		self_segments = _normalizepath(self.segments)
		base_segments = _normalizepath(basepath.segments)
		while len(self_segments)>1 and len(base_segments)>1 and self_segments[0]==base_segments[0]:
			del self_segments[0]
			del base_segments[0]
		# build a path from one file to the other
		self_segments[:0] = [(u"..",)]*(len(base_segments)-1)
		if not len(self_segments) or self_segments==[(u"",)]:
			self_segments = [(u".",), (u"",)]
		return Path(self._segments2path(self_segments))

	def reverse(self):
		segments = self.segments
		segments.reverse()
		if segments and segments[0] == (u"",):
			del segments[0]
			segments.append((u"",))
		self.segments = segments

	def normalize(self):
		self.segments = _normalizepath(self.segments)

	def normalized(self):
		new = self.clone()
		new.normalize()
		return new

	def local(self):
		"""
		Return <self/> converted to a filename using the file naming conventions of the OS.
		Parameters will be dropped in the resulting string.
		"""
		path = Path(self._prefix(self._path) + "/".join(segment[0] for segment in self))
		path = path._path
		localpath = urllib.url2pathname(path)
		if path.endswith("/") and not (localpath.endswith(os.sep) or (os.altsep is not None and localpath.endswith(os.altsep))):
			localpath += os.sep
		return localpath

	def abs(self):
		"""
		<par>Return an absolute version of <self/>.</par>
		"""
		path = os.path.abspath(self.local())
		path = path.rstrip(os.sep)
		if path.startswith("///"):
			path = path[2:]
		path = urllib.pathname2url(path.encode("utf-8"))
		if len(self) and self.segments[-1] == ("",):
			path += "/"
		return Path(path)

	def real(self):
		"""
		<par>Return the canonical version of <self/>, eliminating all symbolic links.</par>
		"""
		path = os.path.realpath(self.local())
		path = path.rstrip(os.sep)
		path = urllib.pathname2url(path.encode("utf-8"))
		if path.startswith("///"):
			path = path[2:]
		if len(self) and self.segments[-1] == ("",):
			path += "/"
		return Path(path)


class Query(dict):
	__slots__= ()
	def __init__(self, arg=None, **kwargs):
		if arg is not None:
			if isinstance(arg, dict):
				for (key, value) in arg.iteritems():
					self.add(key, value)
			else:
				for (key, value) in arg:
					self.add(key, value)
		for (key, value) in kwargs.iteritems():
			self.add(key, value)

	def __setitem__(self, key, value):
		dict.__setitem__(self, unicode(key), [unicode(value)])

	def add(self, key, *values):
		key = unicode(key)
		values = map(unicode, values)
		self.setdefault(key, []).extend(values)

	def __xrepr__(self, mode="default"):
		if mode == "cell":
			yield (astyle.style_url, str(self))
		else:
			yield (astyle.style_url, repr(self))


class URL(object):
	"""
	<par>An RFC2396 compliant &url;.</par>
	"""
	def __init__(self, url=None):
		"""
		<par>Create a new <class>URL</class> instance. <arg>url</arg> may be a <class>str</class>
		or <class>unicode</class> instance, or an <class>URL</class> (in which case you'll get of copy
		of <arg>url</arg>), or <lit>None</lit> (which will create an <class>URL</class> referring
		to the <z>current document</z>).</par>
		"""
		self.url = url

	def _clear(self):
		# internal helper method that makes the ``self`` empty.
		self.reg = defaultreg
		self._scheme = None
		self._userinfo = None
		self._host = None
		self._port = None
		self._path = Path()
		self._reg_name = None
		self._query = None
		self._query_parts = None
		self._opaque_part = None
		self._frag = None

	def clone(self):
		"""
		<par>Return an identical copy <self/>.</par>
		"""
		return URL(self)

	@staticmethod
	def _checkscheme(scheme):
		# Check whether ``scheme`` contains only legal characters.
		if scheme[0] not in schemecharfirst:
			return False
		for c in scheme[1:]:
			if c not in schemechar:
				return False
		return True

	class scheme(misc.propclass):
		"""
		<par>the &url; scheme (e.g. <lit>ftp</lit>, <lit>ssh</lit>, <lit>http</lit>
		or <lit>mailto</lit>). The scheme will be <lit>None</lit> if the &url; is
		a relative one.</par>
		"""
		def __get__(self):
			return self._scheme
		def __set__(self, scheme):
			"""
			<par>The scheme will be converted to lowercase on setting (if <arg>scheme</arg> is not <lit>None</lit>,
			otherwise the scheme will be deleted).</par>
			"""
			if scheme is None:
				self._scheme = None
			else:
				scheme = scheme.lower()
				# check if the scheme only has allowed characters
				if not self._checkscheme(scheme):
					raise ValueError("Illegal scheme char in scheme %r" % (scheme, ))
				self._scheme = scheme
			self.reg = schemereg.get(scheme, defaultreg)
		def __delete__(self):
			"""
			<par>Deletes the scheme, i.e. makes the &url; relative.</par>
			"""
			self._scheme = None
			self.reg = defaultreg

	class userinfo(misc.propclass):
		"""
		<par>the user info part of the <class>URL</class>; i.e. the <lit>user</lit>
		part of <lit>http://user@www.example.com:8080/bar/baz.html;xyzzy?spam=eggs#frag</lit>.</par>
		"""
		def __get__(self):
			return self._userinfo
		def __set__(self, userinfo):
			self._userinfo = userinfo
		def __delete__(self):
			self._userinfo = None

	class host(misc.propclass):
		"""
		<par>the host part of the <class>URL</class>; i.e. the <lit>www.example.com</lit>
		part of <lit>http://user@www.example.com:8080/bar/baz.html;xyzzy?spam=eggs#frag</lit>.</par>
		"""
		def __get__(self):
			return self._host
		def __set__(self, host):
			if host is not None:
				host = host.lower()
			self._host = host
		def __delete__(self):
			self._host = None

	class port(misc.propclass):
		"""
		<par>the port number of the <class>URL</class> (as an <class>int</class>)
		or <lit>None</lit> if the <class>URL</class> has none. The <lit>8080</lit>
		in <lit>http://user@www.example.com:8080/bar/baz.html;xyzzy?spam=eggs#frag</lit>.</par>
		"""
		def __get__(self):
			return self._port
		def __set__(self, port):
			if port is not None:
				port = int(port)
			self._port = port
		def __delete__(self):
			self._port = None

	class hostport(misc.propclass):
		"""
		<par>the host and (if specified) the port number of the <class>URL</class>,
		i.e. the <lit>www.example.com:8080</lit> in
		<lit>http://user@www.example.com:8080/bar/baz.html;xyzzy?spam=eggs#frag</lit>.</par>
		"""
		def __get__(self):
			if self.host is not None:
				hostport = _escape(self.host, safe)
				if self.port is not None:
					hostport += ":%d" % self.port
				return hostport
			else:
				return None
		def __set__(self, hostport):
			# find the port number (RFC2396, Section 3.2.2)
			if hostport is None:
				del self.hostport
			else:
				del self.port
				pos = hostport.rfind(":")
				if pos != -1:
					if pos != len(hostport)-1:
						self.port = hostport[pos+1:]
					hostport = hostport[:pos]
				self.host = _unescape(hostport)
		def __delete__(self):
			del self.host
			del self.port

	class server(misc.propclass):
		"""
		<par>the server part of the <class>URL</class>; i.e. the <lit>user@www.example.com</lit>
		part of <lit>http://user@www.example.com/bar/baz.html;xyzzy?spam=eggs#frag</lit>.</par>
		"""
		def __get__(self):
			if self.hostport is not None:
				userinfo = self.userinfo
				if userinfo is not None:
					return _escape(userinfo, safe) + "@" + self.hostport
				else:
					return self.hostport
			else:
				return None
		def __set__(self, server):
			"""
			<par>Setting the server always works even if the current
			<pyref property="scheme"><property>scheme</property></pyref>
			does use <pyref property="opaque_part"><property>opaque_part</property></pyref>
			or <pyref property="reg_name"><property>reg_name</property></pyref>,
			but will be ignored for <pyref property="url"><property>url</property></pyref>.</par>
			"""
			if server is None:
				del self.server
			else:
				# find the userinfo (RFC2396, Section 3.2.2)
				pos = server.find("@")
				if pos != -1:
					self.userinfo = _unescape(server[:pos])
					server = server[pos+1:]
				else:
					del self.userinfo
				self.hostport = server
		def __delete__(self):
			del self.userinfo
			del self.hostport

	class reg_name(misc.propclass):
		"""
		<par>The reg_name part of the <class>URL</class> for hierarchical schemes that
		use a name based <pyref property="authority"><property>authority</property></pyref>
		instead of <pyref property="server"><property>server</property></pyref>.</par>
		"""
		def __get__(self):
			return self._reg_name
		def __set__(self, reg_name):
			if reg_name is None:
				del self.reg_name
			else:
				self._reg_name = reg_name
		def __delete__(self):
			self._reg_name = None

	class authority(misc.propclass):
		"""
		<par>The authority part of the <class>URL</class> for hierarchical schemes. Depending
		on the scheme, this is either <pyref property="server"><property>server</property></pyref>
		or <pyref property="reg_name"><property>reg_name</property></pyref>.</par>
		"""
		def __get__(self):
			if self.reg.useserver:
				return self.server
			else:
				return self.reg_name
		def __set__(self, authority):
			if self.reg.useserver:
				self.server = authority
			else:
				self.reg_name = authority
		def __delete__(self):
			if self.reg.useserver:
				del self.server
			else:
				del self.reg_name

	class isabspath(misc.propclass):
		"""
		<par>Specifies whether the path of a hierarchical <class>URL</class> is absolute,
		(i.e. it has a leading <lit>"/"</lit>). Note that the path will always be absolute if an
		<pyref property="authority"><property>authority</property></pyref> is specified.</par>
		"""
		def __get__(self):
			return (self.authority is not None) or self.path.isabs
		def __set__(self, isabspath):
			self.path.isabs = isabspath

	class path(misc.propclass):
		"""
		<par>The path segments of a hierarchical <class>URL</class>
		as a <pyref class="Path"><class>Path</class></pyref> object.</par>
		"""
		def __get__(self):
			return self._path
		def __set__(self, path):
			self._path = Path(path)
		def __delete__(self):
			self._path = Path()

	class file(misc.propclass):
		"""
		<par>The filename without the path, i.e. the name part of the last component of
		<pyref property="path"><property>path</property></pyref>.
		The <lit>baz.html</lit> part of
		<lit>http://user@www.example.com/bar/baz.html;xyzzy?spam=eggs#frag</lit>.</par>
		"""
		def __get__(self):
			return self.path.file
		def __set__(self, file):
			"""
			<par>Setting the filename preserves the parameter in the last segment.</par>
			"""
			self.path.file = file
		def __delete__(self):
			"""
			<par>Deleting the filename preserves the parameter in the last segment.</par>
			"""
			del self.path.file

	class ext(misc.propclass):
		"""
		<par>The filename extension of the last segment of the path. The <lit>html</lit> part of
		<lit>http://user@www.example.com/bar/baz.html;xyzzy?spam=eggs#frag</lit>.</par>
		"""
		def __get__(self):
			return self.path.ext
		def __set__(self, ext):
			"""
			<par>Setting the extension preserves the parameter in the last segment.</par>
			"""
			self.path.ext = ext
		def __delete__(self):
			"""
			<par>Deleting the extension preserves the parameter in the last segment.</par>
			"""
			del self.path.ext

	class query_parts(misc.propclass):
		"""
		<par>The query component as a dictionary, i.e. <lit>{u"spam": u"eggs"}</lit> from
		<lit>http://user@www.example.com/bar/baz.html;xyzzy?spam=eggs#frag</lit>.</par>
		<par>If the query component couldn't be parsed, <lit>query_parts</lit> will be <lit>False</lit>.</par>
		"""
		def __get__(self):
			return self._query_parts
		def __set__(self, query_parts):
			self._query = _urlencode(query_parts)
			self._query_parts = query_parts
		def __delete__(self):
			self._query = None
			self._query_parts = None

	class query(misc.propclass):
		"""
		<par>The query component, i.e. the <lit>spam=eggs</lit> part of
		<lit>http://user@www.example.com/bar/baz.html;xyzzy?spam=eggs#frag</lit>.</par>
		"""
		def __get__(self):
			if self._query_parts is False:
				return self._query
			else:
				return _urlencode(self._query_parts)
		def __set__(self, query):
			self._query = query
			if query is not None:
				parts = {}
				for part in query.split(u"&"):
					namevalue = part.split(u"=", 1)
					name = _unescape(namevalue[0].replace("+", " "))
					if len(namevalue) == 2:
						value = _unescape(namevalue[1].replace("+", " "))
						parts.setdefault(name, []).append(value)
					else:
						parts = False
						break
				query = parts
			self._query_parts = query
		def __delete__(self):
			self._query = None
			self._query_parts = None

	class opaque_part(misc.propclass):
		"""
		<par>The opaque part (for schemes like <lit>mailto</lit> that are not
		hierarchical).</par>
		"""
		def __get__(self):
			return self._opaque_part
		def __set__(self, opaque_part):
			self._opaque_part = opaque_part
		def __delete__(self):
			self._opaque_part = None

	class frag(misc.propclass):
		"""
		<par>The fragment identifier, which references a part of the resource,
		i.e. the <lit>frag</lit> part of
		<lit>http://user@www.example.com/bar/baz.html;xyzzy?spam=eggs#frag</lit>.</par>
		"""
		def __get__(self):
			return self._frag
		def __set__(self, frag):
			self._frag = frag
		def __delete__(self):
			self._frag = None

	class url(misc.propclass):
		"""
		<par>The complete &url;</par>
		"""
		def __get__(self):
			"""
			<par>Getting <property>url</property> reassembles the &url;
			from the components.</par>
			"""
			result = ""
			if self.scheme is not None:
				result += self.scheme + ":"
			if self.reg.usehierarchy:
				if self.authority is not None:
					result += "//" + self.authority
					if not self.path.isabs:
						result += "/"
				result += str(self.path)
				if self.query is not None:
					result += "?" + self.query
			else:
				result += self.opaque_part
			if self.reg.usefrag and self.frag is not None:
				result += "#" + _escape(self.frag, fragsafe)
			return result

		def __set__(self, url):
			"""
			<par>Setting <property>url</property> parses <arg>url</arg>
			into the components. <arg>url</arg> may also be an <class>URL</class> instance,
			in which case the &url; will be copied.</par>
			"""
			self._clear()
			if url is None:
				return
			elif isinstance(url, URL):
				self.scheme = url.scheme
				self.userinfo = url.userinfo
				self.host = url.host
				self.port = url.port
				self.path = url.path.clone()
				self.reg_name = url.reg_name
				self.opaque_part = url.opaque_part
				self.query = url.query
				self.frag = url.frag
			else:
				if isinstance(url, unicode):
					url = _escape(url)
				# find the scheme (RFC2396, Section 3.1)
				pos = url.find(":")
				if pos != -1:
					scheme = url[:pos]
					if self._checkscheme(scheme): # if the scheme is illegal assume there is none (e.g. "/foo.php?x=http://www.bar.com", will *not* have the scheme "/foo.php?x=http")
						self.scheme = scheme # the info about what we have to expect in the rest of the URL can be found in self.reg now
						url = url[pos+1:]
	
				# find the fragment (RFC2396, Section 4.1)
				if self.reg.usefrag:
					# the fragment itself may not contain a "#", so find the last "#"
					pos = url.rfind("#")
					if pos != -1:
						self.frag = _unescape(url[pos+1:])
						url = url[:pos]
	
				if self.reg.usehierarchy:
					# find the query (RFC2396, Section 3.4)
					pos = url.rfind("?")
					if pos != -1:
						self.query = url[pos+1:]
						url = url[:pos]
					if url.startswith("//"):
						url = url[2:]
						# find the authority part (RFC2396, Section 3.2)
						pos = url.find("/")
						if pos!=-1:
							authority = url[:pos]
							url = url[pos:] # keep the "/"
						else:
							authority = url
							url = "/"
						self.authority = authority
					self.path = Path(url)
				else:
					self.opaque_part = url
		def __delete__(self):
			"""
			<par>After deleting the &url; the resulting object will refer
			to the <z>current document</z>.</par>
			"""
			self._clear()

	def withext(self, ext):
		"""
		<par>Return a new <class>URL</class> where the filename extension
		has been replaced with <arg>ext</arg>.</par>
		"""
		url = URL(self)
		url.path = url.path.withext(ext)
		return url

	def withoutext(self):
		"""
		<par>Return a new <class>URL</class> where the filename extension
		has been removed.</par>
		"""
		url = URL(self)
		url.path = url.path.withoutext()
		return url

	def withfile(self, file):
		"""
		<par>Return a new <class>URL</class> where the filename (i.e. the <rep>name</rep>
		of last component of
		<pyref property="path_segments"><property>path_segments</property></pyref>)
		has been replaced with <arg>filename</arg>.</par>
		"""
		url = URL(self)
		url.path = url.path.withfile(file)
		return url

	def withoutfile(self):
		url = URL(self)
		url.path = url.path.withoutfile()
		return url

	def withfrag(self, frag):
		"""
		<par>Return a new <class>URL</class> where the fragment
		has been replaced with <arg>frag</arg>.</par>
		"""
		url = URL(self)
		url.frag = frag
		return url

	def withoutfrag(self):
		"""
		<par>Return a new <class>URL</class> where the frag has been dropped.</par>
		"""
		url = URL(self)
		del url.frag
		return url

	def __div__(self, other):
		"""
		<par>join <self/> with another (possible relative) <class>URL</class> <arg>other</arg>,
		to form a new <class>URL</class>.</par>
		
		<par><arg>other</arg> may be a <class>str</class>, <class>unicode</class> or
		<class>URL</class> instance. It may be <lit>None</lit> (referring to the <z>current document</z>)
		in which case <self/> will be returned. It may also be a list or other iterable.
		For this case a list (or iterator) will be returned where <method>__div__</method>
		will be applied to every item in the list/iterator. E.g. the following expression
		returns all the files in the current directory as absolute <class>URL</class>s
		(see <pyref method="files"><method>files</method></pyref> and
		<pyref function="here"><function>here</function></pyref> for further
		explanations):</par>
		<tty>
		<prompt>&gt;&gt;&gt; </prompt><input>here = url.here()</input>
		<prompt>&gt;&gt;&gt; </prompt><input>for f in here/here.files():</input>
		<prompt>... </prompt><input>	print f</input>
		</tty>
		"""
		if isinstance(other, basestring):
			other = URL(other)
		if isinstance(other, URL):
			newurl = URL()
			# RFC2396, Section 5.2 (2)
			if other.scheme is None and other.authority is None and str(other.path)=="" and other.query is None:
				newurl = URL(self)
				newurl.frag = other.frag
				return newurl
			if not self.reg.usehierarchy: # e.g. "mailto:x@y"/"file:foo"
				return other
			# In violation of RFC2396 we treat file URLs as relative ones (if the base is a local URL)
			if other.scheme=="file" and self.islocal():
				del other.scheme
				del other.authority
			# RFC2396, Section 5.2 (3)
			if other.scheme is not None:
				return other
			newurl.scheme = self.scheme
			newurl.query = other.query
			newurl.frag = other.frag
			# RFC2396, Section 5.2 (4)
			if other.authority is None:
				newurl.authority = self.authority
				# RFC2396, Section 5.2 (5) & (6) (a) (b)
				newurl._path = self._path/other._path
			else:
				newurl.authority = other.authority
				newurl._path = other._path.clone()
			return newurl
		elif isinstance(other, (list, tuple)): # this makes path/list possible
			return other.__class__(self/path for path in other)
		else: # this makes path/generator possible
			return (self/path for path in other)

	def __rdiv__(self, other):
		"""
		<par>Right hand version of <pyref method="__div__"><method>__div__</method></pyref>.</par>
		<par>This support lists and iterables as the left hand side too.</par>
		"""
		if isinstance(other, basestring):
			other = URL(other)
		if isinstance(other, URL):
			return other/self
		elif isinstance(other, (list, tuple)):
			return other.__class__(item/self for item in other)
		else:
			return (item/self for item in other)

	def relative(self, baseurl):
		"""
		<par>Return an relative <class>URL</class> <rep>rel</rep> such that
		<lit><arg>baseurl</arg>/<rep>rel</rep> == <self/></lit>, i.e. this is the
		inverse operation of <pyref method="__div__"><method>__div__</method></pyref>.</par>
		<par>If <self/> is relative, has a different
		<pyref property="scheme"><property>scheme</property></pyref> or
		<pyref property="authority"><property>authority</property></pyref> than <arg>baseurl</arg>
		or a non-hierarchical scheme, an identical copy of <self/> will be returned.</par>
		"""
		# if self is relative don't do anything
		if self.scheme is None:
			return URL(self)
		# javascript etc.
		if not self.reg.usehierarchy:
			return URL(self)
		baseurl = URL(baseurl) # clone/coerce
		# only calculate a new URL if to the same server, else use the original
		if self.scheme != baseurl.scheme or self.authority != baseurl.authority:
			return URL(self)
		newurl = URL(self) # clone
		del newurl.scheme
		del newurl.authority
		selfpath_segments = _normalizepath(self._path.segments)
		basepath_segments = _normalizepath(baseurl._path.segments)
		while len(selfpath_segments)>1 and len(basepath_segments)>1 and selfpath_segments[0]==basepath_segments[0]:
			del selfpath_segments[0]
			del basepath_segments[0]
		# does the URL go to the same file?
		if selfpath_segments==basepath_segments and self.query==baseurl.query:
			# only return the frag
			del newurl.path
			del newurl.query
		else:
			# build a path from one file to the other
			selfpath_segments[:0] = [(u"..",)]*(len(basepath_segments)-1)
			if not len(selfpath_segments) or selfpath_segments==[(u"",)]:
				selfpath_segments = [(u".",), (u"",)]
			newurl._path.segments = selfpath_segments
			newurl._path = self.path.relative(baseurl.path)
		newurl._path.isabs = False
		return newurl

	def __str__(self):
		return self.url

	def __unicode__(self):
		return self.url

	def __repr__(self):
		return "URL(%r)" % self.url

	def __nonzero__(self):
		"""
		<par>Return whether the <class>URL</class> is not empty, i.e. whether
		it is not the <class>URL</class> referring to the start of the current document.</par>
		"""
		return self.url != ""

	def __eq__(self, other):
		"""
		<par>Return whether two <pyref class="URL"><class>URL</class></pyref> instances are equal.
		Note that only properties relevant for the current scheme will be compared.</par>
		"""
		if self.__class__!=other.__class__:
			return False
		if self.scheme!=other.scheme:
			return False
		if self.reg.usehierarchy:
			if self.reg.useserver:
				selfport = self.port or self.reg.defaultport
				otherport = other.port or other.reg.defaultport
				if self.userinfo!=other.userinfo or self.host!=other.host or selfport!=otherport:
					return False
			else:
				if self.reg_name!=other.reg_name:
					return False
			if self._path!=other._path:
				return False
		else:
			if self.opaque_part!=other.opaque_part:
				return False
		# Use canonical version of (i.e. sorted names and values)
		if self.query != other.query:
			return False
		if self.frag != other.frag:
			return False
		return True

	def __ne__(self, other):
		"""
		<par>Return whether two <pyref class="URL"><class>URL</class></pyref>s are <em>not</em>
		equal.</par>
		"""
		return not self==other

	def __hash__(self):
		"""
		<par>Return a hash value for <self/>, to be able to use <class>URL</class>s as
		dictionary keys. You must be careful not to modify an <class>URL</class> as soon
		as you use it as a dictionary key.</par>
		"""
		res = hash(self.scheme)
		if self.reg.usehierarchy:
			if self.reg.useserver:
				res ^= hash(self.userinfo)
				res ^= hash(self.host)
				res ^= hash(self.port or self.reg.defaultport)
			else:
				res ^= hash(self.reg_name)
			res ^= hash(self._path)
		else:
			res ^= hash(self.opaque_part)
		res ^= hash(self.query)
		res ^= hash(self.frag)
		return res

	def abs(self, scheme=-1):
		"""
		<par>Return an absolute version of <self/> (works only for local &url;s).</par>
		<par>If the argument <arg>scheme</arg> is specified, it will be used for the resulting &url; otherwise the
		result will have the same scheme as <self/>.</par>
		"""
		self._checklocal()
		new = self.clone()
		new.path = self.path.abs()
		if scheme != -1:
			new.scheme = scheme
		return new

	def real(self, scheme=-1):
		"""
		<par>Return the canonical version of <self/>, eliminating of symbolic links (works only for local &url;s).</par>
		<par>If the argument <arg>scheme</arg> is specified, it will be used for the resulting &url; otherwise the
		result will have the same scheme as <self/>.</par>
		"""
		self._checklocal()
		new = self.clone()
		new.path = self.path.real()
		if scheme != -1:
			new.scheme = scheme
		return new

	def islocal(self):
		"""
		<par>return whether <self/> refers to a local file, i.e. whether
		<self/> is a relative <class>URL</class> or the scheme is
		<lit>root</lit> or <lit>file</lit>).</par>
		"""
		return self.reg.islocal

	def _checklocal(self):
		if not self.islocal():
			raise ValueError("URL %r is not local" % self)

	def local(self):
		"""
		<par>Return <self/> as a local filename (which will only works if <self/>
		is local (see <pyref method="islocal"><method>islocal</method></pyref>)).</par>
		"""
		self._checklocal()
		return self.path.local()

	def connect(self, context=None, *args, **kwargs):
		"""
		<par>Return a <pyref class="Connection"><class>Connection</class></pyref>
		object for accessing and modifying <self/>s metadata.</par>

		<par>Whether you get a new connection object, or an existing one depends
		on the scheme, the &url; itself, and the <pyref class="Context">context</pyref>
		passed in (as the <arg>context</arg> argument).</par>
		"""
		return self.reg.connect(self, context=context, *args, **kwargs)

	def open(self, mode="rb", context=None, *args, **kwargs):
		"""
		<par>Open <self/> for reading or writing. <method>open</method> returns
		a <pyref class="Resource"><class>Resource</class></pyref> object.</par>

		<par>Which additional parameters are supported depends on the actual
		resource created. Some common parameters are:</par>

		<dlist>
		<term><arg>mode</arg> (supported by all resources)</term>
		<item>A string indicating how the file is to be opened (just like the mode
		argument for the builtin <function>open</function>; e.g. <lit>"rb"</lit>
		or <lit>"wb"</lit>).</item>

		<term><arg>context</arg> (supported by all resources)</term>
		<item><method>open</method> needs a <pyref class="Connection">connection</pyref>
		for this &url; which it gets from a <pyref class="Context">context</pyref> object.</item>

		<term><arg>headers</arg></term>
		<item>Additional headers to use for an &http; request.</item>

		<term><arg>data</arg></term>
		<item>Request body to use for an &http; POST request.</item>

		<term><arg>remotepython</arg></term>
		<item>Name of the Python interpreter to use on the remote side
		(used by <lit>ssh</lit> &url;s)</item>
		</dlist>
		"""
		connection = self.connect(context=context)
		return connection.open(self, mode, *args, **kwargs)

	def openread(self, context=None, *args, **kwargs):
		return self.open("rb", context, *args, **kwargs)

	def openwrite(self, context=None, *args, **kwargs):
		return self.open("wb", context, *args, **kwargs)

	def __getattr__(self, name):
		"""
		<par><method>__getattr__</method> forwards every unresolved attribute
		access to the appropriate connection. This makes it possible to call
		<class>Connection</class> methods directly on <class>URL</class> objects:</par>

		<tty>
		<prompt>&gt;&gt;&gt; </prompt><input>from ll import url</input>
		<prompt>&gt;&gt;&gt; </prompt><input>u = url.URL("file:README")</input>
		<prompt>&gt;&gt;&gt; </prompt><input>u.size()</input>
		1584L
		</tty>

		<par>instead of:</par>

		<tty>
		<prompt>&gt;&gt;&gt; </prompt><input>from ll import url</input>
		<prompt>&gt;&gt;&gt; </prompt><input>u = url.URL("file:README")</input>
		<prompt>&gt;&gt;&gt; </prompt><input>u.connect().size()</input>
		1584L
		</tty>
		"""
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

	def import_(self, mode="always"):
		"""
		<par>import the file as a Python module.</par>
		<par>The file extension will be ignored, which
		means that you might not get exactly the
		file you specified.</par>
		<par><arg>mode</arg> can have the following values:</par>
		<ulist>
		<item><lit>"always"</lit> (the default): The module will be imported on every call;</item>
		<item><lit>"once"</lit>: The module will be imported only on the first call;</item>
		<item><lit>"new"</lit>: The module will be imported every time it has changed since the last call.</item>
		</ulist>
		"""
		filename = self.real().local()
		if mode=="always":
			mdate = self.mdate()
		elif mode=="once":
			try:
				return importcache[filename][1]
			except KeyError:
				mdate = self.mdate()
		elif mode=="new":
			mdate = self.mdate()
			try:
				(oldmdate, module) = importcache[filename]
			except KeyError:
				pass
			else:
				if mdate<=oldmdate:
					return module
		else:
			raise ValueError, "mode %r unknown" % mode
		module = _import(filename)
		importcache[filename] = (mdate, module)
		return module

	def __iter__(self):
		try:
			isdir = self.isdir()
		except AttributeError:
			isdir = False
		if isdir:
			return iter(self/self.listdir())
		else:
			return iter(self.open())

	def __xrepr__(self, mode="default"):
		if mode == "cell":
			yield (astyle.style_url, str(self))
		else:
			yield (astyle.style_url, repr(self))


warnings.filterwarnings("always", module="url")
