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
compliant implementation of &url;s (see the class <pyref class="URL"><class>URL</class></pyref>)
and file like classes for reading data from &url;s and writing data to &url;s
(see the classes <pyref class="Resource"><class>Resource</class></pyref>,
<pyref class="ReadResource"><class>ReadResource</class></pyref> and
<pyref class="WriteResource"><class>WriteResource</class></pyref>).</par>
"""


__version__ = tuple(map(int, "$Revision: 1.2 $"[11:-2].split(".")))
# $Source: /data/cvsroot/LivingLogic/Python/core/src/ll/url.py,v $

import sys, os, os.path, urllib, urllib2, new, mimetypes, email.Utils, mimetools, cStringIO, warnings, datetime, cgi

# don't fail when pwd or grp can't be imported, because if this doesn't work,
# we're probably on Windows and os.chown won't work anyway
try:
	import pwd, grp
except ImportError:
	pass

from ll import misc, astyle


os.stat_float_times(True)


def mime2dt(s):
	return datetime.datetime(*email.Utils.parsedate(s)[:7])


def dt2mime(d):
	return email.Utils.formatdate(d.gmticks())


def timestamp2dt(t):
	return datetime.datetime.utcfromtimestamp(t)


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


class SchemeDefinition(object):
	"""
	<par>A <class>SchemeDefinition</class> instance defines the properties
	of a particular &url; scheme.</par>
	"""
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

	def __repr__(self):
		return "<%s instance scheme=%r usehierarchy=%r useserver=%r usefrag=%r at 0x%x>" % (self.__class__.__name__, self.scheme, self.usehierarchy, self.useserver, self.usefrag, id(self))


schemereg = {
	"http": SchemeDefinition("http", usehierarchy=True, useserver=True, usefrag=True, isremote=True, defaultport=80),
	"https": SchemeDefinition("https", usehierarchy=True, useserver=True, usefrag=True, isremote=True, defaultport=443),
	"ftp": SchemeDefinition("ftp", usehierarchy=True, useserver=True, usefrag=True, isremote=True, defaultport=21),
	"file": SchemeDefinition("file", usehierarchy=True, useserver=False, usefrag=True, islocal=True),
	"root": SchemeDefinition("root", usehierarchy=True, useserver=False, usefrag=True, islocal=True),
	"javascript": SchemeDefinition("javascript", usehierarchy=False, useserver=False, usefrag=False),
	"mailto": SchemeDefinition("mailto", usehierarchy=False, useserver=False, usefrag=False),
	"tel": SchemeDefinition("tel", usehierarchy=False, useserver=False, usefrag=False),
	"fax": SchemeDefinition("fax", usehierarchy=False, useserver=False, usefrag=False),
}
defaultreg = SchemeDefinition("", usehierarchy=True, useserver=True, islocal=True, usefrag=True)


def here(scheme="file"):
	"""
	<par>Return the current directory as an <pyref class="URL"><class>URL</class></pyref>.</par>
	"""
	return Dir(os.getcwd(), scheme)


def home(user="", scheme="file"):
	"""
	<par>Return the home directory of the current user (or the user named <arg>user</arg>, if <arg>user</arg> is specified)
	as an <pyref class="URL"><class>URL</class></pyref>.</par>
	<prog>
	&gt;&gt;&gt; url.home()
	URL('file:/home/walter/')
	&gt;&gt;&gt; url.home("andreas")
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
	<par>Turn a filename into an <pyref class="URL"><class>URL</class></pyref>.</par>
	"""
	name = urllib.pathname2url(os.path.expanduser(name).encode("utf-8"))
	if name.startswith("///"):
		name = name[2:]
	url = URL(name)
	url.scheme = scheme
	return url


def Dir(name, scheme="file"):
	"""
	<par>Turns a directory name into an <pyref class="URL"><class>URL</class></pyref>, just like
	<pyref function="File"><function>File</function></pyref>, but ensures that the path
	is terminated with a <lit>/</lit>.</par>
	"""
	name = urllib.pathname2url(os.path.expanduser(name).encode("utf-8"))
	if not name.endswith("/"):
		name += "/"
	if name.startswith("///"):
		name = name[2:]
	url = URL(name)
	url.scheme = scheme
	return url


def first(urls):
	"""
	<par>Return the first &url; from <arg>urls</arg> that exists as a real local file or directory.</par>
	<par><lit>None</lit> entries in <arg>urls</arg> will be skipped.</par>
	"""
	for url in urls:
		if url is not None:
			if url.exists():
				return url


def firstdir(urls):
	"""
	<par>Return the first &url; from <arg>urls</arg> that exists as a real local directory.</par>
	<par><lit>None</lit> entries in <arg>urls</arg> will be skipped.</par>
	"""
	for url in urls:
		if url is not None:
			if url.isdir():
				return url


def firstfile(urls):
	"""
	<par>Return the first &url; from <arg>urls</arg> that exists as a real local file.</par>
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
		<lit>http://user@www.foo.com/bar/baz.html;xyzzy?spam=eggs#frag</lit>.</par>
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
		<lit>http://user@www.foo.com/bar/baz.html;xyzzy?spam=eggs#frag</lit>.</par>
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
		if isinstance(other, list):
			return [ self/path for path in other ] # this makes path/list possible
		if not isinstance(other, Path):
			other = Path(other)
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

	def __rdiv__(self, other):
		"""
		<par>Right hand version of <pyref method="__div__"><method>__div__</method></pyref>.</par>
		<par>This supports list as the left hand side too.</par>
		"""
		if isinstance(other, list):
			return [ path/self for path in other ] # this makes list/path possible
		return Path(other)/self

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

	def access(self, mode):
		"""
		<par>Test for access to the resource.</par>
		"""
		return os.access(self.local(), mode)

	def chdir(self):
		"""
		<par>Change into the directory <self/>.</par>
		"""
		return os.chdir(self.local())

	def chmod(self, mode):
		"""
		<par>Change the access permissions of a file.</par>
		"""
		return os.chmod(self.local(), mode)

	def __chown(self, func, user, group):
		"""
		<par>internal helper for <pyref method="chown"><method>chown</method></pyref> and
		<pyref method="lchown"><method>lchown</method></pyref>.</par>
		"""
		filename = self.local()
		if user is None or group is None:
			stat = os.stat(filename)
		if user is None:
			user = stat.st_uid
		elif isinstance(user, basestring):
			user = pwd.getpwnam(user)[2]

		if group is None:
			group = stat.st_gid
		elif isinstance(group, basestring):
			group = grp.getgrnam(group)[2]
		return func(filename, user, group)

	def chown(self, user=None, group=None):
		"""
		<par>Change the owner and group of <self/> to the user <arg>user</arg> and group <arg>group</arg>.
		<arg>user</arg> and <arg>group</arg> may be either numeric ids or name for the user or group or
		they may be <lit>None</lit> it which case no change will be made.</par>
		"""
		return self.__chown(os.chown, user, group)

	def lchown(self, user=None, group=None):
		"""
		<par>Change the owner and group of <self/> to the user <arg>user</arg> and group <arg>group</arg>.
		<arg>user</arg> and <arg>group</arg> may be either numeric ids or name for the user or group or
		they may be <lit>None</lit> it which case no change will be made.
		(Like <pyref method="chown"><method>chown</method></pyref>, but does not follow symbolic links).</par>
		"""
		return self.__chown(os.lchown, user, group)

	def stat(self):
		"""
		<par>Perform a stat system call on the given path <self/>. (works only for local &url;s).</par>
		"""
		return os.stat(self.local())

	def lstat(self):
		"""
		<par>Perform a stat system call on the given path <self/>. (Like
		<pyref method="stat"><method>stat</method></pyref>, but
		does not follow symbolic links).</par>
		"""
		return os.lstat(self.local())

	def atime(self):
		"""
		<par>Return the last access time of the file.</par>
		"""
		return timestamp2dt(os.path.getatime(self.local()))

	def mtime(self):
		"""
		<par>Return the last modification time of the file.</par>
		"""
		return timestamp2dt(os.path.getmtime(self.local()))

	def size(self):
		"""
		<par>Return the size of the file.</par>
		"""
		return os.path.getsize(self.local())

	def rename(self, new):
		"""
		<par>Renames <self/> to <arg>new</arg>.</par>
		"""
		if not isinstance(new, Path):
			new = Path(new)
		return os.rename(self.local(), new.local())

	def remove(self):
		"""
		<par>Delete the file <self/>.</par>
		"""
		return os.remove(self.local())

	def makedir(self, mode=0777):
		"""
		<par>Make the directory <self/>.</par>
		"""
		return os.makedir(self.local(), mode)

	def makedirs(self, mode=0777):
		"""
		<par>Make the directory <self/> and all intermediate directories.</par>
		"""
		return os.makedirs(self.local(), mode)

	def makefifo(self, mode=0666):
		"""
		<par>Create a FIFO (i.e. a named pipe).</par>
		"""
		return os.mkfifo(self.local(), mode)

	def link(self, target):
		"""
		<par>Create a hard link to <arg>target</arg>.</par>
		"""
		if not isinstance(target, Path):
			target = Path(target)
		return os.link(self.local(), target.local())

	def symlink(self, target):
		"""
		<par>Create a symbolic link to <arg>target</arg>.</par>
		"""
		if not isinstance(target, Path):
			target = Path(target)
		return os.symlink(self.local(), target.local())

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
			mtime = self.mtime()
		elif mode=="once":
			try:
				return importcache[filename][1]
			except KeyError:
				mtime = self.mtime()
		elif mode=="new":
			mtime = self.mtime()
			try:
				(oldmtime, module) = importcache[filename]
			except KeyError:
				pass
			else:
				if mtime<=oldmtime:
					return module
		else:
			raise ValueError, "mode %r unknown" % mode
		module = _import(filename)
		importcache[filename] = (mtime, module)
		return module


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
		"""
		<par>internal helper method that makes the &url; empty.</par>
		"""
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

	def _checkscheme(scheme):
		"""
		<par>Check whether <arg>scheme</arg> consists of legal characters.</par>
		"""
		# check if the scheme only has allowed characters
		if scheme[0] not in schemecharfirst:
			return False
		for c in scheme[1:]:
			if c not in schemechar:
				return False
		return True
	_checkscheme = staticmethod(_checkscheme)

	class scheme(misc.propclass):
		"""
		<par>the &url; scheme (e.g. <lit>ftp</lit>, <lit>http</lit> or <lit>mailto</lit>).
		The scheme will be <lit>None</lit> if the &url; is a relative one.</par>
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
		part of <lit>http://user@www.foo.com:8080/bar/baz.html;xyzzy?spam=eggs#frag</lit>.</par>
		"""
		def __get__(self):
			return self._userinfo
		def __set__(self, userinfo):
			self._userinfo = userinfo
		def __delete__(self):
			self._userinfo = None

	class host(misc.propclass):
		"""
		<par>the host part of the <class>URL</class>; i.e. the <lit>www.foo.com</lit>
		part of <lit>http://user@www.foo.com:8080/bar/baz.html;xyzzy?spam=eggs#frag</lit>.</par>
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
		in <lit>http://user@www.foo.com:8080/bar/baz.html;xyzzy?spam=eggs#frag</lit>.</par>
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
		i.e. the <lit>www.foo.com:8080</lit> in
		<lit>http://user@www.foo.com:8080/bar/baz.html;xyzzy?spam=eggs#frag</lit>.</par>
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
		<par>the server part of the <class>URL</class>; i.e. the <lit>user@www.foo.com</lit>
		part of <lit>http://user@www.foo.com/bar/baz.html;xyzzy?spam=eggs#frag</lit>.</par>
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
		<lit>http://user@www.foo.com/bar/baz.html;xyzzy?spam=eggs#frag</lit>.</par>
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
		<lit>http://user@www.foo.com/bar/baz.html;xyzzy?spam=eggs#frag</lit>.</par>
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
		<lit>http://user@www.foo.com/bar/baz.html;xyzzy?spam=eggs#frag</lit>.</par>
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
		<lit>http://user@www.foo.com/bar/baz.html;xyzzy?spam=eggs#frag</lit>.</par>
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
		<lit>http://user@www.foo.com/bar/baz.html;xyzzy?spam=eggs#frag</lit>.</par>
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

	def withExt(self, ext):
		return self.withext(ext)

	def withoutext(self):
		"""
		<par>Return a new <class>URL</class> where the filename extension
		has been removed.</par>
		"""
		url = URL(self)
		url.path = url.path.withoutext()
		return url

	def withoutExt(self):
		return self.withoutext()

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

	def withFile(self, file):
		return self.withfile(file)

	def withoutfile(self):
		url = URL(self)
		url.path = url.path.withoutfile()
		return url

	def withFragment(self, frag):
		return self.withfrag()

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

	def __div__(self, otherurl):
		"""
		<par>join <self/> with another (possible relative) <class>URL</class> <arg>otherurl</arg>, to form a new <class>URL</class>.</par>
		<par><arg>otherurl</arg> may be a <class>str</class>, <class>unicode</class> or
		<class>URL</class> instance. It may be <lit>None</lit> (referring to the <z>current document</z>)
		in which case <self/> will be returned. It may also be a list. For this case a list
		will be returned where <method>__div__</method> will be applied to every item in the list. E.g.
		the following expression returns all the files in the current directory as absolute
		<class>URL</class>s (see <pyref method="files"><method>files</method></pyref> and
		<pyref function="here"><function>here</function></pyref> for further explanations):</par>
		<prog>
		url.here()/url.here().files()
		</prog>
		"""
		if isinstance(otherurl, list):
			return [ self/url for url in otherurl ] # this makes url/list possible
		otherurl = URL(otherurl)
		newurl = URL()
		# RFC2396, Section 5.2 (2)
		if otherurl.scheme is None and otherurl.authority is None and str(otherurl.path)=="" and otherurl.query is None:
			newurl = URL(self)
			newurl.frag = otherurl.frag
			return newurl
		if not self.reg.usehierarchy: # e.g. "mailto:x@y"/"file:foo"
			return otherurl
		# In violation of RFC2396 we treat file URLs as relative ones (if the base is a local URL)
		if otherurl.scheme=="file" and self.islocal():
			del otherurl.scheme
			del otherurl.authority
		# RFC2396, Section 5.2 (3)
		if otherurl.scheme is not None:
			return otherurl
		newurl.scheme = self.scheme
		newurl.query = otherurl.query
		newurl.frag = otherurl.frag
		# RFC2396, Section 5.2 (4)
		if otherurl.authority is None:
			newurl.authority = self.authority
			# RFC2396, Section 5.2 (5) & (6) (a) (b)
			newurl._path = self._path/otherurl._path
		else:
			newurl.authority = otherurl.authority
			newurl._path = otherurl._path.clone()
		return newurl

	def __rdiv__(self, otherurl):
		"""
		<par>Right hand version of <pyref method="__div__"><method>__div__</method></pyref>.</par>
		<par>This support lists as the left hand side too.</par>
		"""
		if isinstance(otherurl, list):
			return [ url/self for url in otherurl ] # this makes list/url possible
		return URL(otherurl)/self

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

	def islocal(self):
		"""
		<par>return whether <self/> refers to a local file, i.e. whether
		<self/> is a relative <class>URL</class> or the scheme is
		<lit>root</lit> or <lit>file</lit>).</par>
		"""
		return self.reg.islocal

	def _checklocal(self):
		if not self.islocal():
			raise ValueError("cannot convert %r to filename: non local scheme %s not supported" % (self, self.scheme))

	def local(self):
		"""
		<par>Return <self/> as a local filename (which will only works if <self/>
		is local (see <pyref method="islocal"><method>islocal</method></pyref>)).</par>
		"""
		self._checklocal()
		return self.path.local()

	def walk(self, dirsbefore=False, dirsafter=False, files=False):
		"""
		<par>Recursively walk <self/> (if it is a local <class>URL</class>) and
		generate <class>URL</class>s for files and/or directories in <self/>. All <class>URL</class>s
		will be relative to <self/>.</par>
		<par>Arguments have the following meaning:</par>
		<ulist>
		<item><arg>dirsbefore</arg>: Yield directory <class>URL</class>s before
		entering the directory?</item>
		<item><arg>dirsafter</arg>: Yield directory <class>URL</class>s after
		entering the directory?</item>
		<item><arg>files</arg>: Yield files <class>URL</class>s?</item>
		</ulist>
		<par>This method is a generator.</par>
		"""
		for childurl in self.__walk(base=None, dirsbefore=dirsbefore, dirsafter=dirsafter, files=files):
			yield childurl

	def __walk(self, base, dirsbefore, dirsafter, files):
		"""
		<par>Internal helper method for <pyref method="walk"><method>walk</method></pyref>.</par>
		"""
		path = self.local()
		if os.path.isdir(path):
			allfiles = os.listdir(path)
			allfiles.sort()
			url = Dir(path) # adds a trailing / if neccessary
			if base is None:
				base = url
			if dirsbefore:
				yield url.relative(base)
			for file in allfiles:
				file = File(file) # the filename might include #, ? or ;
				for childurl in (url/file).__walk(base=base, dirsbefore=dirsbefore, dirsafter=dirsafter, files=files):
					yield childurl
			if dirsafter:
				yield url.relative(base)
		else:
			if base is None:
				base = self
			if files: # if we have to report files, do it
				yield self.relative(base)

	def files(self):
		"""
		<par>Return a list of all files in the directory <self/> (which must be a
		local <class>URL</class>). If <self/> is a file, a list with <self/> as the only
		entry will be returned. As with <pyref method="walk"><method>walk</method></pyref>
		all <class>URL</class>s will be relative to <self/>.</par>
		"""
		return list(self.walk(files=True))

	def dirs(self):
		"""
		<par>Return a list of all directories in the directory <self/> (which must be a
		local <class>URL</class>). If <self/> is a file, an empty list will be returned.
		As with <pyref method="walk"><method>walk</method></pyref>
		all <class>URL</class>s will be relative to <self/>.</par>
		"""
		return list(self.walk(dirsbefore=True))

	def openread(self, headers=None, data=None):
		"""
		<par>Open <self/> for reading. This returns a
		<pyref class="ReadResource"><class>ReadResource</class></pyref> instance.
		See its <pyref class="ReadResource" method="__init__">constructor</pyref>
		for information about the arguments.</par>
		"""
		return ReadResource(self, headers, data)

	def openwrite(self):
		"""
		<par>Open <self/> for writing. This returns a
		<pyref class="WriteResource"><class>WriteResource</class></pyref> instance.</par>
		"""
		return WriteResource(self)

	def exists(self):
		"""
		<par>Return whether the resource exists (works only for local &url;s).</par>
		"""
		return os.path.exists(self.local())

	def isdir(self):
		"""
		<par>Return whether the resource is a directory (works only for local &url;s).</par>
		"""
		return os.path.isdir(self.local())

	def isfile(self):
		"""
		<par>Return whether the resource is a file (works only for local &url;s).</par>
		"""
		return os.path.isfile(self.local())

	def islink(self):
		"""
		<par>Return whether the resource is a link (works only for local &url;s).</par>
		"""
		return os.path.islink(self.local())

	def ismount(self):
		"""
		<par>Return whether the resource is a mount point (works only for local &url;s).</par>
		"""
		return os.path.ismount(self.local())

	def abs(self, scheme=-1):
		"""
		<par>Return and absolute version of <self/> (works only for local &url;s).</par>
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

	def access(self, mode):
		"""
		<par>Test for access to the resource (works only for local &url;s).</par>
		"""
		self._checklocal()
		return self.path.access(mode)

	def chdir(self):
		"""
		<par>Change into the directory <self/> (works only for local &url;s).</par>
		"""
		self._checklocal()
		return self.path.chdir()

	def chmod(self, mode):
		"""
		<par>Change the access permissions of a file (works only for local &url;s).</par>
		"""
		self._checklocal()
		return self.path.chmod(mode)

	def chown(self, user=None, group=None):
		"""
		<par>Change the owner and group of <self/> to the user <arg>user</arg> and group <arg>group</arg>.
		<arg>user</arg> and <arg>group</arg> may be either numeric ids or name for the user or group or
		they may be <lit>None</lit> it which case no change will be made.
		(works only for local &url;s).</par>
		"""
		self._checklocal()
		return self.path.chown(user, group)

	def lchown(self, user=None, group=None):
		"""
		<par>Change the owner and group of <self/> to the user <arg>user</arg> and group <arg>group</arg>.
		<arg>user</arg> and <arg>group</arg> may be either numeric ids or name for the user or group or
		they may be <lit>None</lit> it which case no change will be made.
		(Like <pyref method="chown"><method>chown</method></pyref>, but
		does not follow symbolic links; works only for local &url;s).</par>
		"""
		self._checklocal()
		return self.path.lchown(user, group)

	def stat(self):
		"""
		<par>Perform a stat system call on the given path <self/>. (works only for local &url;s).</par>
		"""
		self._checklocal()
		return self.path.stat()

	def lstat(self):
		"""
		<par>Perform a stat system call on the given path <self/>. (Like
		<pyref method="stat"><method>stat</method></pyref>, but
		does not follow symbolic links; works only for local &url;s).</par>
		"""
		self._checklocal()
		return self.path.lstat()

	def atime(self):
		"""
		<par>Return the last access time of a local file.</par>
		"""
		self._checklocal()
		return self.path.atime()

	def mtime(self):
		"""
		<par>Return the last modification time of a local file.</par>
		"""
		self._checklocal()
		return self.path.mtime()

	def size(self):
		"""
		<par>Return the size of a local file.</par>
		"""
		self._checklocal()
		return self.path.size()

	def rename(self, new):
		"""
		<par>Renames <self/> to <arg>new</arg> (Both <self/> and <arg>new</arg>
		must be local &url;s).</par>
		"""
		self._checklocal()
		if not isinstance(new, URL):
			new = URL(new)
		new._checklocal()
		return self.path.rename(new.path)

	def remove(self):
		"""
		<par>Delete the file <self/> (works only for local &url;s).</par>
		"""
		self._checklocal()
		return self.path.remove()

	def makedir(self, mode=0777):
		"""
		<par>Make the directory <self/> (works only for local &url;s).</par>
		"""
		self._checklocal()
		return self.path.makedir(mode)

	def makedirs(self, mode=0777):
		"""
		<par>Make the directory <self/> and all intermediate directories
		(works only for local &url;s).</par>
		"""
		self._checklocal()
		return self.path.makedirs(mode)

	def makefifo(self, mode=0666):
		"""
		<par>Create a FIFO (i.e. a named pipe) (works only for local &url;s).</par>
		"""
		self._checklocal()
		return self.path.makefifo(mode)

	def link(self, target):
		"""
		<par>Create a hard link to <arg>target</arg> ((Both <self/> and <arg>target</arg> must be local &url;s).</par>
		"""
		self._checklocal()
		if not isinstance(target, URL):
			target = url.URL(target)
		target._checklocal()
		return self.path.link(target.path)

	def symlink(self, target):
		"""
		<par>Create a symbolic link to <arg>target</arg> ((Both <self/> and <arg>target</arg> must be local &url;s).</par>
		"""
		self._checklocal()
		if not isinstance(target, URL):
			target = url.URL(target)
		target._checklocal()
		return self.path.symlink(target.path)

	def import_(self, mode="always"):
		self._checklocal()
		return self.path.import_(mode)

	def __xrepr__(self, mode="default"):
		if mode == "cell":
			yield (astyle.style_url, str(self))
		else:
			yield (astyle.style_url, repr(self))


