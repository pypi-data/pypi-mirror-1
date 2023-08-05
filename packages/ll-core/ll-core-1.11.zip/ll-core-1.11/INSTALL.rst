Requirements
============

To use this package you need the following software packages:

	1.	`Python 2.5`_;

	2.	A C compiler supported by distutils (if you want to install from source);

	3.	XIST_ version 3.0 or later (if you want to use the XIST classes for
		transforming XML with :mod:`ll.make`);

	4.	ll-toxic_ version 0.7 or later (if you want to use :class:`TOXICAction`
		or :class:`TOXICPrettifyAction` for generating Oracle functions with
		:mod:`ll.make`);

	5.	`Apache FOP`_ (if you want to use :class:`FOPAction` for generating PDFs
		from XSL-FO with :mod:`ll.make`).

	6.	setuptools_ (if you want to install this package as an egg);

	7. py.test_ (if you want to run the test suite).

	.. _Python 2.5: http://www.python.org/
	.. _XIST: http://www.livinglogic.de/Python/xist
	.. _ll-toxic: http://www.livinglogic.de/Python/toxic
	.. _Apache FOP: http://xml.apache.org/fop/index.html
	.. _setuptools: http://peak.telecommunity.com/DevCenter/setuptools
	.. _py.test: http://codespeak.net/py/current/doc/test.html


Installation
============

``distutils`` is used for installation, so it's rather simple. Execute the
following command::

	$ python setup.py install

This will compile the C sources and copy the required files to the
``site-packages`` directory as part of the :mod:`ll` package.

For Windows a binary distribution is provided. To install it, double click it
and follow the instructions.

``setuptools`` is supported for installation, so if you have ``setuptools``
installed the package will be installed as an egg.

If you have difficulties installing this software, send a problem report
to Walter Dörwald (walter@livinglogic.de).
