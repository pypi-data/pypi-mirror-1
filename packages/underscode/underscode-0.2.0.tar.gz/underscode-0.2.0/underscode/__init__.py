r"""
Encodes Unicode strings into Python identifier-like strings.

(Underscode home page: http://underscode.selidor.net/)

An Underscode-encoded (henceforth *underscoded*) string can be used as
a Python identifier, so it consists of lower and upper-case letters
from *a* to *z*, decimal digits from *0* to *9*, and the underscore
character *_*.  Moreover, those strings can not be empty, start with a
number, or match one of the Python keywords.  For more information on
Python identifiers, see the *Lexical Analysis* section of the `Python
Reference Manual`_.

.. _Python Reference Manual:
   http://docs.python.org/ref/identifiers.html

The Underscode encoding avoids invalid characters by using escape
sequences which begin with *_* (the underscore character, hence the
name of the encoding).  The escaping is similar to that of Unicode
strings in Python, i.e. Underscode encodes Unicode code points:

* ``_xNN`` escapes a character < 2^8.
* ``_uNNNN`` escapes a character < 2^16.
* ``_UNNNNNNNN`` escapes a character < 2^32.

Where *N* can be any lower or upper-case hexadecimal digit.  However,
``__`` escapes *the space character* instead of the underscore itself,
since spaces are expected to happen much more frequently than
underscores in strings which *need* encoding.  In addition, a decimal
digit can be directly escaped to ease encoding strings beginning with
numbers.  Thus ``_0`` escapes ``0`` itself.

To make encoding Python keywords easy and to allow encoding the empty
string, *all underscoded strings end with an underscore*, which is
only used as a marker.  This makes identifiers coming from underscoded
strings very easy to spot.  (In fact, an underscoded string may end
with an *odd number of underscores*, in case it encodes a string with
trailing spaces.)

Examples
--------

* ``_`` is the empty string.
* ``foo_`` is the string u'foo'.
* ``class_`` is the string u'class'.

* ``foo__bar_`` is the string u'foo bar'.
* ``foo_x20bar_`` is the string u'foo bar', too.
* ``foo_x2fbar_`` is the string u'foo/bar'.
* ``foo_u002fbar_`` is the string u'foo/bar', too.

* ``_42_`` is the string u'42'.
* ``_2006_01_06_`` is the string u'20060106'.

* ``_xc9rase__una__vez_u2026_`` is the string
  u'\xc9rase una vez\u2026' (Once upon a time...).

* ``__init__`` is not a valid underscoded string.
* ``__init___`` is the string u' init '.
* ``_x5f_x5finit_x5f_x5f_`` is the string u'__init__'

Please note that all the previous underscoded strings are valid Python
identifiers (you can check it by yourself!).

Canonical encoding
------------------

Since an original string can be underscoded in several ways, a
*canonical encoding* is desirable to make the encoding predictable.
All encoded strings created by this package meet the following rules:

* A space character (ASCII 32, 0x20) occurring anywhere in the
  original string is encoded as ``__``.

* A number ``N`` occurring at the beginning of the original string is
  encoded as ``_N``.

* A character not in [a-zA-Z0-9] with a code point <=255 is encoded as
  ``_xNN``, where *NN* is the lower-case hexadecimal value of the
  Unicode code point of the character.

* A character with a code point >=256 and <=65535 is encoded as
  ``_uNNNN``, where *NNNN* is the lower-case hexadecimal value of the
  Unicode code point of the character.

* A character with a code point >=65536 and <=4294967295 is encoded as
  ``_UNNNNNNNN``, where *NNNNNNNN* is the lower-case hexadecimal value
  of the Unicode code point of the character.

* All other characters are not escaped.

From all the possible underscoded versions of an original string, the
one which follows all the previous rules is called the *canonical
underscoded version* of the original string.
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


# Imported and exported objects
# =============================

from underscode.exceptions import *
from underscode.core import *

__all__ = [
    # * Exceptions.
    'InvalidChar', 'EndOfInput',
    # * Basic encoding and decoding.
    'is_underscode_encoded',
    'UnderscodeEncoder', 'underscode_encode',
    'UnderscodeDecoder', 'underscode_decode', ]
"""Names of the objects that this package exports."""


# Main part
# =========

def _test():
    """Run ``doctest`` on this module."""
    import doctest
    doctest.testmod()

if __name__ == '__main__':
    _test()
