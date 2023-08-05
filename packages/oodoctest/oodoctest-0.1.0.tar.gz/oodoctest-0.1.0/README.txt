oodoctest - a utility to run python code samples from an OOo document
=====================================================================

By Olivier Grisel <olivier.grisel@ensta.org>

https://gna.org/projects/oodoctest/

Overview
--------

oodoctest extracts and runs code samples found in an OpenOffice.org document to
test their validity using the standard python doctest machinery. The goal is
to make it easy to write runnable python documentation with OpenOffice.org.

This script can be both used a command line tool (oodoctest --help) or as the
provider of the OODocFileTest class to integrate OO documents as part of
doctest/unittest suite.

Have a look at examples/oodoctest_intro.sxi for some quick introductionary
slides.

Requirements:
-------------

- python 2.4
- ElementTree, cElementTree or lxml

OpenOffice.org is not required to run oodoctest.

Installation
------------

Use the traditional distutils based installation script:

$ sudo python setup.py install

Examples
--------

Run the examples:

  $ python oodoctest examples/*


Run the tests:

  $ python test.py

Using oodoctest in a testsuite
------------------------------

oodoctest is a package that provides two functions (OODocFileTest and
OODocFileSuite) to make OpenOffice documents part of a unittest.TestSuite
instance, eg::

  >>> from oodoctest import OODocFileTest
  >>> import unittest
  >>> from doctest import ELLIPSIS as E
  >>> suite = unittest.TestSuite()
  >>> suite.addTest(OODocFileTest('examples/example.sxw', optionflags=E))
  >>> len(list(suite))
  1

Contributing
------------

Please send all feedback, bug reports or patch to <oodoctest-main@gna.org>
or better, use the web interface of the project page at::

https://gna.org/projects/oodoctest/

You can also make your own branch with bzr (http://bazaar-ng.org):

  $ bzr branch http://download.gna.org/oodoctest/oodoctest.og.main/
