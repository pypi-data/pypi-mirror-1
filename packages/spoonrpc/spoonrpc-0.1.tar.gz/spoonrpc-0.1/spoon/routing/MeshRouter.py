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
"""
Mesh Routing, this is the protocol by which an ad-hoc network of nodes can be created and 
how messages may be passed between them.


Routing in SpoonRPC

Baseline:

    * a network of nodes (each node is probably a server)
    * nodes are connected directly to each other by links (probably TCP)
    * from node A to node B, there may be more than one direct route (redundant paths are okay, encouraged in fact, 
      to avoid pitfalls of IRC) 

Route tracking

Each node tracks -- for every other node in the network -- how many hops it is to that node, and which link is used 
to get there.

New links

When a node gains a new link, it sends a message to each of its other links announcing the new hop-count for this 
new link ("Node T, 1 hop"). Each link compares this with any existing route for T, and if the hop count is smaller, 
the route entry is replaced and a new hop count message is sent to each of its local links (except the one it received 
the original message from). In this way, the new route will propagate. When such a message loops back on itself around 
a redundant link, it will be discarded because the hop count will be larger than the one already stored.

If the hop count is larger, but the link making the announcement is the link already in this node's route table, then 
the route's hop-count is changed and the message is propagated anyway. (It means the node's route is now longer than 
it was, or possibly infinite.)

An example may help: Node A is linked directly to B and C. It has a route to node X through B, with 4 hops. (All it 
stores for "X" is "B, 4 hops".) If it receives a message from C saying "X is 2 hops for me" then it will change X's 
route to "C, 3 hops" and send this new route to its other local links (like B). If, on the other hand, C says "X is 5 
hops for me" then A will ignore the message. If A receives a message from B saying "X is 5 hops for me" then A changes 
its route to "B, 6 hops" and sends this new route to all local links.

Once a new link is established, the two newly connected nodes will each send the other a hopcount update message 
containing all of the nodes each knows about. In the case of a node with no connections to the network, connecting 
to a node with connections, this will make the new node aware of all of the nodes that are available. In the case of 
a link forming between two existing networks (or perhaps fragments of a previous network that got disconnected), these 
messages will cause the two networks to be made fully aware of eachother.

Dead links

When a node drops a link, it sends out a message to all other links announcing the hop-count for the dead route as 
"infinity". (This can be represented as 0, -1, maxint, or whatever.) If a link receives an "infinity" route for node 
X from the link that is its current route to X, then the node must drop that route and propagate the "infinity" route 
to all its other links. In this way, if that was the only route to X, everyone will eventually drop the route and have 
X unreachable.

If a node receives an "infinity" route for node X from a link that is not its current route to X, it should immediately 
propagate its current route to that link. This will end up being propagated as if it were a new link (this is really just
good neighbor policy.)

This rerouting mechanism may leave some nodes with inefficient (winding) routes to nodes that move around. So the 
"good neighbor" policy dictates that when you have a route to X, and a link that is not your route sends you info 
about a much longer route (at least 2 hops longer than yours), you turn around and tell this link about your route.

"""
from spoon.transports import LinkMessage
from spoon import LMTYPE_NETWORK, LMTYPE_NETWORK_PROTO, NMTYPE_MESSAGING
from spoon import serialprop, __SPOONNETMSG_TAG__
from spoon import ber

#from spoon.messaging import SingletonMessaging


class NetMessage(object):
    """
    NetMessage is the protocol unit for the networking component of spoon.  It contains a 
    src (source node id), dest (destination node id), message type and an object attachment.
    The object attachment can of course be anything at all that's serializable.
    The message type indicates what subsystem the message should be handled by.  Currently 
    only messaging is implemented, but in the future, who knows.
    @todo: At some point in the future I'd like to add an HMAC here, but I have to sort out
    how keys and such are shared at a protocol level here.  
    """
    def __init__(self, src=None, dst=None, mtype=None, attach=None):
        self.src = src
        self.dst = dst
        self.mtype = mtype
        self.attach = attach
    

@ber.encoder(NetMessage)
def encode_netmessage(fd, obj):
    ber.Tag.from_tag(__SPOONNETMSG_TAG__, None).write(fd)
    b = ber.BERStream(fd)
    b.add(obj.dst)
    b.add(obj.src)
    b.add(obj.mtype)
    b.add(obj.attach)
    b._add_eof()

