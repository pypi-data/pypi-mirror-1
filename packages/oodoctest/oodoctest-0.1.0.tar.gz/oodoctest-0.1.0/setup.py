#! /usr/bin/env python

# This is an installation script for oodoctest.  Run it with
# './setup.py install', or
# './setup.py --help' for more options

from distutils.core import setup

setup(name='oodoctest',
      version='0.1.0',
      author='Olivier Grisel',
      author_email='olivier.grisel@ensta.org',
      url='https://gna.org/projects/oodoctest/',
      download_url='http://download.gna.org/oodoctest/',
      description='Doctest extractor for OpenOffice.org documents',
      long_description="""\
oodoctest extracts and runs code samples found in an OpenOffice.org document to
test their validity using the standard python doctest machinery. The goal is
to make it easy to write runnable python documentation with OpenOffice.org.

This script can be both used a command line tool (oodoctest --help) or as the
provider of the OODocFileTest class to integrate OO documents as part of
doctest/unittest suite.""",
      license='GNU GPL v2',
      py_modules=['oodoctest'],
      scripts=['oodoctest'],
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Software Development :: Quality Assurance',
          'Topic :: Software Development :: Testing ',
          ],
      )
