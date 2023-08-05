#! /usr/bin/env/python
# -*- coding: iso-8859-1 -*-

## Copyright 2005 by LivingLogic AG, Bayreuth/Germany.
## Copyright 2005 by Walter Dörwald
##
## All Rights Reserved
##
## See __init__.py for the license


import py.test

import ll


def test_notimplemented():
	class Bad(object):
		@ll.notimplemented
		def bad(self):
			pass

	py.test.raises(NotImplementedError, Bad().bad)
