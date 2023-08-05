History
=======


Changes in 1.11.1 (released 01/11/2008)
---------------------------------------

*	Added missing source file ``_xml_codec_include.c`` to the source
	distributions.


Changes in 1.11 (released 01/07/2008)
-------------------------------------

*	``root:`` URLs are now treated as local files for purposes of file i/o.

*	:class:`ll.make.ModuleAction` no longer supports modules that fiddle with
	``sys.modules``.

*	The function :func:`ll.misc.tokenizepi` can be used to split a string
	according to the processing instruction tags in the string (this formerly
	was part of :mod:`ll.xist.xsc`).

*	:mod:`ll.make` has been changed interally to store modification timestamp,
	which should fix the implementation of :class:`PhonyAction` and makes it
	possible to use :class:`PhonyAction` objects as inputs to other actions.

*	:mod:`ll.make` has a new action :class:`ImportAction`. This action doesn't
	take any input. It imports a module specified by name, e.g.
	``make.ImportAction("cStringIO")`` (Note that you should not import one
	module via :class:`ModuleAction` and :class:`ImportAction` (or a normal
	import) as this will return two different module objects).

*	Make actions don't have the input actions as a constructor parameter any
	longer. The input action can now only be set via :meth:`__div__`.

*	:mod:`ll.make` has been updated to support the actions required by XIST 3.0.

*	The functions :func:`misc.item`, :func:`misc.first`, :func:`misc.last` and
	:func:`misc.count` have been reimplemented in C and should be faster now
	(especally :func:`item` for negative indexes).

*	:class:`misc.Namespace` is gone and has been replaced with :class:`misc.Pool`
	which works similar to the pools use by XIST (in fact XISTs pool class is
	a subclass of :class:`misc.Pool`).

*	The module :mod:`xml_codec` has been added. It contains a complete codec
	for encoding and decoding XML.


Changes in 1.10.1 (released 07/20/2007)
---------------------------------------

*	Fix option handling in :mod:`ll.daemon` (values from the optionparser where
	never used).


Changes in 1.10 (released 06/21/2007)
-------------------------------------

*	:mod:`ll.daemon` now uses :mod:`optparse` to parse the command line options.
	Start options ``restart`` and ``run`` have been added.


Changes in 1.9.1 (released 04/03/2007)
--------------------------------------

*	Fixed a bug in :class:`ll.url.SshConnection`, which was missing a call to
	:func:`urllib.url2pathname`.


Changes in 1.9 (released 03/30/2007)
------------------------------------

*	:class:`ll.url.Context` no longer relies on automatic cleanup for closing
	connections. Instead when a :class:`Context` object is used in a ``with``
	block, all connections will be closed at the end of the block. This should
	finally fix the problem with hanging threads at the end of the program.

*	A script ``ucp.py`` has been added that can be used to copy stuff around::

		$ ucp -v http://www.python.org ssh://root@www.example.net/~joe/public_html/index.html -u joe -g users


Changes in 1.8 (released 03/12/2007)
------------------------------------

*	In calls to :class:`ll.url.URL` methods that get forwarded to a connection
	it's now possible to pass keyword arguments for the connection constructor
	directly to the called method, i.e. you can do::

		>>> u = url.URL("ssh://root@www.example.com/etc/passwd")
		>>> u.size(identity="/root/.ssh/id_rsa")
		1550


Changes in 1.7.5 (released 03/09/2007)
--------------------------------------

*	:class:`ll.url.Resource` now has a method :meth:`encoding` that returns
	``None`` (for "encoding unknown").


Changes in 1.7.4 (released 03/08/2007)
--------------------------------------

*	:class:`ll.url.SshConnection` objects now supports the :var:`identity`
	parameter. This can be used to specify the filename to be used as the
	identity file (private key) for authentication.


Changes in 1.7.3 (released 02/22/2007)
--------------------------------------

* :class:`ll.url.SshConnection` now has a new method :meth:`close` which can be
	used to shut down the communication channel. As a :class:`SshConnection` no
	longer stores a reference to the context, this means that ssh connections are
	shut down immediately after the end of the context in which they are stored.
	This avoids a problem with hanging threads.


Changes in 1.7.2 (released 02/02/2007)
--------------------------------------

*	Fixed a bug in :func:`ll.url._import`.


Changes in 1.7.1 (released 01/24/2007)
--------------------------------------

*	:mod:`ll.astyle` has been updated to the current trunk version of
	IPython__.

	__ http://ipython.scipy.org/

*	As the :mod:`new` module is deprecated, use :mod:`types` instead.


Changes in 1.7 (released 11/23/2006)
------------------------------------

*	Fixed a bug in the user switching in :class:`ll.daemon.Daemon`.

*	Added a new action class :class:`GetAttrAction` to :mod:`ll.make`. This
	action gets an attribute of its input object.


Changes in 1.6.1 (released 11/22/2006)
--------------------------------------

*	:class:`ll.make.ModuleAction` now puts a real filename into the modules
	``__file__`` attribute, so that source code can be displayed in stacktraces.

*	:mod:`ll.astyle` has been fixed to work with the current trunk version of
	IPython__.

	__ http://ipython.scipy.org/


Changes in 1.6 (released 11/08/2006)
------------------------------------

*	:mod:`ll.url` now supports ssh URLs which are files on remote hosts.
	This requires `py.execnet`_. Most of the file data and metadata handling
	has been rewritten to support the requirements of ssh URLs.

	.. _py.execnet: http://codespeak.net/py/current/doc/execnet.html

*	:class:`ll.make.ModeAction` and :class:`ll.make.OwnerAction` are subclasses
	of :class:`ll.make.ExternalAction` now. This means they will execute even in
	"infoonly" mode.

*	Fixed a bug in :meth:`ll.make.JoinAction.get`.

*	Remove the pid file for :meth:`ll.sisyphus.Job` when a
	:class:`KeyboardInterrupt` happens and we're running on Python 2.5.

*	Fixed a longstanding bug in :meth:`ll.sisyphus.Job` which resulted in the
	pid file not being written in certain situations.

*	:class:`ll.daemon.Daemon` now allows to switch the group too.


Changes in 1.5 (released 09/24/2006)
------------------------------------

*	:class:`ll.make.XISTTextAction` is compatible to XIST 2.15 now.

*	The functions :func:`ll.url.Dirname` and :func:`ll.url.Filename` have been
	removed (use :func:`ll.url.Dir` and :func:`ll.url.File` instead).

*	The methods :meth:`ll.url.URL.isLocal` and :meth:`ll.url.URL.asFilename`
	have been removed (use :meth:`ll.url.URL.islocal` and :meth:`ll.url.URL.local`
	instead).


Changes in 1.4 (released 08/23/2006)
------------------------------------

*	A new module has been added: :mod:`ll.daemon` can be used on UNIX to fork a
	daemon running.


Changes in 1.3.2 (released 07/25/2006)
--------------------------------------

*	:class:`ll.make.ModuleAction` now normalizes line feeds, so that this action
	can now be used directly on Windows too.


Changes in 1.3.1 (released 07/06/2006)
--------------------------------------

*	An option ``showinfoonly`` has been added to :class:`ll.make.Project`
	(defaulting to ``False``). This option determines whether actions that run
	in ``infoonly`` mode are reported or not.


Changes in 1.3 (released 06/28/2006)
------------------------------------

*	:mod:`ll.make` has been rewritten. Now there's no longer a distinction
	between :class:`Target`s and :class:`Action`s. Actions can be chained more
	easily and creating an action and registering it with the project are two
	separate steps. Actions can no longer be shared, as each action stores its
	own input actions (but output actions are not stored). "Ids" have been
	renamed to "keys" (and :class:`DBID`/:class:`OracleID` to
	:class:`DBKey`/:class:`OracleKey`). :class:`ImportAction` has been renamed
	to :class:`ModuleAction` and can now turn any string into a module.

*	In :mod:`ll.url` modification dates for local files now include microseconds
	(if the OS supports it).

*	A class :class:`Queue` has been added to :mod:`ll.misc` which provides FIFO
	queues.

*	A decorator :func:`withdoc` has been added to :mod:`ll.misc` that sets the
	docstring on the function it decorates.

*	:mod:`setuptools` is now supported for installation.


Changes in 1.2 (released 12/13/2005)
------------------------------------

*	``None`` is now allowed as a proper data object in :mod:`ll.make` actions.

*	:mod:`ll.xpit` now supports conditionals (i.e. the new processing instruction
	targets ``if``, ``elif``, ``else`` and ``endif``. Now there *must* be a space
	after the target name.


Changes in 1.1.1 (released 11/15/2005)
--------------------------------------

*	Fixed a bug in :meth:`ll.make.Project.buildwithargs`.


Changes in 1.1 (released 10/31/2005)
------------------------------------

*	:class:`ll.make.TOXICAction` no longer takes an :var:`encoding` argument in
	the constructor, but works on unicode strings directly.

*	Two new actions (:class:`DecodeAction` and :class:`EncodeAction`) have been
	added to :mod:`ll.make`.


Changes in 1.0.2 (released 10/24/2005)
--------------------------------------

*	Fixed a bug in :meth:`ll.make.Project.destroy` that broke the
	:meth:`recreate` method.


Changes in 1.0.1 (released 10/18/2005)
--------------------------------------

*	Fixed a bug in :meth:`ll.make.Project.__contains__.`


Changes in 1.0 (released 10/13/2005)
------------------------------------

*	This package now contains the following modules, that have been distributed
	as separate packages previously: :mod:`ansistyle`, :mod:`color`, :mod:`make`,
	:mod:`misc` (which contains the stuff from the old :mod:`ll` package),
	:mod:`sisyphus`, :mod:`url` and :mod:`xpit`.

*	:class:`ll.misc.Iterator` now has a method :meth:`get` that will return a
	default value when the iterator doesn't have the appropriate item.

*	In :mod:`ll.make` the output has been fixed: The ``showactionfull`` flag is
	checked before the ``showaction`` flag and target id's will always be output
	in this mode.
