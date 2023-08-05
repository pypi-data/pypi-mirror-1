#!/usr/bin/python
#
# Copyright (C) 2006, Matt Sullivan <matts@zarrf.com>
#
#    This library is free software; you can redistribute it and/or
#    modify it under the terms of the GNU Lesser General Public
#    License as published by the Free Software Foundation; either
#    version 2.1 of the License, or (at your option) any later version.
#
#    This library is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public
#    License along with this library; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

import socket, sys, os, threading, atexit
import spoon, spoon.routing, spoon.messaging, spoon.transports

import traceback

class ConsoleLogger(object):
    def debug(self, msg, *args, **kwargs):
        print msg
        for x in args:
            if isinstance(x, Exception):
                traceback.print_exc()
    def info(self, msg, *args, **kwargs):
        print msg
        for x in args:
            if isinstance(x, Exception):
                traceback.print_exc()
    def warning(self, msg, *args, **kwargs):
        print msg
        for x in args:
            if isinstance(x, Exception):
                traceback.print_exc()
    warn = warning
    def error(self, msg, *args, **kwargs):
        print msg
        for x in args:
            if isinstance(x, Exception):
                traceback.print_exc()
    def critical(self, msg, *args, **kwargs):
        print msg
        for x in args:
            if isinstance(x, Exception):
                traceback.print_exc()
    def log(self, lvl, msg, *args, **kwargs):
        print msg
        for x in args:
            if isinstance(x, Exception):
                traceback.print_exc()
    def exception(self, msg, *args):
        print msg
        
spoon.transports.TransportHub.setLogger(ConsoleLogger())
class ServerMode(object):
    def __init__(self, lsock, nodeId):
        self.lsock = lsock
        spoon.transports.TransportHub.nodeId = nodeId
        self.router = spoon.routing.MeshRouter(spoon.transports.TransportHub, 
                                               spoon.messaging.SingletonMessaging.getinstance())
        self.messaging = spoon.messaging.SingletonMessaging.getinstance()
        self.messaging.setNetwork(self.router)
        self.running = True
        
    def listen(self):
        while self.running:
            try:
                sock, addr = self.lsock.accept()
                sock.setblocking(1)
                spoonSock = spoon.transports.SpoonTransport(sock, self.router)
                spoonSock.start()
            except socket.timeout:
                pass
            
    

class ClientMode(object):
    def __init__(self, sock, nodeId):
        self.sock = sock
        spoon.transports.TransportHub.nodeId = nodeId
        self.router = spoon.routing.MeshRouter(spoon.transports.TransportHub, 
                                               spoon.messaging.SingletonMessaging.getinstance())
        self.messaging = spoon.messaging.SingletonMessaging.getinstance()
        self.messaging.setNetwork(self.router)
        sock.setblocking(1)
        self.spoonSock = spoon.transports.SpoonTransport(sock, self.router)
        
        self.spoonSock.start()

def startServer(nodeId):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("127.0.0.1", 2200))
    sock.listen(5)
    sock.settimeout(1)
    server = ServerMode(sock, int(nodeId))
    sthread = threading.Thread(name="server", target=server.listen)
    sthread.start()
    return server

def startClient(nodeId):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("127.0.0.1", 2200))
    client = ClientMode(sock, int(nodeId))
    return client

connection = None

@spoon.messaging.handleMsg("test")
def msgHandlerTest(src, mtype, attach):
    print "Got '%s' message from %s with '%s'"%(mtype, src, attach)

if __name__ == "__main__":
    mode = sys.argv[1]
    nodeId = sys.argv[2]
    if mode == "server":
        connection = startServer(int(nodeId))
    if mode == "client":
        connection = startClient(int(nodeId))
    
def onExit(objList):
    for x in objList:
        if hasattr(x, "running"):
            x.running = False
    for x in spoon.transports.TransportHub.activeTransports:
        x.active = False

atexit.register(onExit, [connection])
    
    

