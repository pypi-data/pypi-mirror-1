#!/bin/env python
# -*- coding: iso-8859-15 -*-
"""oodoctest - a utility to run python code samples from an OOo document

By Olivier Grisel <olivier.grisel@ensta.org>

oodoctest extracts and run code samples found in an OpenOffice.org document to
test their validity using the standard python doctest machinery. The goal is
to make it easy to write runnable python documentation with OpenOffice.org.

This script can be both used a command line tool (oodoctest.py --help) or as the
provider of the OODocFileTest class to integration OO documents as part of
unittest suite.

OpenOffice.org is not required to run oodoctest.
"""

__copyright__ = """
(C) Copyright 2005 Olivier Grisel <olivier.grisel@ensta.org>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License version 2 as published
by the Free Software Foundation.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
02111-1307, USA.
"""

__version__ = "0.1.0"
__author__ = "Olivier Grisel <olivier.grisel@ensta.org>"

__TODO__ = """\
- add EasyInstall support
- add support for the OpenDocument format (00 2.0 and 1.1.5)
- find a way to plug it in OOo as a macro to inline test the document
"""

import os
import sys
import zipfile
import doctest
import unittest
from copy import copy
from doctest import DocFileCase, DocTestParser

try:
    import lxml.etree as ElementTree
except ImportError:
    try:
        import cElementTree as ElementTree
    except ImportError:
        from elementtree import ElementTree

#
# OpenOffice.org XML namespace
#
OO_base = "http://openoffice.org/2000" # base URI fot OO namespace
OO_office = "%s/office" % OO_base # office URI
OO_body = "{%s}body" % OO_office # Bodyof the document
OO_text = "%s/text" % OO_base # text URI
OO_p = "{%s}p" % OO_text # Paragraph
OO_s = "{%s}s" % OO_text # Whitespaces sequence
OO_c = "{%s}c" % OO_text # Counter
OO_h = "{%s}h" % OO_text # Header
OO_level = "{%s}level" % OO_text # Header level

ns_xlink = "http://www.w3.org/1999/xlink"

#
# API
#

def _extract_text(element, text=''):
    r"""Recursively extract text from an tree structured document

    >>> e = ElementTree.XML('''\
    ... <?xml version="1.0" encoding="UTF-8"?>
    ... <office:document-content
    ...   xmlns:office="%(OO_office)s"
    ...   xmlns:text="%(OO_text)s"
    ...   xmlns:xlink="%(ns_xlink)s"
    ...   >\
    ... <office:body>\
    ... <text:p>This is a <text:a xlink:href="http://example.org/">\
    ... paragraph</text:a></text:p>\
    ... <text:p>3 spaces<text:s text:c="3"/>endSpaces</text:p>\
    ... </office:body>\
    ... </office:document-content>
    ... ''' % globals())
    >>> print _extract_text(e)
    This is a paragraph
    3 spaces   endSpaces
    <BLANKLINE>
    """
    for child in element.getchildren():
        if child.text:
            text += child.text
        if child.tag == OO_s:
            # Expanding spacer markup into white spaces and appending the tail
            counter = child.get(OO_c)
            if counter:
                text += ' '*int(counter)
        # Recursive descent to the children
        text = _extract_text(child, text=text)
        if child.tag == OO_p:
            # Paragraphs have an implicit newline character
            text += '\n'
        if child.tail:
            text += child.tail
    return text

def _read_oo_doc(path, split_level=None):
    """Extract formated text from an OpenOffice.org document

    if split_level is not None, the documents is splited into independant
    strings at each new header of level split_level

    return a list of strings
    """
    oofile = zipfile.ZipFile(path)
    content = oofile.read('content.xml')
    root = ElementTree.fromstring(content)
    body = root.find(OO_body)
    if split_level is None:
        # Do not split the document
        return [_extract_text(body)]
    # Split the document into a list of independant elements
    groups = [ElementTree.Element('oodoctest group')]
    for elem in body.getchildren():
        if elem.tag == OO_h and int(elem.get(OO_level)) == split_level:
            # Create a new group to store the next elements in
            groups.append(ElementTree.Element(elem.text or 'oodoctest group'))
        last_group = groups[-1]
        last_group.append(copy(elem))
    return [_extract_text(group) for group in groups]

def _extract_doctests(path, split_level=None, module_relative=True,
        package=None, globs=None, parser=DocTestParser(), **options):
    """extract doctests from an OO document at 'path'

    return a list of doctests instances
    """
    if globs is None:
        globs = {}

    if package and not module_relative:
        raise ValueError("Package may only be specified for module-"
                         "relative paths.")

    # Relativize the path.
    if module_relative:
        package = doctest._normalize_module(package)
        path = doctest._module_relative_path(package, path)

    # Find the file and extract a formatted utf-8 string
    name = os.path.basename(path)
    docs = _read_oo_doc(path, split_level=split_level)

    # wrap it in a DocFileCase.
    tests = []
    for doc in docs:
        tests.append(parser.get_doctest(doc, globs, name, path, 0))
    return tests

def OODocFileTest(path, module_relative=True, package=None,
                  globs=None, parser=DocTestParser(), **options):
    """Build a DocFileCase out of an OpenOffice document.

    Arguments are similar to those of the doctest.DocFileTest function
    """
    [test] = _extract_doctests(path, split_level=None,
                               module_relative=module_relative,
                               package=package, globs=globs, parser=parser)
    return DocFileCase(test, **options)

def OODocFileSuite(*paths, **kw):
    suite = unittest.TestSuite()

    # We do this here so that _normalize_module is called at the right
    # level.  If it were called in DocFileTest, then this function
    # would be the caller and we might guess the package incorrectly.
    if kw.get('module_relative', True):
        kw['package'] = doctest._normalize_module(kw.get('package'))
    kw2 = kw.copy()
    for key in ('module_relative', 'package', 'globs', 'parser',
            'split_level'):
        if kw2.has_key(key):
            del kw2[key]

    for path in paths:
        for test in _extract_doctests(path, **kw):
            suite.addTest(DocFileCase(test, **kw2))
    return suite

OODocFileSuite.__doc__ = doctest.DocFileSuite.__doc__

def main():
    """Run oodoctest.py as a command line utility
    """
    # Settings from commandline options
    from optparse import OptionParser
    parser = OptionParser()
    parser.set_usage("%prog [options] oofile [oofile2 ...]")
    parser.add_option("-v", "--verbose",
                  action="store_const", const=1, dest="verbosity",
                  help="show extracted doctests and their results",
                  default=0)
    parser.add_option("-s", "--split-level", dest="split_level", type="int",
                      help="split the document into independant tests at"
                           " each new heading at level SPLIT_LEVEL",
                      default=None)
    parser.add_option("-e", "--ellipsis", dest="ellipsis", type="choice",
                      help="enaable ellipsis (default is on)",
                      choices=['on','off'],
                      default='on')
    options, args = parser.parse_args()
    cwd = os.getcwd()
    paths = [os.path.join(cwd, arg) for arg in args]
    if not args:
        print "You should provide an OpenOffice file as argument:"
        parser.print_usage()
        sys.exit(1)
    kw = {
        'split_level': options.split_level,
        'module_relative': False,
        }
    optionflags = 0
    if options.ellipsis is 'on':
        optionflags = optionflags | doctest.ELLIPSIS

    # tests exctraction
    tests = []
    for path in paths:
        tests += _extract_doctests(path, **kw)

    # run!
    runner = doctest.DocTestRunner(optionflags=optionflags)
    for test in tests:
        runner.run(test)
    runner.summarize(verbose=options.verbosity)


if __name__ == '__main__':
    main()
