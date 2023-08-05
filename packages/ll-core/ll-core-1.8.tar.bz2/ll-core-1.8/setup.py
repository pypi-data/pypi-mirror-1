#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

# Setup script for ll-core


__version__ = "$Revision: 1.45.2.4 $"[11:-2]
# $Source: /data/cvsroot/LivingLogic/Python/core/setup.py,v $


try:
	import setuptools as tools
except ImportError:
	from distutils import core as tools


DESCRIPTION = """ll-core is a collection of the following modules:

* ``ansistyle`` can be used for colored terminal output (via ANSI
  escape sequences).

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

* ``url`` contains an RFC2396 compliant implementation of URLs and classes for
  accessing resource metadata (like modification dates or permission bits) as
  well as file like classes for reading data from URLs and writing data to URLs.

* ``xpit`` is a module that makes it possible to embed Python expressions
  in text (as XML style processing instructions).
"""


CLASSIFIERS="""
# Common
Development Status :: 4 - Beta
Intended Audience :: Developers
License :: OSI Approved :: Python License (CNRI Python License)
Operating System :: OS Independent
Programming Language :: Python
Topic :: Software Development :: Libraries :: Python Modules

# ansistyle
Topic :: Terminals
Topic :: Text Processing :: General

# color
Topic :: Multimedia :: Graphics

# make
Topic :: Software Development :: Build Tools

# daemon
Environment :: No Input/Output (Daemon)
Operating System :: POSIX

# url
Topic :: Internet
Topic :: Internet :: File Transfer Protocol (FTP)
Topic :: Internet :: WWW/HTTP

# xpit
Topic :: Text Processing :: Filters
"""


KEYWORDS = """
# misc
property
decorator
iterator

# ansistyle
ANSI
escape sequence
color
terminal

# color
RGB
HSV
HSB
HLS
CSS
red
green
blue
hue
saturation
value
brightness
luminance

# make
make
build

# sisyphus
cron
job

# daemon
daemon
UNIX
fork

# url
URL
RFC 2396
HTTP
FTP
ssh
py.execnet

# xpit
text
template
processing instruction
"""


try:
	news = list(open("NEWS", "r"))
except IOError:
	description = DESCRIPTION.strip()
else:
	underlines = [i for (i, line) in enumerate(news) if line.startswith("===")]
	newnews = []
	news = news[underlines[0]-1:underlines[1]-1]
	indent = min(len(line)-len(line.lstrip()) for line in news if line.startswith(" "))
	newnews = []
	for line in news:
		if line.startswith(" "*indent):
			line = line[indent:]
		newnews.append(line)
	news = "".join(newnews).strip()
	description = "%s\n\n\n%s" % (DESCRIPTION.strip(), news)


args = dict(
	name="ll-core",
	version="1.8",
	description="LivingLogic base package: ansistyle, color, make, sisyphus, xpit, url",
	long_description=description,
	author=u"Walter Doerwald",
	author_email="walter@livinglogic.de",
	url="http://www.livinglogic.de/Python/core/",
	download_url="http://www.livinglogic.de/Python/core/Download.html",
	license="Python",
	classifiers=[c for c in CLASSIFIERS.strip().splitlines() if c.strip() and not c.strip().startswith("#")],
	keywords=", ".join(k for k in KEYWORDS.strip().splitlines() if k.strip() and not k.strip().startswith("#")),
	package_dir={"": "src"},
	py_modules=[
		"ll.misc",
		"ll.astyle",
		"ll.ansistyle",
		"ll.color",
		"ll.make",
		"ll.sisyphus",
		"ll.daemon",
		"ll.url",
		"ll.xpit",
	],
	ext_modules=[
		tools.Extension("ll._url", ["src/ll/_url.c"]),
		tools.Extension("ll._ansistyle", ["src/ll/_ansistyle.c"]),
	],
	namespace_packages=["ll"],
	zip_safe=False
)


if __name__ == "__main__":
	tools.setup(**args)