@ber.decoder(__SPOONNETMSG_TAG__)
def decode_netmessage(fd, tag):
    out = NetMessage()
    b = ber.BERStream(fd)
    out.dst = b.next()
    out.src = b.next()
    out.mtype = b.next()
    out.attach = b.next()
    if b.has_next():
        pass
    return out
    
    
class RoutingProtocolError(Exception):
    pass

class NodeUnreachable(RoutingProtocolError):
    """
    Raised when trying to send to a node that is not currently reachable.  This is not necessarily a 
    permanent condition.  Particularly if a transport has just been lost, a node may become available again 
    within a few seconds as a new route is found.
    """
    def __init__(self, data, nodeId=None):
        self.nodeId = nodeId
        RoutingProtocolError.__init__(self, data)
        

# Just use MAX signed int on a 32 bit scale to represent infinity, AKA, node not reachable.
INFINITY = 2147483647

class MeshRouter(object):
    """
    This class handles LMTYPE_NETWORK messages and LMTYPE_NETWORK_PROTO messages.  LMTYPE_NETWORK_PROTO is handled 
    as a routing update, and LMTYPE_NETWORK will be handled as network traffic to be dealt with or routed.
    
    If there is a SingletonMessaging instance already created (e.g. through the use of 
    the acceptMsg decorator) and messaging is None
    
    @ivar hub: the TransportHub that the router is associated with, should be set at init time and never changed.
    @ivar nodes: This is the routing table.  It's a dictionary whose keys are node ids, and the values are a 
    tuple consisting of the hop count to the node and the transport used to get there.
    @ivar transports:   A set of the transports that are currently active.
    """
    def __init__(self, hub, messaging=None):
        self.hub = hub
        self.nodes = {}
        self.transports = set()
        self.nmtypes = {}
        if messaging:
            self.nmtypes[NMTYPE_MESSAGING] = messaging
        #elif SingletonMessaging.hasinstance():
        #    msging = SingletonMessaging.getinstance()
        #    msging.setNetwork(self)
        #    self.nmtypes[NMTYPE_MESSAGING] = messaging
        
    
    def addTransport(self, t, nodeId):
        """
        Handles the routing protocol initilization.  
        This involves first exchanging routing tables entirely, then updating 
        our routing table as appropriate.  While updating our routing table, 
        we need to construct a routing update message and send it to all transports other than 
        the transport being added.
        @param t: The transport being added to the network
        """
        # Construct a complete table message to send to the new node.
        wholeTable = {}
        for k,v in self.nodes.iteritems():
            wholeTable[k] = v[0]
        wholeTableMessage = LinkMessage(LMTYPE_NETWORK_PROTO, wholeTable)
        
        remoteTable = {}
        # Weird hack... but between the two nodes exchanging tables, the one with the lowest nodeId will send first.
        if nodeId < self.hub.nodeId:
            # Send the table update message to the new node.
            t.write(wholeTableMessage)
            remoteTable = t.read()
        else:
            remoteTable = t.read()
            t.write(wholeTableMessage)
            
        if type(remoteTable) != LinkMessage:
            self.hub._log.error("Invalid protocol message received during transport initialization of routing on transport "+repr(t)+", got '%s'"%(type(remoteTable)))
            raise RoutingProtocolError("Invalid protocol message received during transport initialization of routing on transport "+repr(t))
        # Process the routing table that we've received from the remote node and update our routing table to indicate that
        # we have a route to the remote node with a hopcount of 1.
        self.transports.add(t)
        self.handleUpdate(t, remoteTable.attach, {t.nodeId: (1, t)})
        
    def removeTransport(self, t):
        """
        Removes the transport from the network.  This involves figuring out which nodes are now unreachable (any routes
        we had over that transport), removing any references to the transport from our routing table, and updating
        our neighbors about our changed routing table.
        @param t: The transport being removed from the network
        """
        updatedRoutes = {}
        self.transports.remove(t)
        for k,v in self.nodes.iteritems():
            if v[1] == t:
                self.nodes[k] = (INFINITY, None)
                updatedRoutes[k] = INFINITY
        
        # Normally we'd check to see if updatedRoutes actually contains anything, but it has to at this point.
        for x in self.transports:
            x.write(LinkMessage(LMTYPE_NETWORK_PROTO, updatedRoutes))
        
    def handleUpdate(self, t, update, localUpdate=None):
        """
        Handles a routing table update, builds the update message and sends it out to all except the src of the update.
        @param t: The source transport from which the update came (in other words where NOT to send our update)
        @param update: A dict containing the routing update.
        @param localUpdate: Only used in the specific case of when creating a new transport.  This will include an 
        entry for the node we've just connected to, so that it may be merged into the update sent out to the 
        other nodes.
        """
        # Updated routes will be sent to all transports but t
        updatedRoutes = {}
        # Good neighbor updates will be sent only to t
        goodNeighborUpdate = {}
        if localUpdate:
            # Update our local table with the info in localUpdate
            for k, v in localUpdate.iteritems():
                self.nodes[k] = v
                updatedRoutes[k] = v[0]
        
        for k, v in update.iteritems():
            currentRoute = self.nodes.get(k, None)
            newCount = v + 1
            # Do we have a current route
            if currentRoute:
                # We will update our current route and propagate it if the hop count we're being told about is 
                # better than what we have.  We will also update our current route and propagate it if the
                # hop count is worse than our current route and it is coming from our current route.
                if (newCount < currentRoute[0]) or ((newCount > currentRoute[0]) and (t == currentRoute[1])):
                    updatedRoutes[k] = newCount
                    self.nodes[k] = (newCount, t)
                
                # If the the advertised hopcount +1 is greater than our current hopcount, and the message isn't
                # coming from our current route, we should send a "good neighbor" update to inform the other 
                # node of our better route.
                elif(newCount > currentRoute[0]) and (t != currentRoute[1]):
                    goodNeighborUpdate[k] = currentRoute[0]
            # No current route, so we'll take the first one we hear about until we get a better one
            else:
                updatedRoutes[k] = newCount
                self.nodes[k] = (newCount, t)
        
        # Ok, we should have all of our messages now, let's send them if they have anything
        if updatedRoutes:
            for x in self.transports:
                if x != t:
                    x.write(LinkMessage(LMTYPE_NETWORK_PROTO, updatedRoutes))
        if goodNeighborUpdate:
            t.write(LinkMessage(LMTYPE_NETWORK_PROTO, updatedRoutes))
                
    def handleLinkMessage(self, t, lm):
        """
        Called by the SpoonTransportThread when a link message has been received for one of our 
        LMTYPEs.  
        @param t: The transport that it came from
        @param lm: The LinkMessage that came in.
        """
        self.hub._log.debug("Recieving link message "+repr(lm))
        if lm.msgtype == LMTYPE_NETWORK_PROTO:
            self.handleUpdate(t, lm.attach)
        elif lm.msgtype == LMTYPE_NETWORK:
            self.handleNetworkTraffic(t, lm.attach)
        else:
            raise RoutingProtocolError("Received unknown LinkMessage type %d on transport %s"%(lm.msgtype, repr(t)))
    
    def handleNetworkTraffic(self, t, obj):
        if type(obj) != NetMessage:
            raise RoutingProtocolError("Received unknown content in LinkMessage on transport %s"%(repr(t)))
        handler = self.nmtypes.get(obj.mtype, None)
        # Is this destined to us?  This is where the tricky bit comes in.
        if obj.dst == self.hub.nodeId:
            if not handler:
                # This is destined for us, but we don't have a clue how to handle it
                self.hub._log.warning("Received network message with a handler type of %s but no handler is registered."%(obj.mtype))
                return
            handler.handleMessage(obj.src, obj.attach)
        else:
            route = self.nodes.get(obj.dst, (INFINITY, None))
            if route[0] == INFINITY: 
                self.hub._log.debug("Dropped network message to %d, no current route."%obj.dst)
                return
            if route[1] == t:
                self.hub._log.error("Immediate routing loop detected, something very bad is happening!\
                  Received message for node %d from our route for it, %d"%(obj.dst, t.NodeId))
            route[1].write(LinkMessage(LMTYPE_NETWORK, obj))
    
    def sendNetMsg(self, dst, mtype, obj):
        """
        Sends a network message to the destination specified.
        A NetMessage object is constructed from the arguments provided to this 
        method and routed appropriately.
        @param dst: The node id of the destination
        @param mtype: The message type (probably NMTYPE_MESSAGE)
        @param obj: The object attachment of the NetMessage
        """
        msg = NetMessage(self.hub.nodeId, dst, mtype, obj)
        route = self.nodes.get(dst, (INFINITY, None))
        if route[0] == INFINITY:
            raise NodeUnreachable("NodeId %s is not currently reachable"%dst, dst)
        route[1].write(LinkMessage(LMTYPE_NETWORK, msg))
        