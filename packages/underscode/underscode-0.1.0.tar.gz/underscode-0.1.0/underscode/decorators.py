"""
Utility decorators based on the Underscode encoding.

These decorators apply to *default methods* and *access methods*.
*Access methods* should (at least) accept some kind of identifier in
the form of a Unicode string, while *default methods* should (again at
least) accept some kind of identifier in the form of a normal string.
The decorators take care of providing decoded Unicode strings or
encoded Underscode strings as convenient to them.

The best way to see this is by example.  Let us create a subclass of
``dict`` which allows to access items with a string or Unicode key as
instance attributes.  The `proxy_method` decorator tailors a method so
that giving it an underscoded name makes it call the *access method*
(e.g. ``dict.__getitem__()``) with the decoded name; giving it a
non-underscoded name makes it call the *default method* (which is the
decorated method, e.g. ``__getattr__()``), without touching the name.
So, in the example, when an attribute with an underscoded name is
accessed, it is the corresponding item that will be accessed instead.

>>> class AttributedDict(dict):
...   @proxy_method(dict.__getitem__)
...   def __getattr__(self, name):
...     return super(AttributedDict, self).__getattr__(name)
...   @proxy_method(dict.__setitem__)
...   def __setattr__(self, name, value):
...     super(AttributedDict, self).__setattr__(name, value)
...   @proxy_method(dict.__delitem__)
...   def __delattr__(self, name):
...     super(AttributedDict, self).__delattr__(name)
... 
>>> d = AttributedDict()
>>> d
{}
>>> d.foo = 1
>>> d.foo
1
>>> d['foo'], d.bar_ = 42, 43
>>> d.foo_, d['bar']
(42, 43)
>>> d == {'foo': 42, u'bar': 43}
True
>>> del d['foo'], d.bar_
>>> del d.foo_
Traceback (most recent call last):
  ...
KeyError: u'foo'
>>> d
{}

You can see that normal (non-underscoded) attributes work as usual.
Also note that keys like *'foo'* directly set with the default method
(as items) retain their type, while keys like *u'bar'* set with the
access method (as underscoded attributes) are always Unicode.  This is
because decoding the underscoded attribute name always results in a
Unicode string.

Also notice that deleting the non-existing underscoded attribute
*'foo_'* raised a ``KeyError`` instead of an ``AttributeError``.
Since the default method acts in this call as a proxy to the access
method, the exceptions raised are those of the last one.

For interactive usage it is nice to have attribute name completion.
There are two ways to achieve this: using the instance ``__members__``
or using its ``__dict__``.  This module provides decorators for both.

In the following example, using the ``__members__`` approach allows
completion but still makes *all* accesses to underscoded attribute
names go through the access methods.  To make access methods keep the
list of ``__members__`` up to date, the `members_setter` and
`members_deleter` decorators are used on them.  Remember to initalise
the ``__members__`` list!

>>> class AttributedDict(dict):
...   def __init__(self, *args, **kwargs):
...     self.__dict__['__members__'] = []
...     super(AttributedDict, self).__init__(*args, **kwargs)
...   __setitem__ = members_setter(dict.__setitem__)
...   __delitem__ = members_deleter(dict.__delitem__)
...   @proxy_method(dict.__getitem__)
...   def __getattr__(self, name):
...     return super(AttributedDict, self).__getattr__(name)
...   @proxy_method(__setitem__)
...   def __setattr__(self, name, value):
...     super(AttributedDict, self).__setattr__(name, value)
...   @proxy_method(__delitem__)
...   def __delattr__(self, name):
...     super(AttributedDict, self).__delattr__(name)
... 
>>> d = AttributedDict()
>>> d.__members__
[]
>>> d['foo'], d.bar_, d._2006_08_29_ = 42, 43, 44
>>> sorted(d.__members__)
['_20060829_', 'bar_', 'foo_']
>>> d._2006_08_29_
44
>>> del d.foo_
>>> sorted(d.__members__)
['_20060829_', 'bar_']

Both the decorator and function call syntaxes are used here.  Note
that there is no ``members_getter`` decorator since no *values* are
stored in ``__members__``.  Also note that `proxy_method` is using the
new versions of ``__setitem__()`` and ``__delitem__()`` defined in
this class as access methods, so that setting and deleting underscoded
attribute names keeps ``__members__`` up to date.

The last statememts show something that also applies to ``__dict__``
completion: the stored underscoded names are *always canonically
encoded*.  So, one can get ``_200608`` completed, but ``_2006_08``
does not work.  However, both ``_20060829_`` and ``_2006_08_29_`` (and
other variants) can be used to refer to the attribute with the same
decoded name.

Using the ``__dict__`` decorators (`dict_getter`, `dict_setter` and
`dict_deleter`) is very similar.  Using `dict_getter` is optional (as
explained below).  The basic difference with the previous approach is
that *values are cached* in the instance ``__dict__``.

>>> class AttributedDict(dict):
...   __getitem__ = dict_getter(dict.__getitem__)
...   __setitem__ = dict_setter(dict.__setitem__)
...   __delitem__ = dict_deleter(dict.__delitem__)
...   @proxy_method(__getitem__)
...   def __getattr__(self, name):
...     return super(AttributedDict, self).__getattr__(name)
...   @proxy_method(__setitem__)
...   def __setattr__(self, name, value):
...     super(AttributedDict, self).__setattr__(name, value)
...   @proxy_method(__delitem__)
...   def __delattr__(self, name):
...     super(AttributedDict, self).__delattr__(name)
... 
>>> d = AttributedDict()
>>> d.__dict__
{}
>>> d['foo'], d.bar_ = 42, 43
>>> d.__dict__ == {'foo_': 42, 'bar_': 43}
True
>>> del d.foo_
>>> d.__dict__ == {'bar_': 43}
True
>>> # Don't try this at home! ;)
>>> d.__dict__['bar_'] = 430
>>> d.bar_, d['bar']
(430, 430)
>>> d
{u'bar': 43}

As you can see from the last statements, values are cached in
``__dict__`` when using `dict_setter`.  The decorated ``__getitem__``
uses ``__dict__`` as a cache, and so accesses to ``bar_`` do not reach
the original ``dict.__getitem__()``.  So, using `dict_getter` is
useful when calling the *access method* is very costly.
"""

