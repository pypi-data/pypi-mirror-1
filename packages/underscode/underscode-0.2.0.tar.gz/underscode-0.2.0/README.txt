==============
  Underscode
==============

-------------------------------------
  A Python identifier-like encoding
-------------------------------------

:Author: `Ivan Vilata i Balaguer <ivan@selidor.net>`__
:URL: http://underscode.selidor.net/


About Underscode
================

Underscode_ is an encoding which is capable of representing *any*
Unicode string as a valid (and quite similar) Python identifier.  The
way Unicode strings are encoded minimises the chances of clashing with
other existing names, while not obscuring the resulting string too much.

Some method decorators are provided which allow arbitrary objects to be
accessed as normal instance attributes, with optional tab-completion
support for interactive usage.  The standard Python codec API is also
supported.

Underscode-encoded (or *underscoded*) strings can be quickly spotted
because they end with an *odd* number of underscores, and they contain
escape sequences beginning with an underscore where characters not
allowed in identifiers would be found.  Some examples of underscoded
strings are:

* ``_`` encodes the empty string.
* ``foo_`` encodes ``foo``.
* ``class_`` encodes ``class``.
* ``foo__bar_`` encodes ``foo bar``.
* ``foo_x5fbar_`` encodes ``foo_bar``.
* ``_2006_09_18_``, like ``_20060918_``, encodes ``20060918``.
* ``_x2fbin_x2fls_``, encodes ``/bin/ls``.
* ``The__Knights__Who__Say___u201cNi_x21_u201d_`` encodes the properly
  quoted ``The Knights Who Say “Ni!”``.

As you see, underscoded strings are quite similar to their decoded
counterparts when these are more or less identifier-like, but complex
strings can still be handled.

Underscode is a very basic tool which may have several uses:

* Avoiding clashes between method names and table field names in ORMs.
* Enabling interactive attribute-like completion for children in
  hierarchically arranged structures (DOM trees, filesystems...), with
  full Unicode support.
* As an aid in the generation of RPC stubs for identifiers which are not
  allowed by Python.
* Computing unique IDs for sections in automatically generated XML or
  HTML documents.
* Naming page handlers for web server frameworks like CherryPy.
* ... just use your imagination!

The Underscode package is released under the GNU Lesser General Public
License (LGPL) version 3 or later (see http://www.gnu.org/licenses/).

Underscoded strings as attributes
---------------------------------

Underscode provides a module with decorators that allow you to use plain
attribute access as a flexible way of accessing all kinds of "child
objects" without polluting the normal attribute namespace, and with
optional interactive completion if you wish so.  For instance, you can
make the (string) keys of a dictionary accessible as attributes::

    from underscode.decorators import proxy_method

    class AttributedDict(dict):
        @proxy_method(dict.__getitem__)
        def __getattr__(self, name):
            return super(AttributedDict, self).__getattr__(name)

        @proxy_method(dict.__setitem__)
        def __setattr__(self, name, value):
            super(AttributedDict, self).__setattr__(name, value)

        @proxy_method(dict.__delitem__)
        def __delattr__(self, name):
            super(AttributedDict, self).__delattr__(name)

Then, access to an attribute which looks like an underscoded string gets
the name decoded and used as an argument to ``__getitem__()``:

>>> d = AttributedDict()
>>> d
{}
>>> d.foo = 1
>>> d.foo_ = 42
>>> d.foo_, d['foo'], d.foo
(42, 42, 1)
>>> d
{u'foo': 42}
>>> del d.foo_
>>> d
{}

Adding tab-completion on underscoded attributes to this simple example
is as easy as applying some ready-to-use decorators on the methods used
as arguments to ``proxy_method``.  See the documentation of the
``underscode.decorators`` module for more information and examples.

Python codec API support
------------------------

Since the Underscode package is compliant with the standard Python codec
API, you can use Underscode to encode and decode strings with the usual
``unicode.encode()`` and ``str.decode()`` calls at any time just by
importing the ``underscode.codec`` subpackage (it is not automatically
imported by the main ``underscode`` package):

>>> import underscode.codec
>>> print u'this is \u201ca test\u201d'
this is “a test”
>>> u'this is \u201ca test\u201d'.encode('underscode')
'this__is___u201ca__test_u201d_'
>>> 'this__is___u201ca__test_u201d_'.decode('underscode')
u'this is \u201ca test\u201d'


Getting Underscode
==================

You can download the source code distribution of Underscode from the
Python Package Index at http://pypi.python.org/.  It uses the standard
``setup.py`` method for installation, runs on any platform and has no
additional dependencies but Python version 2.4 or greater.

You may also be interested in following the development of Underscode;
you can get a copy of its development `Bazaar-NG`_ branch with::

    $ bzr get https://bzr.selidor.net/selidor/underscode/trunk underscode


Helping Underscode
==================

There is a discussion group for Underscode at Google Groups:
http://groups.google.com/group/underscode

It would be great to discuss your opinions and feelings on Underscode in
the group, to know how you used it in your project, and to help solving
yours and others problems there!  If you come across a bug or you have
some enhancement proposal, you may use the Trac_ instance available at
http://underscode.selidor.net/


.. _Underscode: http://underscode.selidor.net/
.. _Bazaar-NG: http://bazaar-ng.org/
.. _Trac: http://trac.edgewall.org/


.. Local Variables:
.. mode: rst
.. coding: utf-8
.. fill-column: 72
.. End:
