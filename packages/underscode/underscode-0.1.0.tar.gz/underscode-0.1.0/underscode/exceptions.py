"""Exceptions defined by the Underscode package."""

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


# Exceptions
# ==========

class InvalidChar(ValueError):

    """
    An invalid character was found while decoding an underscoded string.

    >>> invalid_char = InvalidChar('_b1_', 1, '[_0-9xuU]')
    >>> invalid_char.encoded, invalid_char.offset, invalid_char.expected
    ('_b1_', 1, '[_0-9xuU]')
    >>> raise invalid_char
    Traceback (most recent call last):
      ...
    InvalidChar: Invalid character 'b' at offset 1; expected [_0-9xuU]: '_b1_'.
    >>> 
    >>> try:
    ...   raise InvalidChar('_b1_', 1, '[_0-9xuU]')
    ... except ValueError, ve:
    ...   print ve.args
    ... 
    ('b',)
    """

    def __init__(self, encoded, offset, expected):
        ValueError.__init__(self, encoded[offset])

        self.encoded = encoded
        """The whole encoded string."""
        self.offset = offset
        """The offset of the invalid character within the string."""
        self.expected = expected
        """The expected set of characters (e.g. a regular expression)."""

    def __str__(self):
        encoded = self.encoded
        offset = self.offset

        return (
            "Invalid character %r at offset %d; expected %s: %r."
            % (encoded[offset], self.offset, self.expected, self.encoded) )

class EndOfInput(ValueError):

    """
    The end of input was found while decoding an underscoded string.

    >>> end_of_input = EndOfInput('Err_u202', 3)
    >>> end_of_input.encoded, end_of_input.offset
    ('Err_u202', 3)
    >>> raise end_of_input
    Traceback (most recent call last):
      ...
    EndOfInput: Incomplete encoded character '_u202' at offset 3: 'Err_u202'.
    >>> 
    >>> raise EndOfInput('__foo__', 7)
    Traceback (most recent call last):
      ...
    EndOfInput: Unexpected end of input while decoding: '__foo__'.
    >>> 
    >>> try:
    ...   raise EndOfInput('__foo__', 7)
    ... except ValueError, ve:
    ...   print ve.args
    ... 
    ('__foo__',)
    """

    def __init__(self, encoded, offset):
        ValueError.__init__(self, encoded)

        self.encoded = encoded
        """The whole encoded string."""
        self.offset = offset
        """The offset after the last complete character."""

    def __str__(self):
        encoded = self.encoded
        offset = self.offset

        if self.offset < len(encoded):
            return ( "Incomplete encoded character %r at offset %d: %r."
                     % (encoded[offset:], offset, encoded) )
        return "Unexpected end of input while decoding: %r." % encoded


# Main part
# =========

def _test():
    """Run ``doctest`` on this module."""
    import doctest
    doctest.testmod()

if __name__ == '__main__':
    _test()
