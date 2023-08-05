#
# Copyright (C) 2006, Matt Sullivan <matts@zarrf.com>
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

import spoon
import ber
import StringIO
import zlib

class SocketFile (object):
    """
    Simple wrapper around a socket like object that pretends to be a file.
    Albeit one that can't seek or tell for obvious reasons.
    """
    def __init__(self, sock):
        self.sock = sock
        
    def read(self, cnt=1):
        return self.sock.recv(cnt)
    
    def write(self, data):
        return self.sock.send(data)
    
    def close(self):
        self.sock.close()

class SpoonStream (object):
    """
    SpoonStream implements an object stream.
    This will take either a file like object or a socket like object
    """
    def __init__(self, fd, compress=False):
        self.compress = compress
        self.realfd = fd
        if hasattr(fd, "write") and hasattr(fd, "read"):
            self.fd = fd
        else:
            self.fd = SocketFile(fd)
        self.buffer = StringIO.StringIO()
    
    def read(self, cnt=None):
        return ber.BERStream(self.fd).next()
    
    def recv(self, cnt=None):
        return self.read()
    
    def write(self, obj):
        ber.BERStream(self.buffer).add(obj, self.compress)
        self.fd.write(self.buffer.getvalue())
        self.buffer.truncate(0)
        
    def send(self, obj):
        self.write(obj)
    
    def close(self):
        self.realfd.close()
    
        