__copyright__ = [
    (u"Ivan Vilata i Balaguer", "ivan@selidor.net", [2006, 2007]), ]
"""List of copyright holders of this file."""

__license__ = u"""\
This file is part of the Underscode package.

The Underscode package is free software; you can redistribute it
and/or modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation, either
version 3 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library.  If not, see
<http://www.gnu.org/licenses/>.
"""
"""Statement of license for this file."""

__docformat__ = 'reStructuredText'
"""The format of documentation strings in this module."""


# Imports, variables and functions
# ================================

from underscode import (
    is_underscode_encoded, underscode_encode, underscode_decode )


# Underscoded proxied access decorators
# =====================================
#
# .. Warning::
#    When requesting a non-existing attribute, Python complains about
#    the absence of ``__getattr__`` instead.  Since getting existing
#    attributes works, the former looks like a Python bug.

def proxy_method(access_method):
    """
    Derive calls to `access_method` on underscoded first argument.

    This returns a decorator which makes the decorated method (the
    *default method*) call the given *access method* instead whenever
    an underscoded string is given as a first argument.  In this case,
    the string is decoded.  Otherwise, the default method is used with
    the string as is.

    The *access method* must at least accept a Unicode string as a
    first argument, and the *default method* must at least accept a
    string as a first argument.
    """
    accmethod_name = access_method.__name__
    def decorator(default_method):
        """Decorate `default_method` to derive calls to ``%s()``."""
        defmethod_name = default_method.__name__
        def newmethod(self, name, *args, **kwargs):
            """Underscoded proxy from *default* to *access* methods."""
            if not is_underscode_encoded(name):
                return default_method(self, name, *args, **kwargs)
            decoded_name = underscode_decode(name)
            return access_method(self, decoded_name, *args, **kwargs)
        newmethod.__name__ = defmethod_name
        newmethod.__doc__ = default_method.__doc__
        return newmethod
    decorator.__doc__ %= accmethod_name
    return decorator


# Decorators affecting ``__members__``
# ====================================
#
# There is no default ``members_getter()`` decorator since no actual
# data can be retrieved from ``__members__``.

