"""
Underscode support for the Python codec API.

Standard codec support enables encoding of Unicode strings into
underscoded strings, and decoding of underscoded strings into Unicode
strings, just by importing this module.  Only strict error handling is
supported.

>>> u'foo/bar'.encode('underscode')
'foo_x2fbar_'
>>> 'foo_x2fbar_'.decode('underscode')
u'foo/bar'
>>> unicode('foo_x2fbar_', 'underscode')
u'foo/bar'
>>> 'foo_x2fbar'.decode('underscode')
Traceback (most recent call last):
  ...
EndOfInput: Unexpected end of input while decoding: 'foo_x2fbar'.
>>> 'foo_x2fbar'.decode('underscode', 'ignore')
Traceback (most recent call last):
  ...
UnicodeError: Only strict error handling is supported.

Very limited support for writing and reading underscoded streams is
also provided.  At the present moment, all data needs to be written or
read at once into the stream.  Otherwise, a `UnicodeError` is raised.

>>> from StringIO import StringIO
>>> 
>>> stream = StringIO('foo_x2fbar_')
>>> reader = StreamReader(stream)
>>> reader.read()
u'foo/bar'
>>> reader.read()
Traceback (most recent call last):
  ...
UnicodeError: Only one call to ``decode()`` is supported per stream instance.
>>> 
>>> stream = StringIO()
>>> writer = StreamWriter(stream)
>>> writer.write(u'foo/bar')
>>> stream.getvalue()
'foo_x2fbar_'
>>> writer.write(u'/baz')
Traceback (most recent call last):
  ...
UnicodeError: Only one call to ``encode()`` is supported per stream instance.
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

import sys
import codecs

from underscode.core import underscode_encode, underscode_decode

def one_use_method(codecmethod):
    """
    Ensure that the decorated method is called at most once.

    The decorated encoding or decoding method is called again, a
    `UnicodeError` is raised.  The method sets a ``_used_METHOD_NAME``
    instance variable for that purpose.
    """
    def newmethod(self, input, errors='strict'):
        """Encoding or decoding method with one call limitation."""
        flagname = '_used_%s' % codecmethod.__name__
        if getattr(self, flagname, False):
            raise UnicodeError(
                "Only one call to ``%s()`` is supported per stream instance."
                % codecmethod.__name__ )
        setattr(self, flagname, True)
        return codecmethod(self, input, errors)
    newmethod.__name__ = codecmethod.__name__
    newmethod.__doc__ = codecmethod.__doc__
    return newmethod


# Python codec API
# ================

class Codec(codecs.Codec):
    """Stateless codec for the Underscode encoding."""

    @staticmethod
    def _transcode(codecfunc, input_, errors):
        """Use `codecfunc` to encode or decode the given `input`."""
        if errors != 'strict':
            raise UnicodeError("Only strict error handling is supported.")
        return (codecfunc(input_), len(input_))

    def encode(self, input, errors='strict'):
        """
        Encode the `input` object into Underscode.

        A tuple of (underscoded string, input length consumed) is
        returned.  Only strict error handling is supported.

        See `codecs.Codec.encode()` for more information.
        """
        return self._transcode(underscode_encode, input, errors)

    def decode(self, input, errors='strict'):
        """
        Decode the Underscode-encoded `input` object.

        A tuple of (decoded Unicode string, input length consumed) is
        returned.  Only strict error handling is supported.  Also note
        that, because of the nature of this encoding, empty strings
        are *not* accepted.

        See `codecs.Codec.decode()` for more information.
        """
        return self._transcode(underscode_decode, input, errors)

class StreamWriter(Codec, codecs.StreamWriter):
    """
    Stateful writer for Underscode-encoded streams.

    To ensure that a properly underscoded stream is written out, only
    one write operation is allowed per instance.  Subsequent write
    attempts result in `UnicodeError`.
    """
    encode = one_use_method(Codec.encode)

class StreamReader(Codec, codecs.StreamReader):
    """
    Stateful reader for Underscode-encoded streams.

    To ensure that the underscoded stream is properly decoded, only
    one read operation is allowed per instance.  Subsequent read
    attempts result in `UnicodeError`.
    """
    decode = one_use_method(Codec.decode)

def getregentry():
    """Return callable objects conforming to the Python codec API."""
    encode, decode = Codec().encode, Codec().decode
    if sys.version_info >= (2, 5):
        codecinfo = codecs.CodecInfo(
            encode, decode, StreamReader, StreamWriter,
            name='underscode' )
    else:
        codecinfo = (encode, decode, StreamReader, StreamWriter)
    return codecinfo

def search_function(encoding):
    """Return codec information for the given `encoding`."""
    if encoding == 'underscode':
        return getregentry()
    return None


# Main part
# =========

# Register the Underscode search function so that importing this
# module enables things like ``u'foo bar'.encode('underscode')``.
codecs.register(search_function)

def _test():
    """Run ``doctest`` on this module."""
    import doctest
    doctest.testmod()

if __name__ == '__main__':
    _test()
