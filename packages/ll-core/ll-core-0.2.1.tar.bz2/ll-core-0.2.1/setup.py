#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

# Setup script for ll-core

__version__ = "$Revision: 1.4 $"[11:-2]
# $Source: /data/cvsroot/LivingLogic/Python/core/setup.py,v $

from distutils.core import setup
import textwrap

DESCRIPTION = """
ll-core is a set of various utilities used by the other
LivingLogic packages.
"""

CLASSIFIERS="""
Development Status :: 4 - Beta
Intended Audience :: Developers
License :: OSI Approved :: Python License (CNRI Python License)
Operating System :: OS Independent
Programming Language :: Python
"""

KEYWORDS = """
property
decorator
"""

DESCRIPTION = "\n".join(textwrap.wrap(DESCRIPTION.strip(), width=64, replace_whitespace=True))

setup(
	name="ll-core",
	version="0.2.1",
	description="Various utilities",
	long_description=DESCRIPTION,
	author=u"Walter Dörwald",
	author_email="walter@livinglogic.de",
	url="http://www.livinglogic.de/Python/core/",
	download_url="http://www.livinglogic.de/Python/core/Download.html",
	license="Python",
	classifiers=CLASSIFIERS.strip().splitlines(),
	keywords=",".join(KEYWORDS.strip().splitlines()),
	packages=["ll"],
	package_dir={"ll": "."},
)
