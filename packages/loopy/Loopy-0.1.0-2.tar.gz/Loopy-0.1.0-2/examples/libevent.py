# Module: loop.libevent.example
# File: example.py
# Copyright (C) 2007 Ariel De Ocampo arieldeocampo@gmail.com
#
# This module is part of the loopy project and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

#from ctypes import *

import socket
import os
import signal

from loopy.libevent.wrapper import *
from loopy.libevent.core import *
from loopy.libevent.fd import *

class SocketConnected(SocketEvent): #{{{
    __slots__ = ()
    def __init__(self, sckt, timeout=None): #{{{
        super(SocketConnected, self).__init__(sckt, timeout)
        self._auto_close = False
    # End def #}}}
    def _on_call(self, *args): #{{{
        s = self.socket
        client_sock, addr = s.accept()
        client_sock.setblocking(False)
        self.callback(client_sock, addr)
        print 'LISTENING SOCKET:', s.fileno(), 'CLIENT SOCKET:', client_sock.fileno()
        self._auto_close = True
    # End def #}}}

    def callback(self, sckt, addr): #{{{
        raise NotImplementedError("on_accept not implemented")
    # End def #}}}
# End class #}}}

class CreateSocket(TimeoutEvent): #{{{
    __slots__ = ('_bind_args',)
    def __init__(self, timeout=0, *bind_args): #{{{
        super(CreateSocket, self).__init__(timeout)
        self._bind_args = bind_args
    # End def #}}}
    def _on_call(self, *args): #{{{
        host, port = self._bind_args
        listen_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while 1:
            try:
                listen_sock.bind((host, port))
            except socket.error:
                port += 1
            else:
                print "PORT:", port
                break
        listen_sock.listen(5)
        reuseaddr_on = 1
        listen_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, reuseaddr_on)
        listen_sock.setblocking(False)
        self.callback(listen_sock)
        print 'NEW SOCKET:', listen_sock.fileno()
    # End def #}}}

    def callback(self, sckt): #{{{
        raise NotImplementedError("on_new_socket not implemented")
    # End def #}}}
# End class #}}}

def test_hello(): #{{{
    class HelloWorld(TimeoutEvent): #{{{
        def __init__(self, timeout=0): #{{{
            super(HelloWorld, self).__init__(timeout)
            self.v.count = 0
        # End def #}}}
        def callback(self): #{{{
            print 'Hello world', self.v.count
            self.v.count += 1
            self.event_loop.register(self)
        # End def #}}}
    # End class #}}}
    msg = HelloWorld()
    evloop = EventLoop()
    import signal
    evloop.register_signal(signal.SIGINT)
    evloop.register(msg)
    evloop.loop(count=5)
    print 'CLOSING...'
    evloop.close()
    print 'CLOSED'
# End def #}}}

def test_echo(HOST, SERVER_PORT): #{{{
    class BufferedEchoEvent(BufferedEvent, SocketEvent): #{{{
        __slots__ = ()
        def on_read(self): #{{{
            print 'READ'
            data = self.read_buffer
            if data.strip() == 'quit':
                self.event_loop.end_loop()
                return
            self.write(data)
        # End def #}}}

        def on_write(self): #{{{
            print 'WRITE'
        # End def #}}}

        def on_error(self): #{{{
            print 'ERROR'
        # End def #}}}

        def on_eof(self): #{{{
            print 'CLIENT DISCONNECTED'
        # End def #}}}
    # End class #}}}

    class EchoEvent(SocketEvent): #{{{
        __slots__ = ()
        def callback(self): #{{{
            s = self.socket
            MAXLINE = 4096
            data = s.recv(MAXLINE)
            if not data:
                print 'Connection closed by peer'
                return
            print 'received from client: %s' %data
            if data.strip() == 'quit':
                self.event_loop.end_loop()
                return
            s.send(data)
            print 'writing to client: %s' %data
            self.event_loop.register(self)
        # End def #}}}
    # End class #}}}

    class AcceptConnection(SocketConnected): #{{{
        __slots__ = ()
        def callback(self, sckt, addr): #{{{
            self.event_loop.register(BufferedEchoEvent(sckt))
#            self.event_loop.register(EchoEvent(sckt))
            print 'Accepted connection from %s' %str(addr)
        # End def #}}}
    # End class #}}}

    class CreateEchoSocket(CreateSocket): #{{{
        __slots__ = ()
        def callback(self, listen_sock): #{{{
            ac = AcceptConnection(listen_sock)
            ac.persists = True
            self.event_loop.register(ac)
        # End def #}}}
    # End class #}}}
    s = CreateEchoSocket(0, HOST, SERVER_PORT)
    evloop = EventLoop()
    evloop.register_signal(2)
    evloop.register_signal(1)
    evloop.register(s)
    evloop.loop(count=None)
    print 'Cleanup...'
    evloop.close()
    print 'DONE'
# End def #}}}

if __name__ == '__main__':
    print 'PID: %i' %os.getpid()
    print 'LIBRARY: %s' %str(libevent)
#    test_hello()
    test_echo('localhost', 5555)