class Resource(object):
	def __init__(self, url):
		self.url = URL(url)

	def __repr__(self):
		return "<%s instance for %r at 0x%x>" % (self.__class__.__name__, self.url, id(self))

	class imagesize(misc.propclass):
		"""
		The size of the image as a (x, y) tuple
		"""
		def __get__(self):
			if not hasattr(self, "_imagesize"):
				try:
					import Image
				except ImportError:
					raise IOError("feature not available (no PIL)")
				img = Image.open(cStringIO.StringIO(self.resdata))
				self._imagesize = img.size
			return self._imagesize

	def import_(self, mode="always"):
		return self.url.import_(mode)


class ReadResource(Resource):
	"""
	<par>A <class>file</class> like object from which the content of an
	<pyref class="URL"><class>URL</class></pyref> can be read.</par>
	<par><class>ReadResource</class> tries to defer opening the connection
	as long as possible, i.e. creating a <class>ReadResource</class> instance
	does not open a connection, only accessing the relevant properties will.</par>
	"""
	def __init__(self, url, headers, data):
		"""
		<par>Create a new resource object for reading.</par>
		<par><arg>headers</arg> (which must be a mapping) will be used
		for additional headers to be passed in the request and data
		(which also is a mapping) will be used as the data for a
		<lit>POST</lit> request.</par>
		"""
		Resource.__init__(self, url)
		if url.islocal():
			self.filename = url.real().local() # protects against calls to os.chdir
		if headers is not None:
			headers = headers.copy()
		self.reqheaders = headers
		if data is not None:
			data = data.copy()
		self.reqdata = data
		self._finalurl = None

	def _open(self):
		"""
		<par>internal helper that opens the resource on demand.</par>
		"""
		if not hasattr(self, "_stream"):
			if hasattr(self, "filename"):
				self._stream = open(self.filename, "rb")
				self._finalurl = self.url
			else:
				data = self.reqdata
				if data is not None:
					data = urllib.urlencode(data)
				headers = self.reqheaders
				if headers is None:
					headers = {}
				req = urllib2.Request(url=self.url.url, data=data, headers=headers)
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

				l = self._resheaders.get("Content-Length")
				if l:
					l = int(l)
				self._contentlength = l
				m = self._resheaders.get("Last-Modified")
				if m is not None:
					m = mime2dt(m)
				self._lastmodified = m
			self._buffer = cStringIO.StringIO() # here the bytes read from the stream will be cached

	def close(self):
		"""
		<par>Close the resource</par>
		"""
		if hasattr(self, "_stream"):
			self._stream.close()
			del self._stream

	class lastmodified(misc.propclass):
		"""
		<par>The last modification date (in UTC) of the resource as a
		<class>datetime.datetime</class> object.</par>
		"""
		def __get__(self):
			if not hasattr(self, "_lastmodified"):
				if hasattr(self, "filename"): # local file
					self._lastmodified = timestamp2dt(self.stats.st_mtime)
				else:
					self._open()
			return self._lastmodified

	class contentlength(misc.propclass):
		"""
		<par>The size of the resource in bytes</par>
		"""
		def __get__(self):
			if not hasattr(self, "_contentlength"):
				if hasattr(self, "filename"): # local file
					self._contentlength = self.stats.st_size
				else:
					self._open()
			return self._contentlength

	class mimetype(misc.propclass):
		"""
		<par>The &mime; type of the resource</par>
		"""
		def __get__(self):
			if not hasattr(self, "_mimetype"):
				if hasattr(self, "filename"): # local file
					mimetype = mimetypes.guess_type(self.filename)[0]
					if mimetype is None:
						self._mimetype = "application/octetstream"
					else:
						self._mimetype = mimetype
				else:
					self._open()
			return self._mimetype

	class encoding(misc.propclass):
		"""
		<par>The character encoding of the resource</par>
		"""
		def __get__(self):
			if not hasattr(self, "_encoding"):
				if hasattr(self, "filename"): # local file
					self._encoding = None # we can't determine the encoding for local files
				else:
					self._open()
			return self._encoding

	class resheaders(misc.propclass):
		"""
		<par>The headers of the response as a <class>mimetools.Message</class> object</par>
		"""
		def __get__(self):
			if not hasattr(self, "_resheaders"):
				if hasattr(self, "filename"): # local file
					self._resheaders = mimetools.Message(
						cStringIO.StringIO(
							"Content-Type: %s/%s\nContent-Length: %d\nLast-modified: %s\n" %
							(self.mimetype[0], self.mimetype[1], self.contentlength, dt2mime(self.lastmodified))
						)
					)
				else:
					self._open()
			return self._resheaders

	class stats(misc.propclass):
		"""
		<par>The result of a <function>os.stat</function> call
		(or <lit>None</lit> for a non-local resource)</par>
		"""
		def __get__(self):
			if not hasattr(self, "_stats"):
				if hasattr(self, "filename"): # local file
					self._stats = os.stat(self.filename)
				else:
					self._stats = None
			return self._stats

	class finalurl(misc.propclass):
		"""
		The real &url; of the resource (this might be different from
		<lit><self/>.url</lit> in case of a redirect).
		"""
		def __get__(self):
			self._open()
			return self._finalurl
		
	def read(self, size=-1):
		self._open()
		data = self._stream.read(size)
		self._buffer.write(data)
		return data

	class resdata(misc.propclass):
		"""
		<par>The content of the resource as a byte string</par>
		"""
		def __get__(self):
			self._open()
			self.read() # read the rest
			data = self._buffer.getvalue()
			self.close()
			return data


