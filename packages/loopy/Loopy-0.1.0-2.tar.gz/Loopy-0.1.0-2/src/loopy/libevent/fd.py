# Module: loopy.libevent.fd
# File: fd.py
# Copyright (C) 2007 Ariel De Ocampo arieldeocampo@gmail.com
#
# This module is part of the loopy project and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from ctypes import *

import socket
import os
from operator import attrgetter

from loopy.libevent.wrapper import *
from loopy.libevent.core import Event, TimeoutEvent
from loopy.misc.decorators import property_

__all__ = ('FileDescriptorEvent', 'FIFOEvent', 'SocketEvent')

class FileDescriptorEvent(Event): #{{{
    __slots__ = ()
# End class #}}}

class FIFOEvent(FileDescriptorEvent): #{{{
    __slots__ = ()
# End class #}}}

class SocketEvent(FileDescriptorEvent): #{{{
    __slots__ = ('_socket', '_auto_close')
    def __init__(self, sckt, timeout=None): #{{{
        if not isinstance(sckt, socket.SocketType):
            raise TypeError('Expected SocketType object, got %s object instead' %sckt.__class__.__name__)
        super(SocketEvent, self).__init__(timeout=timeout, flags=EV_READ)
        self._socket = sckt
        self._auto_close = True
        self._event.ev.ev_fd = sckt.fileno()
    # End def #}}}

    # Super here goes directly to Event.close
    def close(self): #{{{
        super(SocketEvent, self).close()
        if self.auto_close:
            self._socket.close()
    # End def #}}}

    @property_
    def socket(): #{{{
        def fget(self): #{{{
            return self._socket
        # End def #}}}
        return locals()
    # End def #}}}

    @property_
    def auto_close(): #{{{
        def fget(self): #{{{
            return self._auto_close
        # End def #}}}
        def fset(self, val): #{{{
            self._auto_close = bool(val)
        # End def #}}}
        return locals()
    # End def #}}}
# End class #}}}
