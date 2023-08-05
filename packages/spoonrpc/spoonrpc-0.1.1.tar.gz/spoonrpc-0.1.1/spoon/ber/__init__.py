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
"""
The low level BER based encoding used by spoon to serialize objects. 

Users of the spoon library will probably not need to use this package 
at all.
"""

from cStringIO import StringIO

from common import UNIVERSAL, APPLICATION, CONTEXT, PRIVATE
from common import BERException

from tag import Tag
from stream import BERStream, encoder, zencoder, decoder, encode_container, decode_container
from stream import EOF_TYPE, NULL_TYPE, INT_TYPE, BYTES_TYPE, UTF8_TYPE, LIST_TYPE


def encode_stream(fd, *items):
    """
    Encode one or more python objects into a ber stream, written to the
    given file object.
    """
    b = BERStream(fd)
    for x in items:
        b.add(x)


def decode_stream(fd):
    """
    Decode a ber-encoded python object from a file object and return it.
    """
    return BERStream(fd).next()


def encode(*items):
    """
    Encode one or more python objects into a ber stream, and return the
    encoded string.
    """
    s = StringIO()
    encode_stream(s, *items)
    return s.getvalue()


def decode(s):
    """
    Decode a python object from a ber-encoded string and return it.
    """
    return decode_stream(StringIO(s))

for x in [decode, encode, decode_stream, encode_stream, BERException, Tag, 
          BERStream, encoder, zencoder,
          decoder, encode_container, decode_container, 
          EOF_TYPE, NULL_TYPE, INT_TYPE, BYTES_TYPE, UTF8_TYPE, LIST_TYPE]:
    x.__module__ = "spoon.ber"

__all__ = ["decode", 
           "encode", 
           "decode_stream", 
           "encode_stream", 
           "UNIVERSAL", 
           "APPLICATION",
           "CONTEXT", 
           "PRIVATE", 
           "BERException", 
           "Tag", 
           "BERStream", 
           "encoder", 
           "zencoder",
           "decoder", 
           "encode_container", 
           "decode_container", 
           "EOF_TYPE", 
           "NULL_TYPE", 
           "INT_TYPE", 
           "BYTES_TYPE", 
           "UTF8_TYPE", 
           "LIST_TYPE"]