class WriteResource(Resource):
	def __init__(self, url):
		"""
		<par>Create a new resource object for writing
		(only local <pyref class="URL"><class>URL</class></pyref>s are supported).</par>
		"""
		Resource.__init__(self, url)
		if not url.islocal():
			raise ValueError("cannot open %r for writing: non local scheme %s not supported" % (self.url, self.url.scheme))
		self.filename = url.real().local() # protects against calls to os.chdir

	def __del__(self):
		self.close()

	def _open(self):
		if not hasattr(self, "_stream"):
			try:
				self._stream = open(self.filename, "wb+")
			except IOError, ex:
				if ex[0] != 2: # didn't work for some other reason than a non existing directory
					raise
				(splitpath, splitname) = os.path.split(self.filename)
				if splitpath == "": # we don't really have a parent
					raise # we don't have a directory to make so pass the error on
				else:
					os.makedirs(splitpath)
					self._stream = open(self.filename, "wb")
			# directly wire write to the write method of the underlying stream
			self.write = self._stream.write

	def write(self, data):
		self._open()
		self.write(data) # this has been rewired to be a bound method in the instance

	def tell(self):
		if hasattr(self, "_stream"):
			return self._stream.tell()
		else:
			return 0

	def close(self):
		"""
		<par>Close the resource</par>
		"""
		if hasattr(self, "_stream"):
			self._stream.close() # we keep the stream and the bound write method around to be able to distinguish a resource that has never been written too, from one that has been closed.
		# if we've never written to the file, do it now, so the empty file will be created
		else:
			self.write("")
			self.close()

	class stats(misc.propclass):
		"""
		<par>The result of a <function>os.stat</function> call.</par>
		"""
		def __get__(self):
			if hasattr(self, "_stream"):
				return os.fstat(self._stream.fileno())
			else:
				return None

	class lastmodified(misc.propclass):
		"""
		<par>The last modification date of the resource as a <class>datetime.datetime</class> object.</par>
		"""
		def __get__(self):
			stats = self.stats
			if stats is not None:
				return timestamp2dt(stats.st_mtime)
			else:
				return None

	class contentlength(misc.propclass):
		"""
		<par>The size of the resource in bytes</par>
		"""
		def __get__(self):
			return self.tell()

	class mimetype(misc.propclass):
		"""
		<par>The &mime; type of the resource as a (maintype, subtype) tuple</par>
		"""
		def __get__(self):
			if not hasattr(self, "_mimetype"):
				mimetype = mimetypes.guess_type(self.filename)[0]
				if mimetype is None:
					self._mimetype = ("text", "plain")
				else:
					self._mimetype = tuple(mimetype.split("/"))
			return self._mimetype

	class resheaders(misc.propclass):
		"""
		<par>The headers of the response as a <class>mimetools.Message</class> object</par>
		"""
		def __get__(self):
			return mimetools.Message(
				cStringIO.StringIO(
					"Content-Type: %s/%s\nContent-Length: %d\nLast-modified: %s\n" %
					(self.mimetype[0], self.mimetype[1], self.contentlength, email.Utils.formatdate(self.lastmodified.gmticks()))
				)
			)

	class resdata(misc.propclass):
		"""
		<par>The content of the resource as a byte string</par>
		"""
		def __get__(self):
			"""
			<par>Getting this property returns the bytes that have been written to
			the resouce so far.</par>
			"""
			if hasattr(self, "_stream"):
				self._stream.seek(0)
				data = self._stream.read()
				return data
			else:
				return ""
		def __set__(self, data):
			"""
			<par>Setting this property will write <arg>data</arg> to the resource.</par>
			"""
			if hasattr(self, "_stream") and self.contentlength:
				raise ValueError("resource %r has already been written to")
			self._open()
			self.write(data)
			self.close()


warnings.filterwarnings("always", module="url")
