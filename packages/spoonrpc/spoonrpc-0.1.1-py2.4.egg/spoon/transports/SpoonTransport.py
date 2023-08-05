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

from spoon import SpoonStream
from threading import Semaphore, Thread
from transports import TransportException, TransportHub, LMTYPE_NETWORK, LMTYPE_NETWORK_PROTO, LinkMessage
import StringIO

class SpoonTransport(object):
    """
    The spoon transport base class.  This will probably mostly be responsible for handling locking on
    the transport.  It also takes care of removing itself from the transport hub if it is made inactive.
    
    Any reads or writes on the socket should be performed with the SpoonTransport, or otherwise synchronized 
    once this is created.
    @ivar sock: The raw socket or file object that the transport is bound to
    @ivar spoon: The SpoonStream wrapper around the socket.
    @ivar active: Indicates if the transport is currently active.
    
    """
    def __init__(self, t, network=None):
        """
        Creates a spoon transport link out of an existing socket and joins it to a network.  This network
        is either a mesh network or a point to point network (just a direct connection.)
        @param t: Some sort of a socket or file like object.  
        @param network: An instance of a mesh network or a point to point network that the transport will be joined to.
        """
        self.sock = t
        self.spoon = SpoonStream(self.sock)
        self.active = property(fget=self.__get_active, fset=self.__set_active,\
                               doc="""Will be True as long as the transport is active, will be false if it is inactive.
Transports are made inactive if any exceptions are encountered.""")
        if network:
            self.mtypes = {LMTYPE_NETWORK:network, LMTYPE_NETWORK_PROTO:network}
        else:
            self.mtypes = dict()
        self.nodeId = None
        self.thread = None
        self.__active = False
        self.__wlock = Semaphore()
        self.__rlock = Semaphore()
        
    def __repr__(self):
        return "SpoonTransport(%s, %s)"%(repr(self.sock), repr(self.mtypes[LMTYPE_NETWORK]))
    
    def write(self, obj):
        if not self.active:
            raise TransportException("SpoonTransport %s not active."%(repr(self)))
        self.__wlock.acquire()
        try:
            try:
                self.spoon.write(obj)
            except Exception, ex:
                self.active = False
                raise ex
        finally:
            self.__wlock.release()
    
    def read(self):
        if not self.active:
            raise TransportException("SpoonTransport %s not active."%(repr(self)))
        self.__rlock.acquire()
        try:
            try:
                return self.spoon.read()
            except Exception, ex:
                self.active = False
                
                raise ex
        finally:
            self.__rlock.release()
    
    def fileno(self):
        """
        Returns the fileno for use in a select or poll call if one exists for the socket or file wrapped by this SpoonTransport.
        If the socket or file does not have a fileno method, None will be returned.  For proper behavior with paramiko, fileno 
        on the socket isn't called any time before fileno is called on the SpoonTransport.
        """
        if hasattr(self.sock, "fileno"):
            return self.sock.fileno()
        else:
            return None
        
    def close(self):
        TransportHub.removeTransport(self)
        self.sock.close()
    
    def start(self):
        """
        Starts the spoon protocol on the socket.  Must be called before writing/reading with the SpoonTransport object.
        Will cause the Transport to be registered with TransportHub.
        """
        TransportHub.addTransport(self)
        self.__active = True
        self.thread = SpoonTransportThread(self)
        self.thread.start()
        
    def getAuthedNodeId(self):
        """
        override this if your class does any pre authentication.
        """
        return None
    
    def __get_active(self):
        return self.__active
    
    def __set_active(self, newval):
        if (newval == False) and (self.__active):
            self.__active = newval
            TransportHub.removeTransport(self)
        # Do nothing if trying to do anything else
    
    def getNetwork(self):
        return self.mtypes.get(LMTYPE_NETWORK, None)

class SpoonTransportThread(Thread):
    def __init__(self, t):
        self.sock = t
        Thread.__init__(self, name="SpoonTransportThread for "+repr(t))
    
    def run(self):
        while self.sock.active:
            obj = None
            try:
                obj = self.sock.read()
            except Exception, ex:
                TransportHub._log.error("Got exception '%s' while reading from socket '%s'"%(repr(ex), repr(self.sock)))
                continue
            
            if not isinstance(obj, LinkMessage):
                TransportHub._log.warn("Decoded a message from %s that wasn't a LinkMessage, something's screwy here."%(repr(self.sock)))
                return
            
            if not self.sock.mtypes.has_key(obj.msgtype):
                TransportHub._log.error("Unknown link message type receieved from '%s'"%(repr(self.sock)))
                continue
            try:
                self.sock.mtypes[obj.msgtype].handleLinkMessage(self.sock, obj)
            except Exception, ex:
                TransportHub._log.error("Uncaught exception in link message handler for type %d on transport '%s'"%(obj.msgtype, self.sock), ex)
                continue
        TransportHub._log.debug("SpoonTransportThread stopping")