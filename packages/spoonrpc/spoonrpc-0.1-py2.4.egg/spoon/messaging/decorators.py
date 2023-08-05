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

from messaging import SingletonMessaging

class handleMsg(object):
    """
    The handleMsg decorator can be used to decorate functions and static methods 
    (NOT methods of class instances) that should receive messages of a given type.
    In the case of static methods, be sure to put the staticmethod decorator first.
    
    When a message of the given type is received, the function will be called with
    (srcNodeId, message type, attached object) as the arguments to it.
    
    @param msgtype: Indicates the message type that the function will receive.
    This can be a list of msgtypes as well as just a string.
    """
    def __init__(self, msgtype):
        if type(msgtype) == str:
            self.msgtype = [msgtype]
        else:
            self.msgtype = msgtype
    
    def __call__(self, handler):
        messaging = SingletonMessaging.getinstance()
        for x in self.msgtype:
            messaging.registerHandler(x, handler)