def members_setter(access_method):
    """
    Decorate method to add an underscoded name to ``__members__``.

    The decorated method `access_method` must at least accept a
    Unicode string as a first argument and an arbitrary value as a
    second one.  When the call to the method succeeds, the canonically
    underscoded version of the string is added to the instance
    ``__members__``.

    When using this decorator, please remember to set ``__members__``
    to an empty list early on instance initialisation::

        def __init__(self, ...):
            ...
            self.__dict__['__members__'] = []
            ...

    """
    def newmethod(self, name, value, *args, **kwargs):
        """Call and add underscoded `name` to ``__members__``."""
        access_method(self, name, value, *args, **kwargs)
        encoded_name = underscode_encode(name)
        members = self.__members__
        if encoded_name not in members:
            members.insert(0, encoded_name)
    newmethod.__name__ = access_method.__name__
    newmethod.__doc__ = access_method.__doc__
    return newmethod

def members_deleter(access_method):
    """
    Decorate method to delete an underscoded name from ``__members__``.

    The decorated method `access_method` must at least accept a
    Unicode string as a first argument.  When the call to the method
    succeeds, the canonically underscoded version of the string is
    deleted from the instance ``__members__``.

    When using this decorator, please remember to set ``__members__``
    to an empty list early on instance initialisation::

        def __init__(self, ...):
            ...
            self.__dict__['__members__'] = []
            ...

    """
    def newmethod(self, name, *args, **kwargs):
        """Call and delete underscoded `name` from ``__members__``."""
        access_method(self, name, *args, **kwargs)
        encoded_name = underscode_encode(name)
        members = self.__members__
        members.remove(encoded_name)
    newmethod.__name__ = access_method.__name__
    newmethod.__doc__ = access_method.__doc__
    return newmethod


# Decorators affecting ``__dict__``
# =================================

def dict_getter(access_method):
    """
    Decorate method to look up underscoded keys in ``__dict__``.

    The decorated method `access_method` must at least accept a
    Unicode string as a first argument.  If the canonically
    underscoded string is present in the instance ``__dict__``, its
    value is retrieved from there.  Else, the access method is tried.

    Use this decorator to turn ``__dict__`` into a cache of values
    with underscoded keys, when calling the access method costs more
    than encoding the string.
    """
    def newmethod(self, name, *args, **kwargs):
        """Get underscoded `name` from ``__dict__``, or call."""
        encoded_name = underscode_encode(name)
        try:
            return self.__dict__[encoded_name]
        except KeyError:
            return access_method(self, name, *args, **kwargs)
    newmethod.__name__ = access_method.__name__
    newmethod.__doc__ = access_method.__doc__
    return newmethod

def dict_setter(access_method):
    """
    Decorate method to add an underscoded key to ``__dict__``.

    The decorated method `access_method` must at least accept a
    Unicode string as a first argument and an arbitrary value as a
    second one.  When the call to the method succeeds, the canonically
    underscoded version of the string is added to the instance
    ``__dict__`` with the given value.
    """
    def newmethod(self, name, value, *args, **kwargs):
        """Call and add underscoded `name` to ``__dict__``."""
        access_method(self, name, value, *args, **kwargs)
        encoded_name = underscode_encode(name)
        self.__dict__[encoded_name] = value
    newmethod.__name__ = access_method.__name__
    newmethod.__doc__ = access_method.__doc__
    return newmethod

def dict_deleter(access_method):
    """
    Decorate method to delete an underscoded key from ``__dict__``.

    The decorated method `access_method` must at least accept a
    Unicode string as a first argument.  When the call to the method
    succeeds, the canonically underscoded version of the string is
    deleted from the instance ``__dict__``.
    """
    def newmethod(self, name, *args, **kwargs):
        """Call and delete underscoded `name` from ``__dict__``."""
        access_method(self, name, *args, **kwargs)
        encoded_name = underscode_encode(name)
        del self.__dict__[encoded_name]
    newmethod.__name__ = access_method.__name__
    newmethod.__doc__ = access_method.__doc__
    return newmethod


# Main part
# =========

def _test():
    """Run ``doctest`` on this module."""
    import doctest
    doctest.testmod()

if __name__ == '__main__':
    _test()
