Content
-------

ll-core is a collection of the following modules:

* ``astyle`` can be used for colored terminal output (via ANSI escape
  sequences).

* ``color`` provides classes and functions for handling RGB color values.
  This includes the ability to convert between different color models
  (RGB, HSV, HLS) as well as to and from CSS format, and several functions
  for modifying and mixing colors.

* ``make`` is an object oriented make replacement. Like make it allows you
  to specify dependencies between files and actions to be executed
  when files don't exist or are out of date with respect to one
  of their sources. But unlike make you can do this in a object oriented
  way and targets are not only limited to files, but you can implement
  e.g. dependencies on database records.

* ``misc`` provides several small utility functions and classes.

* ``sisyphus`` provides classes for running Python scripts as cron jobs.

* ``daemon`` can be used on UNIX to fork a daemon process.

* ``url`` provides classes for parsing and constructing RFC 2396
  compliant URLs.

* ``xpit`` is a module that makes it possible to embed Python expressions
  in text (as XML style processing instructions).

* ``xml_codec`` contains a complete codec for encoding and decoding XML.


Documentation
-------------

For documentation read the source or the `web pages`_.

.. _web pages: http://www.livinglogic.de/Python/core/

For requirements and installation instructions read ``INSTALL`` or the
`installation web page`_.

.. _installation web page: http://www.livinglogic.de/Python/core/Installation.html

For a list of new features and bugfixes read ``NEWS`` or the
`history web page`_.

.. _history web page: http://www.livinglogic.de/Python/core/History.html

For a list of old features and bugfixes read ``OLDNEWS`` or the
`old history web page`_.

.. _old history web page: http://www.livinglogic.de/Python/core/OldHistory.html

For the license read ``__init__.py``.


Download
--------

ll-core is available via ftp_, http_, from the cheeseshop_ or as a
`debian package`_.

.. _ftp: ftp://ftp.livinglogic.de/pub/livinglogic/core/
.. _http: http://ftp.livinglogic.de/core/
.. _cheeseshop: http://cheeseshop.python.org/pypi/ll-core
.. _debian package: http://packages.debian.org/python-ll-core


-- Walter Dörwald <walter@livinglogic.de>
