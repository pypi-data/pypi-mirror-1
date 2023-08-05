"""Unit tests for the Underscode package."""

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


# Tests
# =====

import unittest
import underscode
import underscode.core
import underscode.codec
import underscode.exceptions
import underscode.decorators

class DecodingTestCase(unittest.TestCase):

    """Test decoding Underscode-encoded strings."""

    def test_valid_string(self):
        """Decoding and checking whole valid strings."""

        # The steps mentioned here take the decoding of an encoded
        # character as a single step (here, decoding ``_`` is used).
        # Then, there are only five possible steps, according to the
        # finite state machine.
        valid_encoded = [
            # Valid in zero different steps.
            {},
            # Valid in one different step.
            {'_': u''},
            # Valid in two different steps.
            {'z_': u'z'},
            # Valid in three different steps.
            { '___': u' ',
              'zz_': u'zz', },
            # Valid in four different steps.
            { '__z_': u' z',
              'z___': u'z ', },
            # Valid in five different steps.
            {'z__z_': u'z z'}, ]

        for nsteps in range(len(valid_encoded)):
            for (encoded, decoded) in valid_encoded[nsteps].items():
                # Check ``is_underscode_encoded()``.
                self.assert_(underscode.is_underscode_encoded(encoded))
                # Check ``underscode_decode()``.
                udecoded = underscode.underscode_decode(encoded)
                self.assert_(type(udecoded) is unicode)
                self.assertEqual(udecoded, decoded)

    def test_invalid_string(self):
        """Decoding and checking whole invalid strings."""

        invalid = underscode.InvalidChar
        incomplete = underscode.EndOfInput

        # The steps mentioned here take the decoding of an encoded
        # character as a single step (here, decoding ``_`` is used).
        # Then, there are only five possible steps, according to the
        # finite state machine.
        invalid_encoded = [
            # Invalid in zero different steps.
            {'': incomplete},
            # Invalid in one different step.
            { 'z': incomplete,
              '/': invalid, },
            # Invalid in two different steps.
            { '__': incomplete,
              '_/': invalid,
              'zz': incomplete,
              'z/': invalid,
              'z0': incomplete,
              '_z': invalid,
              '_/': invalid,
              'z/': invalid, },
            # Invalid in three different steps.
            { '__z': incomplete,
              '__/': invalid,
              'zz/': invalid,
              'z_/': invalid, },
            # Invalid in four different steps.
            { '___/': invalid,
              '__z/': invalid,
              'z__z': incomplete,
              'z__/': invalid, },
            # Invalid in five different steps.
            { '__z_/': invalid,
              'z__z/': invalid, }, ]

        for nsteps in range(len(invalid_encoded)):
            for (encoded, exception) in invalid_encoded[nsteps].items():
                # Check ``is_underscode_encoded()``.
                self.assert_(not underscode.is_underscode_encoded(encoded))
                # Check ``underscode_decode()``.
                self.assertRaises(
                    exception, underscode.underscode_decode, encoded )

    def test_valid_character(self):
        """Decoding and checking valid encoded characters."""

        valid_encodings = {
            u'a': ['a_', '_x61_', '_u0061_', '_U00000061_'],
            u' ': ['___', '_x20_', '_u0020_', '_U00000020_'],
            u'0': ['_0_', '_x30_', '_u0030_', '_U00000030_'],
            u'_': ['_x5f_', '_u005f_', '_U0000005f_'],
            u'\x1a': ['_x1a_', '_u001a_', '_U0000001a_'],
            u'\u12ab': ['_u12ab_', '_U000012ab_'],
            u'\U0001abcd': ['_U0001abcd_'], }

        for (decoded, encodings) in valid_encodings.items():
            for encoded in encodings:
                # Check ``is_underscode_encoded()``.
                self.assert_(underscode.is_underscode_encoded(encoded))
                # Check ``underscode_decode()``.
                udecoded = underscode.underscode_decode(encoded)
                self.assert_(type(udecoded) is unicode)
                self.assertEqual(udecoded, decoded)

    def test_invalid_character(self):
        """Decoding and checking invalid encoded characters."""

        valid_encoded = [
            'a_', '___', '_0_', '_x5f_', '_x1a_', '_u12ab_', '_U0001abcd_' ]

        # All incomplete versions for each of the previous encoded
        # characters; from two input characters on, since ``_`` is a
        # valid encoded string with no encoded characters, and up to
        # the full encoded character bar the final underscore.
        incomplete_encoded = [
            [encchar[:i] for i in range(2, len(encchar))]
            for encchar in valid_encoded ]

        # All invalid versions for each of the previous encoded
        # characters; from two input characters on, since an odd
        # invalid first character does not yet start an encoded
        # character, and up to the full encoded character bar the
        # final underscore.
        invalid_encoded = [
            [encchar[:i] + '/' for i in range(1, len(encchar))]
            for encchar in valid_encoded ]

        invalid_encodings = {
            underscode.InvalidChar: invalid_encoded,
            underscode.EndOfInput: incomplete_encoded, }

        for (exception, encchars) in invalid_encodings.items():
            for encchar in encchars:
                for encoded in encchar:
                    # Check ``is_underscode_encoded()``.
                    self.assert_(not underscode.is_underscode_encoded(encoded))
                    # Check ``underscode_decode()``.
                    self.assertRaises(
                        exception, underscode.underscode_decode, encoded )

