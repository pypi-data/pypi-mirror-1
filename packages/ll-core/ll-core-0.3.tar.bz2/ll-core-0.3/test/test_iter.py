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


def test_item():
	e = iter(range(10))
	assert ll.item(e, 0) == 0
	assert ll.item(e, 0) == 1
	assert ll.item(e, -1) == 9
	py.test.raises(IndexError, ll.item, e, -1)
	assert ll.item(e, -1, 42) == 42

	e = iter(range(10))
	assert ll.item(e, 4) == 4

	e = iter(range(10))
	py.test.raises(IndexError, ll.item, e, 10)

	e = iter(range(10))
	assert ll.item(e, 10, 42) == 42

	e = iter(range(10))
	assert ll.item(e, -1) == 9

	e = iter(range(10))
	assert ll.item(e, -10) == 0

	e = iter(range(10))
	py.test.raises(IndexError, ll.item, e, -11)

	e = iter(range(10))
	assert ll.item(e, -11, 42) == 42


def test_first():
	e = iter(range(10))
	assert ll.first(e) == 0
	assert ll.first(e) == 1

	e = iter([])
	py.test.raises(IndexError, ll.first, e)

	e = iter([])
	assert ll.first(e, 42) == 42


def test_count():
	e = iter(range(10))
	assert ll.count(e) == 10
	assert ll.count(e) == 0

	e = iter([])
	assert ll.count(e) == 0


def test_iterator_bool():
	e = ll.Iterator(iter(range(10)))
	assert e

	e = ll.Iterator(iter([]))
	assert not e


def test_iterator_next():
	e = ll.Iterator(iter(range(2)))
	assert e.next() == 0
	assert e.next() == 1
	py.test.raises(StopIteration, e.next)


def test_iterator_getitem():
	e = ll.Iterator(iter(range(10)))
	assert e[0] == 0
	assert e[0] == 1
	assert e[-1] == 9
	py.test.raises(IndexError, e.__getitem__, -1)
