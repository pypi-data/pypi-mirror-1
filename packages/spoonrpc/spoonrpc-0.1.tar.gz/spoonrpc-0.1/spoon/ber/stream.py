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

from cStringIO import StringIO

from common import BERException, deflate_long, inflate_long
from common import UNIVERSAL, APPLICATION, CONTEXT, PRIVATE
from tag import Tag


UNIVERSAL_BOOL = 1
UNIVERSAL_INT = 2
UNIVERSAL_BYTES = 4
UNIVERSAL_NULL = 5
UNIVERSAL_UTF8 = 12
UNIVERSAL_LIST = 16

EOF_TYPE = Tag(UNIVERSAL, 0, 0)
NULL_TYPE = Tag(UNIVERSAL, UNIVERSAL_NULL)
BOOL_TYPE = Tag(UNIVERSAL, UNIVERSAL_BOOL)
INT_TYPE = Tag(UNIVERSAL, UNIVERSAL_INT)
BYTES_TYPE = Tag(UNIVERSAL, UNIVERSAL_BYTES)
UTF8_TYPE = Tag(UNIVERSAL, UNIVERSAL_UTF8)
LIST_TYPE = Tag(UNIVERSAL, UNIVERSAL_LIST, container=True)


class CountingFile (object):
    def __init__(self, fd):
        self._fd = fd
        self.count = 0
    
    def read(self, n):
        out = self._fd.read(n)
        self.count += len(out)
        return out

    def __getattr__(self, name):
        return getattr(self._fd, name)


class BERStream (object):
    """
    FIXME docs
    """
    
    _encoder_table = {}
    _zencoder_table = {}
    _decoder_table = {}

    def __init__(self, fd, size=None):
        self._fd = fd
        self._bytes_read = 0
        self._size = size
        self._hit_eof = False
        self._advance_tag = None

    def _next_tag(self):
        tag = Tag.from_stream(self._fd)
        if tag is None:
            raise BERException('Stream overrun')
        self._bytes_read += len(tag)            
        if (self._size is not None) and (self._bytes_read > self._size):
            raise BERException('Stream overrun')
        return tag

    def has_next(self):
        """
        Return C{True} if there is still more data left in this stream, and
        a future call to L{next} should succeed.
        
        @return: C{True} if the stream has more data to read
        """
        if self._size is not None:
            return self._bytes_read < self._size
        if self._hit_eof:
            return False

        # indefinite length -- read the next tag
        if self._advance_tag is not None:
            # i've already read the next tag :)
            return not self._hit_eof
        self._advance_tag = self._next_tag()
        if self._advance_tag == EOF_TYPE:
            self._hit_eof = True
            return False
        return True

    def next(self):
        """
        Return the next item from this stream.  Objects are decoded using the
        codecs registered via the L{decoder} operator, though simple types
        (None, bool, int, long, str, unicode, list, and tuple) have default
        decoders.
        
        @return: the next object from the stream
        @rtype: object
        @raise BERException: if you're already at the end of the stream
        """
        
        if not self.has_next():
            # end of stream
            raise BERException('End of stream')
        
        if self._advance_tag is not None:
            # indefinite length mode
            tag = self._advance_tag
            self._advance_tag = None
        else:
            tag = self._next_tag()

        decoder = self._decoder_table.get(tag, None)
        if decoder is None:
            raise BERException('Can\'t decode object of type %r' % (tag,))

        # insert a counting fd so we can track how many bytes were actually read
        count_fd = CountingFile(self._fd)
        obj = decoder(count_fd, tag)
        if tag.size is not None:
            if count_fd.count > tag.size:
                raise BERException('Overrun in decoder for type %r' % (tag,))
            if count_fd.count < tag.size:
                raise BERException('Underrun in decoder for type %r' % (tag,))
            self._bytes_read += tag.size
        else:
            # that was an indefinite-length sequence: trust that the correct number of bytes were read
            self._bytes_read += count_fd.count
        return obj

    def add(self, item, compress=False):
        """
        Write an object into the stream.  Simple types (None, bool, int, long,
        str, unicode, list, and tuple) are handled by default encoders.  Other
        encoders may be added with the L{encoder} decorator.
        
        @param item: object to add
        @type item: object
        """
        encoder = BERStream._get_encoder(item, compress)
        if encoder is None:
            raise BERException('Can\'t encode object of type %r' % (type(item),))
        encoder(self._fd, item)
    
    def _add_eof(self):
        EOF_TYPE.write(self._fd)

    @staticmethod
    def _get_encoder(item, compress=False):
        # walk the mro, so a codec can be defined for a superclass
        for cls in type(item).__mro__:
            if compress:
                encoder = BERStream._zencoder_table.get(cls, None)
                if encoder is None:
                    # Don't compress if we can't find something to compress with
                    encoder = BERStream._encoder_table.get(cls, None)
            else:
                encoder = BERStream._encoder_table.get(cls, None)
            if encoder is not None:
                return encoder
        return None

    @staticmethod
    def can_encode(item):
        return (BERStream._get_encoder(item) is not None)
