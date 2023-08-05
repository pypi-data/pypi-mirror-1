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
from cStringIO import StringIO

from spoon import ber


class Data (object):
    TAG = ber.Tag(ber.CONTEXT, 100)
    def __init__(self, data):
        self.data = data


class Sequence (object):
    TAG = ber.Tag(ber.APPLICATION, 200, container=True)
    def __init__(self, seq):
        self.seq = seq
    
    def __eq__(self, other):
        if type(other) is not Sequence:
            return False
        if len(self.seq) != len(other.seq):
            return False
        for i in range(len(self.seq)):
            if self.seq[i] != other.seq[i]:
                return False
        return True


@ber.encoder(Data)
def encode_data(fd, item):
    ber.Tag.from_tag(Data.TAG, len(item.data)).write(fd)
    fd.write(item.data)

@ber.decoder(Data.TAG)
def decode_data(fd, tag):
    return Data(fd.read(tag.size))

@ber.encoder(Sequence)
def encode_seq(fd, item):
    ber.encode_container(fd, Sequence.TAG, item.seq)

@ber.decoder(Sequence.TAG)
def decode_seq(fd, tag):
    return Sequence(ber.decode_container(fd, tag))


EXAMPLE = '\x7f\x81\x48\x80\x0c\x06README\x0c\x0atext/plain\x30\x80\x02' + \
    '\x02\x01\xb4\x02\x02\x02\x9a\x7f\x81\x48\x80\x02\x04\x40\x77\xbf\xf3' + \
    '\x02\x01\x00\x00\x00\x7f\x81\x48\x80\x02\x04\x40\x77\xbf\xf6\x02\x01' + \
    '\x00\x00\x00\x00\x00\x30\x80\x0c\x05robey\x30\x80\x0c\x05robey\x00' + \
    '\x00\x00\x00\x00\x00'


