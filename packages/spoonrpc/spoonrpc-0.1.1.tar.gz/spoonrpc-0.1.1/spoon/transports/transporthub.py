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

from spoon import Serial, SpoonStream, serialprop, __SPOONLINKMSG_TAG__
from spoon import NullLogger, LMTYPE_INIT, LMTYPE_NETWORK, LMTYPE_NETWORK_PROTO
from spoon import ber

from threading import Thread



class SpoonRPCHello(Serial):
    """
    This object is sent as a very simple form of initial negotiation.
    It contains the nodeId and the protocol version (currently always
    1.)
    """
    nodeId = serialprop()
    version = serialprop(1)
    
class LinkMessage(object):
    """
    Link message is the wrapper which will contain messages sent between two directly connected nodes.
    This message just consists of a msg type (an int) and some arbitrary attachment.  The msgtype 
    determines what system will deal with the message.
    Since this is strictly for use between directly connected nodes, there's no need for src or destination
    fields.
    """
    def __init__(self, msgtype=None, attach=None):
        self.msgtype = msgtype
        self.attach = attach

@ber.encoder(LinkMessage)
def encode_linkmessage(fd, obj):
    ber.Tag.from_tag(__SPOONLINKMSG_TAG__, None).write(fd)
    b = ber.BERStream(fd)
    b.add(obj.msgtype)
    b.add(obj.attach)
    b._add_eof()
@ber.decoder(__SPOONLINKMSG_TAG__)
def decode_linkmessage(fd, tag):
    out = LinkMessage()
    b = ber.BERStream(fd)
    out.msgtype = b.next()
    out.attach = b.next()
    # Pull the EOF off the stream
    if b.has_next():
        pass
    return out

class TransportException(Exception):
    pass

class TransportHub(object):
    """
    Where all of your transports connect to form your glorious new node.
    
    B{Important} you must set the nodeId on this object to something unique for the networks you are 
    joining in order for things to work.  
    
    @cvar activeTransports: A simple list of the transports that are currently active
    @cvar links: A dict, keys are the node id of the directly connected neighbor and the values are 
    the associated transport
    @cvar nodeId: The local node id.  This must be set to the node's integer id before the spoon transport hub is started.
    The nodeId is just a network wide, unique int.  How this is determined is left as an excercise for the implementation.
    In most cases, it should probably be something that is constant for the host/program between instances.
    @type nodeId: int
    """
    activeTransports = []
    links = {}
    nodeId = None
    _log = NullLogger()
    
    @staticmethod
    def setLogger(logger):
        """
        Sets a logger object for SpoonRPC to use.
        
        This can be a python logger object, or just anything that supports that general protocol.
        It defaults to NullLogger which does nothing with the messages.  
        """
        TransportHub._log = logger
    
    @staticmethod
    def addTransport(t):
        """
        Must be called after a transport is initialized to initiate the spoonRPC protocol.
        
        @param t: The transport being initialized
        @return: Nothing
        @raise TransportException: If the protocol initialization fails for some reason.
        """
        if TransportHub.nodeId == None:
            raise TransportException("Cannot initialize transport until nodeId is set on TransportHub. \
         Use spoon.transports.TransportHub.nodeId = someint")
        # This is our protocol initilization, just a simple exchange of nodeId
        hello = SpoonRPCHello()
        hello.nodeId = TransportHub.nodeId
        lmhello = LinkMessage(LMTYPE_INIT, hello)
        t.spoon.write(lmhello)
        remoteLmHello = t.spoon.read()
        remoteHello = remoteLmHello.attach
        if (type(remoteLmHello) != LinkMessage) or (type(remoteHello) != SpoonRPCHello):
            TransportHub._log.error("Did not get proper Hello message from neighbor across transport "+repr(t))
            raise TransportException("Did not get proper Hello message from neighbor across transport "+repr(t))
        
        # TODO Implement something to check that the transport authenticated as the proper node if it supports such a thing
        if TransportHub.links.has_key(remoteHello.nodeId):
            # Try to remove any transports we currently have to this nodeid
            try:
                TransportHub.activeTransports.remove(TransportHub.links[remoteHello.nodeId])
            except:
                pass
            del TransportHub.links[remoteHello.nodeId]
        t.nodeId = remoteHello.nodeId
        TransportHub.links[remoteHello.nodeId] = t
        TransportHub.activeTransports.append(t)
        # TODO possibly refactor this to handle other message types, but we'll figure that out later.
        tNetwork = t.getNetwork()
        if tNetwork:
            tNetwork.addTransport(t, t.nodeId)
        
    @staticmethod
    def removeTransport(t):
        """
        Must be called after a transport has been made inactive.
        
        """
        if not TransportHub.links.has_key(t.nodeId):
            TransportHub._log.warn("Removing transport for nodeId %d and it wasn't in the links dict."%t.nodeId)
            raise TransportException("Removing transport for nodeId %d and it wasn't in the links dict."%t.nodeId)
        del TransportHub.links[t.nodeId]
        TransportHub.activeTransports.remove(t)
        # TODO possibly refactor this to handle other message types, but we'll figure that out later.
        t.getNetwork().removeTransport(t)
    
            
        
        