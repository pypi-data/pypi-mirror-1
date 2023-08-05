#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

# Setup script for ll-core


__version__ = "$Revision: 1.12 $"[11:-2]
# $Source: /data/cvsroot/LivingLogic/Python/core/setup.py,v $


# FIXME: Eggs
#try:
#	import ez_setup
#except ImportError:
#	import distutils.core as tools
#else:
#	ez_setup.use_setuptools()
#	import setuptools as tools
import distutils.core as tools

DESCRIPTION = """ll-core is a collection of the following modules::

* ``ansistyle`` wraps an output stream and adds color capability
  via ANSI escape sequences.

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

* ``url`` provides classes for parsing and constructing RFC 2396
  compliant URLs.

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

# url
URL
RFC 2396
HTTP
FTP

# xpit
text
template
processing instruction
"""


tools.setup(
	name="ll-core",
	version="1.2",
	description="LivingLogic base package: ansistyle, color, make, sispyphus, xpit, url",
	long_description=DESCRIPTION,
	author=u"Walter Dörwald".encode("utf-8"),
	author_email="walter@livinglogic.de",
	url="http://www.livinglogic.de/Python/core/",
	download_url="http://www.livinglogic.de/Python/core/Download.html",
	license="Python",
	classifiers=[c for c in CLASSIFIERS.strip().splitlines() if c.strip() and not c.strip().startswith("#")],
	keywords=", ".join(k for k in KEYWORDS.strip().splitlines() if k.strip() and not k.strip().startswith("#")),
	py_modules=[
		"ll.misc",
		"ll.ansistyle",
		"ll.color",
		"ll.make",
		"ll.sisyphus",
		"ll.url",
		"ll.xpit",
	],
	package_dir={"ll": ""},
	ext_modules=[
		tools.Extension("ll._ansistyle", ["_ansistyle.c"]),
		tools.Extension("ll._url", ["_url.c"])
	]
)