class zencoder (object):
    # decorator used to mark functions for encoding compressed types
    # compressed functions should use different types than their non 
    # compressed counterparts, and thus a zdecoder isn't necessary.
    def __init__(self, *types):
        self._types = types
    
    def __call__(self, f):
        for t in self._types:
            BERStream._zencoder_table[t] = f
        return f
    
class encoder (object):
    # decorator
    
    def __init__(self, *types):
        self._types = types
    
    def __call__(self, f):
        for t in self._types:
            BERStream._encoder_table[t] = f
        return f


class decoder (object):
    # decorator
    
    def __init__(self, ttype):
        self._type = ttype
    
    def __call__(self, f):
        BERStream._decoder_table[self._type] = f
        return f


def encode_container(fd, tag, items):
    """
    Encode a list of items into a container with the given tag and write it
    to a stream.  The list is written using indefinite-length encoding, so
    no extra copying occurs.
    
    @param fd: the file object to write into
    @type fd: file
    @param tag: the tag to use for this list
    @type tag: L{Tag}
    @param items: a list of items to put into the container
    @type items: list or iterable
    """
    Tag.from_tag(tag, None).write(fd)
    b = BERStream(fd)
    for x in items:
        b.add(x)
    b._add_eof()


def decode_container(fd, tag):
    """
    Decode a container into a list of items.
    
    @param fd: the file object to read from
    @type fd: file
    @param tag: the tag from the container
    @type tag: L{Tag}
    @return: a list of decoded objects
    @rtype: list
    """
    b = BERStream(fd, tag.size)
    out = []
    while b.has_next():
        out.append(b.next())
    return out


@encoder(type(None))
def encode_null(fd, item):
    Tag.from_tag(NULL_TYPE, 0).write(fd)

@decoder(NULL_TYPE)
def decode_null(fd, tag):
    return None

@encoder(bool)
def encode_bool(fd, item):
    Tag.from_tag(BOOL_TYPE, 1).write(fd)
    if item:
        fd.write('\xff')
    else:
        fd.write('\x00')


@decoder(BOOL_TYPE)
def decode_bool(fd, tag):
    if tag.size != 1:
        raise BERException('unexpected size of boolean (%d)' % (tag.size,))
    data = fd.read(1)
    if len(data) < 1:
        raise BERException('abrupt end of stream')
    if ord(data) == 0:
        return False
    return True

@encoder(int, long)
def encode_int(fd, item):
    x = deflate_long(item)
    Tag.from_tag(INT_TYPE, len(x)).write(fd)
    fd.write(x)

@decoder(INT_TYPE)
def decode_int(fd, tag):
    return inflate_long(fd.read(tag.size))

@encoder(str)
def encode_str(fd, item):
    Tag.from_tag(BYTES_TYPE, len(item)).write(fd)
    fd.write(item)

@decoder(BYTES_TYPE)
def decode_str(fd, tag):
    return fd.read(tag.size)

@encoder(unicode)
def encode_unicode(fd, item):
    x = item.encode('utf-8')
    Tag.from_tag(UTF8_TYPE, len(x)).write(fd)
    fd.write(x)

@decoder(UTF8_TYPE)
def decode_unicode(fd, tag):
    return fd.read(tag.size).decode('utf-8')

@encoder(list, tuple)
def encode_list(fd, items):
    encode_container(fd, LIST_TYPE, items)

@decoder(LIST_TYPE)
def decode_list(fd, tag):
    return decode_container(fd, tag)