class EncodeStreamTest (unittest.TestCase):

    def test_1_encode_simple(self):
        s = StringIO()
        ber.encode_stream(s, 23)
        self.assertEqual(s.getvalue(), '\x02\x01\x17')

        s = StringIO()
        ber.encode_stream(s, 23L)
        self.assertEqual(s.getvalue(), '\x02\x01\x17')

        s = StringIO()
        ber.encode_stream(s, False)
        self.assertEqual(s.getvalue(), '\x01\x01\x00')

        s = StringIO()
        ber.encode_stream(s, 'kitten')
        self.assertEqual(s.getvalue(), '\x04\x06kitten')

        s = StringIO()
        ber.encode_stream(s, u'f\xfcnky')
        self.assertEqual(s.getvalue(), '\x0c\x06f\xc3\xbcnky')

    def test_2_encode_simple_list(self):
        s = StringIO()
        ber.encode_stream(s, [])
        self.assertEqual(s.getvalue(), '\x30\x80\x00\x00')

        s = StringIO()
        ber.encode_stream(s, [ 0x23, '\xff', True ])
        self.assertEqual(s.getvalue(), '\x30\x80\x02\x01\x23\x04\x01\xff\x01\x01\xff\x00\x00')

        s = StringIO()
        ber.encode_stream(s, [ 0x23, [ 10 ], True ])
        self.assertEqual(s.getvalue(), '\x30\x80\x02\x01\x23\x30\x80\x02\x01\x0a\x00\x00\x01\x01\xff\x00\x00')

    def test_3_encode_data(self):
        s = StringIO()
        ber.encode_stream(s, Data('vox'))
        self.assertEqual(s.getvalue(), '\x9f\x64\x03vox')

        s = StringIO()
        ber.encode_stream(s, Data('\xff\x00'))
        self.assertEqual(s.getvalue(), '\x9f\x64\x02\xff\x00')

    def test_4_encode_sequence(self):
        s = StringIO()
        ber.encode_stream(s, Sequence([ 3, 9 ]))
        self.assertEqual(s.getvalue(), '\x7f\x81\x48\x80\x02\x01\x03\x02\x01\x09\x00\x00')

        s = StringIO()
        ber.encode_stream(s, Sequence([ 3, '', False ]))
        self.assertEqual(s.getvalue(), '\x7f\x81\x48\x80\x02\x01\x03\x04\x00\x01\x01\x00\x00\x00')

    def test_5_encode_complex(self):
        s = StringIO()
        timestamp1 = Sequence([ 1081589747L, 0L ])
        timestamp2 = Sequence([ 1081589750L, 0L ])
        ber.encode_stream(s, Sequence([ u'README', u'text/plain', [ 0664L, 666L, timestamp1, timestamp2 ], [ u'robey', [ u'robey' ]]]))
        self.assertEqual(s.getvalue(), EXAMPLE)

    def test_6_decode_simple(self):
        x = ber.decode_stream(StringIO('\x02\x01\x17'))
        self.assertEqual(23L, x)

        x = ber.decode_stream(StringIO('\x0c\x03hey'))
        self.assertEqual(u'hey', x)

        x = ber.decode_stream(StringIO('\x01\x01\x00'))
        self.assertEqual(False, x)

        x = ber.decode_stream(StringIO('\x04\x09candidate'))
        self.assertEqual('candidate', x)

    def test_7_decode_sequence(self):
        x = ber.decode_stream(StringIO('\x30\x09\x02\x02\x5a\x93\x04\x03cat'))
        self.assertTrue(type(x) is list)
        self.assertEqual(2, len(x))
        self.assertEqual(23187, x[0])
        self.assert_(type(x[1]) is str)
        self.assertEqual('cat', x[1])

        x = ber.decode_stream(StringIO('\x30\x80\x02\x02\x5a\x93\x04\x03cat\x00\x00'))
        self.assert_(type(x) is list)
        self.assertEqual(2, len(x))
        self.assertEqual(23187, x[0])
        self.assert_(type(x[1]) is str)
        self.assertEquals('cat', x[1])

    def test_8_decode_nested_sequence(self):
        x = ber.decode_stream(StringIO('\x30\x07\x30\x02\x05\x00\x01\x01\xff'))
        self.assert_(type(x) is list)
        self.assertEqual(2, len(x))
        self.assert_(type(x[0]) is list)
        self.assertEqual(1, len(x[0]))
        self.assert_(type(x[0][0]) is type(None))
        self.assertEqual(None, x[0][0])
        self.assert_(type(x[1]) is bool)
        self.assertEqual(True, x[1])

        x = ber.decode_stream(StringIO('\x30\x80\x30\x80\x05\x00\x00\x00\x01\x01\xff\x00\x00'))
        self.assert_(type(x) is list)
        self.assertEqual(2, len(x))
        self.assert_(type(x[0]) is list)
        self.assertEqual(1, len(x[0]))
        self.assert_(type(x[0][0]) is type(None))
        self.assertEqual(None, x[0][0])
        self.assert_(type(x[1]) is bool)
        self.assertEqual(True, x[1])

    def test_9_decode_complex_sequence(self):
        x = ber.decode_stream(StringIO(EXAMPLE))
        self.assert_(type(x) is Sequence)
        self.assertEqual(4, len(x.seq))
        self.assert_(type(x.seq[0]) is unicode)
        self.assertEqual(u'README', x.seq[0])
        self.assert_(type(x.seq[1]) is unicode)
        self.assertEqual(u'text/plain', x.seq[1])
        self.assert_(type(x.seq[2]) is list)
        self.assertEqual(4, len(x.seq[2]))
        self.assert_(type(x.seq[2][0]) is long)
        self.assertEqual(436L, x.seq[2][0])
        self.assert_(type(x.seq[2][1]) is long)
        self.assertEqual(666L, x.seq[2][1])

        y = x.seq[2][2]
        self.assert_(type(y) is Sequence)
        self.assertEqual(2, len(y.seq))
        self.assert_(type(y.seq[0]) is long)
        self.assertEqual(1081589747L, y.seq[0])
        self.assert_(type(y.seq[1]) is long)
        self.assertEqual(0L, y.seq[1])

        y = x.seq[2][3]
        self.assert_(type(y) is Sequence)
        self.assertEqual(2, len(y.seq))
        self.assert_(type(y.seq[0]) is long)
        self.assertEqual(1081589750L, y.seq[0])
        self.assert_(type(y.seq[1]) is long)
        self.assertEqual(0L, y.seq[1])

        self.assert_(type(x.seq[3]) is list)
        self.assertEqual(2, len(x.seq[3]))
        self.assert_(type(x.seq[3][0]) is unicode)
        self.assertEqual(u'robey', x.seq[3][0])
        self.assert_(type(x.seq[3][1]) is list)
        self.assertEqual(1, len(x.seq[3][1]))
        self.assert_(type(x.seq[3][1][0]) is unicode)
        self.assertEqual(u'robey', x.seq[3][1][0])

        timestamp1 = Sequence([ 1081589747L, 0L ])
        timestamp2 = Sequence([ 1081589750L, 0L ])
        self.assertEqual(Sequence([u'README', u'text/plain', [ 0664L, 666L, timestamp1, timestamp2 ], [ u'robey', [ u'robey' ]]]), x)
