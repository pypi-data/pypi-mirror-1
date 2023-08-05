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

from spoon import NMTYPE_MESSAGING 


class Messaging(object):
    """
    This is the main messaging class that implements the basic functionality for Spoon.
    Messaging implementations that need specific functionality (such as reliablility) will
    probably want to subclass from this.
    
    There may be multiple instances of Messaging per python process, however there should only be one per
    network to which a node is a member.  There may be a case where one would want a single Messaging instance
    shared between networks however, and as long as the node ids on the networks do not overlap, you shouldn't have
    any problems.
    
    You cannot use the acceptMsg decorator with this, for that you have to use the SingletonMessaging class.
    To register handlers with instances of Messaging, you must use the registerHandler method on
    the Messaging instance.
    """
    def __init__(self, network = None):
        self.handlers = {}
        self.network = network
        if network:
            self.network.nmtypes[NMTYPE_MESSAGING] = self
            
    def registerHandler(self, msgtype, handler):
        handlers = self.handlers.get(msgtype, None)
        if handlers:
            handlers.append(handler)
        else:
            self.handlers[msgtype] = [handler]
        
    def unregisterHandler(self, msgtype, handler):
        handlers = self.handlers.get(msgtype, None)
        if handlers:
            try:
                handlers.remove(handler)
            except:
                pass
    
    def handleMessage(self, src, msg):
        """
        Calls the all handlers for the given message.
        @param src: The source node of the message
        @param msg: A list containing the message type, and the attached object.
        """
        handlers = self.handlers.get(msg[0], [])
        for handler in handlers:
            handler(src, msg[0], msg[1])
    
    def setNetwork(self, network):
        self.network = network
        self.network.nmtypes[NMTYPE_MESSAGING] = self
    
    def send(self, dst, messageStr, obj):
        """
        Sends a Messaging message (not just a NetMessage) to the 
        destination node.
        @param dst: Destination node id
        @param messageStr: A string describing the message type.
        @param obj: Some object attached the net message.
        """
        self.network.sendNetMsg(dst, NMTYPE_MESSAGING, (messageStr, obj))
        

class SingletonMessaging(Messaging):
    """
    For convinience this is a singleton version of the Messaging system.
    This can be used when the node will only have one Messaging system
    throughout the life of the process.  Furthermore, if this is the case
    you can use the function/static method decorator acceptMsg with this.
    """
    singleton = None
    
    @staticmethod
    def getinstance():
        if SingletonMessaging.singleton:
            return SingletonMessaging.singleton
        else:
            SingletonMessaging.singleton = SingletonMessaging()
            return SingletonMessaging.singleton
        
    @staticmethod
    def hasinstance():
        return SingletonMessaging.singleton != None
    