class EncodingTestCase(unittest.TestCase):

    """Test encoding Unicode strings to Underscode."""

    def test(self):
        """Encoding Unicode strings."""

        # Since characters are encoded one at a time, checking for at
        # most one character long strings is enough.  However, numbers
        # are not encoded in the same way at the beginning and in the
        # middle of a string.
        canonical_encoding = [
            # 0 characters.
            {u'': '_'},
            # 1 character.
            { u'a': 'a_',
              u' ': '___',
              u'0': '_0_',
              u'_': '_x5f_',
              u'\x1a': '_x1a_',
              u'\u12ab': '_u12ab_',
              u'\U0001abcd': '_U0001abcd_', },
            # 2 characters.
            {u'a0': 'a0_'}, ]

        for nsteps in range(len(canonical_encoding)):
            for (decoded, encoded) in canonical_encoding[nsteps].items():
                # Check ``underscode_encode()``.
                uencoded = underscode.underscode_encode(decoded)
                self.assert_(type(uencoded) is str)
                self.assertEqual(uencoded, encoded)

class ProxyDecoratorTestCase(unittest.TestCase):

    """Test using the ``proxy_method`` decorator."""

    class AttributedDict(dict):
        """Dictionary with items accessible via underscoded attributes."""
        @underscode.decorators.proxy_method(dict.__getitem__)
        def __getattr__(self, name):
            return super(self.__class__, self).__getattr__(name)
        @underscode.decorators.proxy_method(dict.__setitem__)
        def __setattr__(self, name, value):
            super(self.__class__, self).__setattr__(name, value)
        @underscode.decorators.proxy_method(dict.__delitem__)
        def __delattr__(self, name):
            super(self.__class__, self).__delattr__(name)

    def test_proxy(self):
        """Using methods decorated with ``proxy_method``."""
        from operator import getitem

        adict = self.AttributedDict()
        self.assertEqual(adict, {})

        # Accessing normal attributes.
        for value in ['foo', 'bar']:
            adict.foo = value
            self.assertEqual(adict.foo, value)
            self.assertEqual( adict, {},
                              "A call with a non-underscoded argument "
                              "was derived to the access method." )
        del adict.foo
        self.assertRaises(AttributeError, getattr, adict, 'foo')

        # Accessing underscoded attributes.
        adict.foo = 'foo'
        for (name0, name1) in [(u'foo', u'bar'), (u'bar', u'foo')]:
            encoded_name0 = underscode.underscode_encode(name0)
            encoded_name1 = underscode.underscode_encode(name1)
            adict[name0] = 42
            setattr(adict, encoded_name1, 43)
            self.assertEqual(adict.foo, 'foo')
            self.assertEqual(adict[name0], 42)
            self.assertEqual(adict[name1], 43)
            self.assertEqual(getattr(adict, encoded_name0), 42)
            self.assertEqual(getattr(adict, encoded_name1), 43)

        # Using alternative encodings and deleting.
        self.assertEqual(getattr(adict, 'foo_'), getattr(adict, '_x66oo_'))
        adict._x66oo_ = 100
        self.assertEqual(adict.foo_, 100)
        del adict._x66oo_, adict.bar_
        for name in [u'foo', u'bar']:
            encoded_name = underscode.underscode_encode(name)
            self.assertRaises(KeyError, getattr, adict, encoded_name)
            self.assertRaises(KeyError, getitem, adict, name)

        self.assertEqual(adict.foo, 'foo')
        self.assertEqual(adict, {})

class MembersDecoratorsTestCase(ProxyDecoratorTestCase):

    """Test using the ``members_*`` decorators."""

    class AttributedDict(dict):
        """Dictionary with items accessible via underscoded attributes."""
        def __init__(self):
            self.__dict__['__members__'] = []
            super(self.__class__, self).__init__()

        __setitem__ = underscode.decorators.members_setter(dict.__setitem__)
        __delitem__ = underscode.decorators.members_deleter(dict.__delitem__)

        @underscode.decorators.proxy_method(dict.__getitem__)
        def __getattr__(self, name):
            return super(self.__class__, self).__getattr__(name)
        @underscode.decorators.proxy_method(__setitem__)
        def __setattr__(self, name, value):
            super(self.__class__, self).__setattr__(name, value)
        @underscode.decorators.proxy_method(__delitem__)
        def __delattr__(self, name):
            super(self.__class__, self).__delattr__(name)

class DictDecoratorsTestCase(ProxyDecoratorTestCase):

    """Test using the ``dict_*`` decorators."""

    class AttributedDict(dict):
        """Dictionary with items accessible via underscoded attributes."""

        __getitem__ = underscode.decorators.dict_getter(dict.__getitem__)
        __setitem__ = underscode.decorators.dict_setter(dict.__setitem__)
        __delitem__ = underscode.decorators.dict_deleter(dict.__delitem__)

        @underscode.decorators.proxy_method(__getitem__)
        def __getattr__(self, name):
            return super(self.__class__, self).__getattr__(name)
        @underscode.decorators.proxy_method(__setitem__)
        def __setattr__(self, name, value):
            super(self.__class__, self).__setattr__(name, value)
        @underscode.decorators.proxy_method(__delitem__)
        def __delattr__(self, name):
            super(self.__class__, self).__delattr__(name)


# Main part
# =========

def suite():
    """Return a test suite comprising all tests in the module."""
    import doctest

    # List of modules with doctests to be checked.
    doctest_modules = [
        underscode,
        underscode.core,
        underscode.codec,
        underscode.exceptions,
        underscode.decorators, ]
    # List of test cases defined here.
    unittest_cases = [
        DecodingTestCase,
        EncodingTestCase,
        ProxyDecoratorTestCase,
        MembersDecoratorsTestCase,
        DictDecoratorsTestCase, ]

    # Create the main suite and add every other suite to it.
    test_suite = unittest.TestSuite()
    for test_module in doctest_modules:
        test_suite.addTest(doctest.DocTestSuite(test_module))
    for test_case in unittest_cases:
        test_suite.addTest(unittest.makeSuite(test_case))
    return test_suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
