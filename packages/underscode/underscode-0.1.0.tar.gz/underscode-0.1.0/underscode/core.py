"""
Core classes and functions for Underscode encoding and decoding.

.. Note::

   You can find a Graphviz_ DOT description of the finite state
   machine (FSM) recognising (and decoding) underscoded strings in the
   ``underscode.dot`` file in the documentation directory of the
   Underscode source distribution.  For a fast look at the FSM, issue
   the command ``dotty underscode.dot``.  The meaning of output
   actions are described in comments in the DOT file itself.

   .. _Graphviz: http://www.graphviz.org/
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

import re
import string

from underscode.exceptions import InvalidChar, EndOfInput

_numeric_rxs = {
    'dec': '[0-9]',
    'hex': '[0-9a-fA-F]', }

_escaped_rx = '_|%(dec)s|x%(hex)s{2}|u%(hex)s{4}|U%(hex)s{8}' % _numeric_rxs

_main_rxs = {
    'alpha': '[a-zA-Z]',
    'alphanum': '[a-zA-Z0-9]',

    'escaped': '(?:%s)' % _escaped_rx, }

_encoded_rx = (
    '^(?:(?:%(alpha)s|_%(escaped)s)(?:%(alphanum)s|_%(escaped)s)*_|_)$'
    % _main_rxs )

_encoded_re = re.compile(_encoded_rx)

def is_underscode_encoded(encoded):
    """
    Return true if the `encoded` string is underscoded.

    >>> is_underscode_encoded('foo_x2fbar_')
    True
    >>> is_underscode_encoded('__foo__')
    False
    """
    # Simple optimization (20% to 50% speedup) to avoid matching
    # against the regular expression in obvious cases.
    if not encoded or encoded[-1] != '_':
        return False
    return _encoded_re.match(encoded) is not None


# Decoding
# ========

class UnderscodeDecoder(object):

    """
    Character-by-character decoder of underscoded strings.

    Instances of this class can be used to iterate over the *decoded*
    characters of an underscoded string.  This string is stored in the
    `self.encoded` instance variable.

    Each time the `self.next()` method is called, a new Unicode
    character is decoded and returned, and `self.offset` is left
    pointing to the offset in `self.encoded` where the next encoded
    character starts.

    >>> decoder = UnderscodeDecoder('foo_x2fbar_')
    >>> for c in decoder:
    ...   print repr(c), decoder.offset
    u'f' 1
    u'o' 2
    u'o' 3
    u'/' 7
    u'b' 8
    u'a' 9
    u'r' 10
    >>> decoder.next()
    Traceback (most recent call last):
      ...
    StopIteration

    If an error occurs, a `ValueError` is raised and the state of the
    decoder is not changed:

    >>> decoder = UnderscodeDecoder('a/b')
    >>> decoder.next(), decoder.offset
    (u'a', 1)
    >>> decoder.next(), decoder.offset
    Traceback (most recent call last):
      ...
    InvalidChar: Invalid character '/' at offset 1; expected [_a-zA-Z0-9]: 'a/b'.
    >>> decoder.offset, decoder.encoded[decoder.offset:]
    (1, '/b')

    The encoded string can also be extended by appending a new string,
    and the decoding continues after the last successfully decoded
    character, even when the end marker has already been reached:

    >>> decoder = UnderscodeDecoder('U_x')
    >>> decoder.next()
    u'U'
    >>> decoder.next()
    Traceback (most recent call last):
       ...
    EndOfInput: Incomplete encoded character '_x' at offset 1: 'U_x'.
    >>> decoder.append('2fV_')
    >>> decoder.next()
    u'/'
    >>> decoder.next()
    u'V'
    >>> decoder.next()
    Traceback (most recent call last):
      ...
    StopIteration
    >>> decoder.append('x2fW_')
    >>> decoder.next()
    u'/'
    >>> decoder.next()
    u'W'
    >>> decoder.append('TAIL')
    >>> decoder.next()
    Traceback (most recent call last):
       ...
    InvalidChar: Invalid character 'T' at offset 12; expected [_0-9xuU]: 'U_x2fV_x2fW_TAIL'.
    """

    # Using frozen sets is as fast as using dictionaries, somehow
    # faster than using mutable sets, plain strings, and compiled
    # regular expressions, and twice as fast as using non-compiled
    # regular expressions.
    _alpha = frozenset(string.ascii_letters)
    """Set of alphabetic characters (lower and upper-case)."""
    _alphanum = frozenset(string.ascii_letters + string.digits)
    """Set of alphanumeric characters (lower and upper-case)."""
    _digits = frozenset(string.digits)
    """Set of decimal numeric characters."""
    _hexdigits = frozenset(string.hexdigits)
    """Set of hexadecimal numeric characters (lower and upper-case)."""

    _initial_state = 0
    """The initial state of the finite state machine."""
    _final_states = frozenset([2])
    """The set of final states of the finite state machine."""

    def __init__(self, encoded):
        self.encoded = str(encoded)
        """The encoded string."""
        self.offset = 0
        """
        The offset of the encoded string where decoding will start.

        This is the offset of the input character following the part
        of the input string used to successfuly decode the previous
        characters, or 0 if no successful decoding has been done yet.
        """
        self._state = self._initial_state
        """The current state of the finite state machine."""

    def __repr__(self):
        return ( "<%s of %r at offset %d>"
                 % (self.__class__.__name__, self.encoded, self.offset) )

    def __iter__(self):
        return self

    def _get_next_state(self, state, offset, partchar):
        """
        Get next state information for a given state and input.

        The transition depends on the given `state` and the input
        character located at the given `offset` in the encoded input
        string.  The value of a (maybe) partially decoded character is
        given as `partchar`.

        The return value is a tuple consisting of the next state, the
        decoded output Unicode character, and the value of the
        partially decoded character.  If no character is fully
        decoded, the second value is ``None``.  If the transition does
        not affect the partially decoded character, `partchar` is
        returned as is.

        An `InvalidChar` exception is raised if there is no transition
        for the given state and input character.
        """
        inchar = self.encoded[offset]

        if state == 0:
            if inchar == '_':
                partchar = 0  # start of escape sequence (maybe)
                (state, outchar) = (2, None)
            elif inchar in self._alpha:
                (state, outchar) = (1, unicode(inchar))
            else:
                raise InvalidChar(self.encoded, offset, '[_a-zA-Z]')

        elif state == 1:
            if inchar == '_':
                partchar = 0  # start of escape sequence
                (state, outchar) = (2, None)
            elif inchar in self._alphanum:
                (state, outchar) = (1, unicode(inchar))
            else:
                raise InvalidChar(self.encoded, offset, '[_a-zA-Z0-9]')

        elif state == 2:
            if inchar == '_':
                (state, outchar) = (1, u'_')  # end of escape sequence
            elif inchar in self._digits:
                (state, outchar) = (1, unicode(inchar))  # end of esc. seq.
            elif inchar == 'x':
                (state, outchar) = (0xf2, None)
            elif inchar == 'u':
                (state, outchar) = (0xf4, None)
            elif inchar == 'U':
                (state, outchar) = (0xf8, None)
            else:
                raise InvalidChar(self.encoded, offset, '[_0-9xuU]')

        elif 0xf1 <= state <= 0xf8:
            if inchar in self._hexdigits:
                partchar = (partchar << 4) | int(inchar, 16)
                if state == 0xf1:
                    # end of escape sequence
                    (state, outchar) = (1, unichr(partchar))
                else:
                    (state, outchar) = (state - 1, None)
            else:
                raise InvalidChar(self.encoded, offset, '[0-9a-fA-F]')

        else:
            raise AssertionError(
                "Decoding the input string ``%s`` "
                "lead to the unknown state %d."
                % (repr(self.encoded[:offset])[1:-1], state) )

        return (state, outchar, partchar)

    def next(self):
        """
        Get a decoded character from the encoded string.

        Each time this method gets called, it returns a Unicode
        character decoded from the encoded string, until it hits the
        end of the string or an invalid encoding sequence.  In the
        last case, a `ValueError` is raised and the state of the
        decoder is not changed.

        If the input string had already been completely decoded, an
        `StopIteration` is raised.
        """
        # The state of the decoder will only be updated when we can
        # return a decoded character, so we work with local variables.
        state = self._state
        outchar = None  # the decoded character
        partchar = 0  # the code of the character being decoded

        # Look for a character to return, but not beyond the end of
        # the encoded string.
        for offset in xrange(self.offset, len(self.encoded)):
            (state, outchar, partchar) = (
                self._get_next_state(state, offset, partchar) )

            if outchar:
                # A complete character was decoded, we are done.
                self.offset = offset + 1
                self._state = state
                return outchar

        # If the encoded string was exhausted and no character was
        # decoded, then the next state should be a final one.  Please
        # note that the state is not updated, since the end of the
        # decoded string is not a meaningful character.
        if state not in self._final_states:
            raise EndOfInput(self.encoded, self.offset)
        raise StopIteration

    def append(self, encoded):
        """
        Append a new `encoded` string to the one being decoded.

        This method allows the user to dynamically extend the encoded
        string with new input characters.  After appending, decoding
        continues where it was before appending.

        This operation is always successful, even if the decoding has
        raised an exception or hit the end marker.  Of course, further
        decoding will fail if the newly constructed encoded string is
        not valid.

        Please note that the whole new encoded string is stored in the
        decoder, so memory requirements grow with the length of the
        encoded string.
        """
        # Since the offset is only placed after a successfully decoded
        # character, no further actions are needed.
        self.encoded += encoded

def underscode_decode(encoded):
    """
    Decode a string using Underscode.

    The `encoded` argument is converted to a string first.  The
    function returns the resulting decoded Unicode string.  If the
    `encoded` string is invalid, a `ValueError` describing the problem
    is raised.

    >>> underscode_decode('foo_x2fbar_')
    u'foo/bar'
    >>> underscode_decode('__foo__')
    Traceback (most recent call last):
      ...
    EndOfInput: Unexpected end of input while decoding: '__foo__'.
    """
    # Using a generator expression is just as fast as using a list
    # comprehension, and maybe a little bit less memory-consuming.
    return u''.join(outchar for outchar in UnderscodeDecoder(encoded))


# Encoding
# ========

class UnderscodeEncoder(object):

    """
    Character-by-character Underscode encoder of Unicode strings.

    Instances of this class can be used to iterate over the *encoded*
    Underscode representations of a Unicode string.  This string is
    stored in the `self.decoded` instance variable.

    Each time the `self.next()` method is called, a character is
    encoded into a string and returned, and `self.offset` is left
    pointing to the offset in `self.decoded` of the next character to
    be encoded.  When no more characters are left to be encoded, the
    end marker is returned and `self.finished` becomes true.

    >>> encoder = UnderscodeEncoder(u'foo/bar')
    >>> encoder.finished
    False
    >>> for c in encoder:
    ...   print repr(c), encoder.offset
    'f' 1
    'o' 2
    'o' 3
    '_x2f' 4
    'b' 5
    'a' 6
    'r' 7
    '_' 7
    >>> encoder.finished
    True
    >>> encoder.next()
    Traceback (most recent call last):
      ...
    StopIteration

    The decoded string can also be extended by appending a new Unicode
    string, and the encoding continues after the last encoded
    character.  However, appending is not allowed once encoding has
    been finished.

    >>> encoder = UnderscodeEncoder(u'foo')
    >>> encoder.next()
    'f'
    >>> encoder.next()
    'o'
    >>> encoder.append(u'/bar')
    >>> encoder.next()
    'o'
    >>> encoder.next()
    '_x2f'
    >>> encoder.next()
    'b'
    >>> encoder.next()
    'a'
    >>> encoder.next()
    'r'
    >>> encoder.next()
    '_'
    >>> encoder.append(u'/baz')
    Traceback (most recent call last):
      ...
    ValueError: Can not extend completely encoded strings.
    """

    # Using frozen sets is as fast as using dictionaries, somehow
    # faster than using mutable sets, plain strings, and compiled
    # regular expressions, and twice as fast as using non-compiled
    # regular expressions.
    _alphanum = frozenset(unicode(string.ascii_letters + string.digits))
    """Set of alphanumeric Unicode characters (lower and upper-case)."""
    _digits = frozenset(unicode(string.digits))
    """Set of decimal numeric Unicode characters."""

    def __init__(self, decoded):
        self.decoded = unicode(decoded)
        """The Unicode string to be encoded."""
        self.offset = 0
        """The offset of the decoded string where encoding will start."""
        self.finished = False
        """Has the decoded string been completely encoded?"""

    def __repr__(self):
        class_name, finish_info = self.__class__.__name__, ""
        if self.finished:
            finish_info = " (finished)"
        return ( "<%s of %r at offset %d%s>"
                 % (class_name, self.decoded, self.offset, finish_info) )

    def __iter__(self):
        return self

    def _encode_next(self):
        """
        Get the encoded representation of the next input character.

        When the current offset is at the end of the input string, the
        end marker is returned.
        """
        offset = self.offset
        inchar = self.decoded[offset:offset+1]

        # If the end of the string was hit, return the end marker.
        if not inchar:
            return '_'

        # Special case: a digit starting a string must be encoded.
        if offset == 0 and inchar in self._digits:
            return '_%c' % str(inchar)

        # Encode underscores, but not ASCII-alphanumeric characters.
        if inchar == u'_':
            return '__'
        if inchar in self._alphanum:
            return str(inchar)

        # Encode the other non-ASCII-alphanumeric characters.
        cpoint = ord(inchar)
        if cpoint <= 0xff:
            outfmt = '_x%02x'
        elif cpoint <= 0xffff:
            outfmt = '_u%04x'
        else:
            outfmt = '_U%08x'
        return outfmt % cpoint

    def next(self):
        """
        Get an encoded character from the decoded string.

        Each time this method gets called, it returns the Underscode
        string representation of the next Unicode character in the
        decoded string, until it hits the end of the string.  In the
        last case, the end marker is returned and `self.finished`
        becomes true.

        If the input string had already been completely encoded, an
        `StopIteration` is raised.
        """
        if self.finished:
            raise StopIteration

        # Not yet finished, encode and return the next character.
        outchar = self._encode_next()
        if self.offset == len(self.decoded):
            self.finished = True  # finished, don't increment offset
        else:
            self.offset += 1
        return outchar  # may be the end marker

    def append(self, decoded):
        """
        Append a new `decoded` Unicode string to the one being encoded.

        This method allows the user to dynamically extend the decoded
        string with new input characters.  After appending, encoding
        continues where it was before appending.

        Appending to completely encoded strings is not allowed, since
        the resulting encoded string may not be a valid underscoded
        string.  If that is attempted, a `ValueError` is raised.

        Please note that the whole new decoded string is stored in the
        encoder, so memory requirements grow with the length of the
        decoded string.
        """
        if self.finished:
            raise ValueError("Can not extend completely encoded strings.")
        self.decoded += decoded

def underscode_encode(decoded):
    """
    Encode a Unicode string using Underscode.

    The `decoded` argument is converted to a Unicode string first.
    The function returns the resulting encoded string.

    >>> underscode_encode(u'foo/bar')
    'foo_x2fbar_'
    >>> underscode_encode(20060831)
    '_20060831_'
    """
    # Using a generator expression is just as fast as using a list
    # comprehension, and maybe a little bit less memory-consuming.
    return ''.join(outchar for outchar in UnderscodeEncoder(decoded))


# Main part
# =========

def _test():
    """Run ``doctest`` on this module."""
    import doctest
    doctest.testmod()

if __name__ == '__main__':
    _test()
