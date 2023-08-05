#!/usr/bin/env python

import sys
from distutils.core import setup

if sys.version_info < (2, 4):
    print >> sys.stderr, ".. ERROR:: Underscode requires Python 2.4 or newer."
    sys.exit(1)

dist_classifiers = """
Development Status :: 3 - Alpha
Environment :: Console
Intended Audience :: Developers
License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)
Natural Language :: English
Operating System :: OS Independent
Programming Language :: Python
Topic :: Software Development :: Libraries :: Python Modules
"""
dist_classifiers = [cl for cl in dist_classifiers.split('\n') if cl]

setup(
    name='underscode',
    description="Underscode -- A Python identifier-like encoding",
    long_description="""\
Underscode is an encoding which is capable of representing
*any* Unicode string as a valid (and quite similar) Python
identifier.  The way Unicode strings are encoded minimises
the chances of clashing with other existing names, while not
obscuring the resulting string too much.

Some method decorators are provided which allow arbitrary
objects to be accessed as normal instance attributes, with
optional tab-completion support for interactive usage.  The
standard Python codec API is also supported.""",  # wrap at 60 columns
    keywords='encoding, identifier, codec, Unicode',
    classifiers=dist_classifiers,

    author="Ivan Vilata i Balaguer",
    author_email='ivan@selidor.net',
    license='GNU Lesser General Public License (LGPL)',

    url='http://underscode.selidor.net/',
    version='0.2.0',
    platforms='Any',

    packages=['underscode'], )
