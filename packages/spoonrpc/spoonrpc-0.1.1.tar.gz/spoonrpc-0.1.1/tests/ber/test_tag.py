#
# Copyright (C) 2003-2006, Robey Pointer <robey@lag.net>
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
# 
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

import unittest
from spoon import ber
from cStringIO import StringIO


class TagTest (unittest.TestCase):

    def test_1_universal(self):
        t = ber.Tag.from_stream(StringIO('\x00\x00'))
        self.assertEqual(t.tag_class, ber.UNIVERSAL)
        self.assertEqual(t.container, False)
        self.assertEqual(t.tag, 0)

        self.assertEqual(len(t), 2)
        s = StringIO()
        t.write(s)
        self.assertEqual(s.getvalue(), '\x00\x00')

    def test_2_application_container(self):
        t = ber.Tag.from_stream(StringIO('\x7e\x00'))
        self.assertEqual(t.tag_class, ber.APPLICATION)
        self.assertEqual(t.container, True)
        self.assertEqual(t.tag, 30)

        self.assertEqual(len(t), 2)
        s = StringIO()
        t.write(s)
        self.assertEqual(s.getvalue(), '\x7e\x00')

    def test_3_context(self):
        t = ber.Tag.from_stream(StringIO('\x81\x00'))
        self.assertEqual(t.tag_class, ber.CONTEXT)
        self.assertEqual(t.container, False)
        self.assertEqual(t.tag, 1)

        self.assertEqual(len(t), 2)
        s = StringIO()
        t.write(s)
        self.assertEqual(s.getvalue(), '\x81\x00')

    def test_4_private(self):
        t = ber.Tag.from_stream(StringIO('\xc9\x00'))
        self.assertEqual(t.tag_class, ber.PRIVATE)
        self.assertEqual(t.container, False)
        self.assertEqual(t.tag, 9)

        self.assertEqual(len(t), 2)
        s = StringIO()
        t.write(s)
        self.assertEqual(s.getvalue(), '\xc9\x00')

    def test_5_long_tag(self):
        t = ber.Tag.from_stream(StringIO('\x9f\x82\x23\x01'))
        self.assertEqual(t.tag_class, ber.CONTEXT)
        self.assertEqual(t.container, False);
        self.assertEqual(t.tag, 0x123)
        self.assertEqual(t.size, 1)

        self.assertEqual(len(t), 4)
        s = StringIO()
        t.write(s)
        self.assertEqual(s.getvalue(), '\x9f\x82\x23\x01')
        
        t = ber.Tag.from_stream(StringIO('\x9f\x8c\xd7\xfa\xf5\x3e\x00'))
        self.assertEqual(t.tag, 0xcafebabeL)

        self.assertEqual(len(t), 7)
        s = StringIO()
        t.write(s)
        self.assertEqual(s.getvalue(), '\x9f\x8c\xd7\xfa\xf5\x3e\x00')

    def test_6_long_size(self):
        t = ber.Tag.from_stream(StringIO('\xc0\x82\x01\x03'))
        self.assertEqual(t.tag_class, ber.PRIVATE)
        self.assertEqual(t.container, False)
        self.assertEqual(t.tag, 0)
        self.assertEqual(t.size, 259)

        self.assertEqual(len(t), 4)
        s = StringIO()
        t.write(s)
        self.assertEqual(s.getvalue(), '\xc0\x82\x01\x03')

    def test_7_errors(self):
        got_exc = False
        try:
            t = ber.Tag.from_stream(StringIO('\x04\x80'))
        except ber.BERException:
            got_exc = True
        self.assert_(got_exc)

        got_exc = False
        try:
            t = ber.Tag.from_stream(StringIO('\x3f'))
        except ber.BERException:
            got_exc = True
        self.assert_(got_exc)

        got_exc = False
        try:
            t = ber.Tag.from_stream(StringIO('\x30'))
        except ber.BERException:
            got_exc = True
        self.assert_(got_exc)

        got_exc = False
        try:
            t = ber.Tag.from_stream(StringIO('\x30\x81'))
        except ber.BERException:
            got_exc = True
        self.assert_(got_exc)

    def test_8_cmp_hash(self):
        t = ber.Tag(ber.CONTEXT, 13, 0)
        self.assertEqual(t, ber.Tag(ber.CONTEXT, 13, 0))
        self.assertEqual(t, ber.Tag.from_stream(StringIO('\x8d\x00')))

        x = {}
        x[t] = 23
        self.assertEqual(x[ber.Tag(ber.CONTEXT, 13, 0)], 23)
        
        self.assertFalse(ber.Tag(ber.CONTEXT, 12, 0) == t)

