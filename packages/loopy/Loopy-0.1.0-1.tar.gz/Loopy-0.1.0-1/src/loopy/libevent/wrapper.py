# Module: loopy.libevent.wrapper
# File: wrapper.py
# Copyright (C) 2007 Ariel De Ocampo arieldeocampo@gmail.com
#
# This module is part of the loopy project and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from ctypes import *
from ctypes.util import find_library
from types import ClassType as classobj

import socket
from decimal import Decimal, getcontext

SIZE_T = c_ulong

EV_TIMEOUT = 1
EV_READ = 2
EV_WRITE = 4
EV_SIGNAL = 8
EV_PERSIST = 16

EVLOOP_ONCE = 1
EVLOOP_NONBLOCK = 2

EVBUFFER_READ = 1
EVBUFFER_WRITE = 2
EVBUFFER_EOF = 16
EVBUFFER_ERROR = 32
EVBUFFER_TIMEOUT = 64

libevent = CDLL(find_library('event'))

def tailq_entry(eltype, name): #{{{
    anon = classobj(name, (Structure,), {})
    anon._fields_ = [("tqe_next", POINTER(eltype)),
                     ("tqe_prev", POINTER(POINTER(eltype)))]
    return anon
# End def #}}}

def rb_entry(eltype, name): #{{{
    anon = classobj(name, (Structure,), {})
    anon._fields_ = [('rbe_left', POINTER(eltype)), 
                     ('rbe_right', POINTER(eltype)), 
                     ('rbe_parent', POINTER(eltype)), 
                     ('rbe_color', c_int)]
    return anon
# End def #}}}

class EVENT_BASE(Structure): #{{{
    pass
# End class #}}}

class TIMEVAL(Structure): #{{{
    _fields_ = [('tv_sec', c_long), ('tv_usec', c_long)]
# End class #}}}

class EVENT(Structure): #{{{
    pass
# End class #}}}

EVCB = CFUNCTYPE(None, c_int, c_short, c_void_p)
EVENT._fields_ = [('ev_next', tailq_entry(EVENT, 'ev_next')), 
                  ('ev_active_next', tailq_entry(EVENT, 'ev_active_next')),
                  ('ev_signal_next', tailq_entry(EVENT, 'ev_signal_next')),
                  ('ev_timeout_node', rb_entry(EVENT, 'ev_timeout_node')),
                  ('ev_base', POINTER(EVENT_BASE)),
                  ('ev_fd', c_int),
                  ('ev_events', c_short),
                  ('ev_ncalls', c_short),
                  ('ev_pncalls', POINTER(c_short)),
                  ('ev_timeout', TIMEVAL),
                  ('ev_pri', c_int),
                  ('ev_callback', EVCB),
                  ('ev_arg', c_void_p),
                  ('ev_res', c_int),
                  ('ev_flags', c_int)]

class EVBUFFER(Structure): #{{{
    pass
# End class #}}}

EVBUFFER._fields_ = [('buffer', POINTER(c_ubyte)),
                     ('orig_buffer', POINTER(c_ubyte)),
                     ('misalign', SIZE_T),
                     ('totallen', SIZE_T),
                     ('off', SIZE_T),
                     ('cb', CFUNCTYPE(c_int, POINTER(EVBUFFER), SIZE_T, SIZE_T, c_void_p)), 
                     ('cbarg', c_void_p)]

class EVENT_WATERMARK(Structure): #{{{
    _fields_ = [('low', SIZE_T), ('high', SIZE_T)]
# End class #}}}

class BUFFEREVENT(Structure): #{{{
    pass
# End class #}}}

EVBUFFERCB = CFUNCTYPE(None, POINTER(BUFFEREVENT), c_void_p)
EVERRORCB = CFUNCTYPE(None, POINTER(BUFFEREVENT), c_short, c_void_p)

BUFFEREVENT._fields_ = [('ev_read', EVENT), 
                        ('ev_write', EVENT),
                        ('input', POINTER(EVBUFFER)),
                        ('output', POINTER(EVBUFFER)),
                        ('wm_read', EVENT_WATERMARK),
                        ('wm_write', EVENT_WATERMARK),
                        ('readcb', EVBUFFERCB),
                        ('writecb', EVBUFFERCB),
                        ('errorcb', EVERRORCB),
                        ('cbarg', c_void_p),
                        ('timeout_read', c_int),
                        ('timeout_write', c_int),
                        ('enabled', c_short)]

class BUFFEREVENT_CLIENT(Structure): #{{{
    _fields_ = [('ev_fd', c_int), 
                ('buf_ev', POINTER(BUFFEREVENT)),
                ('timeout_read', c_int),
                ('timeout_write', c_int),
                ('readcb_ptr', EVBUFFERCB),
                ('writecb_ptr', EVBUFFERCB),
                ('errorcb_ptr', EVERRORCB)]
# End class #}}}

class EVENT_CLIENT(Structure): #{{{
    _fields_ = [('ev', EVENT), ('timeout', c_int)]
# End class #}}}

EVENT_SIGCB = c_void_p.in_dll(libevent, 'event_sigcb')
EVENT_GOTSIG = c_int.in_dll(libevent, 'event_gotsig')
ERRNO = c_int.in_dll(libevent, 'errno')

def flags_to_str(flags): #{{{
    output = []
    add_str = output.append
    possible = ('EV_TIMEOUT', 'EV_READ', 'EV_WRITE', 'EV_SIGNAL', 'EV_PERSIST')
    for p in possible:
        if flags & globals()[p]:
            add_str(p)
    return ' '.join(output)
# End def #}}}

def setnonblock(sock): #{{{
    sock.setblocking(False)
    to = sock.gettimeout()
    if to != 0.0:
        raise socket.error('Failed to set server to non-blocking: %s' %str(to))
# End def #}}}

def to_timeval(sec): #{{{
    if sec is None:
        return sec
    full = Decimal(str(sec)).quantize(Decimal('.000000'))
    sec = full.quantize(Decimal('1.'))
    usec = full - sec
    usec = usec * Decimal('1000000')
    return TIMEVAL(tv_sec=c_int(int(full)), 
                    tv_usec=c_int(int(usec)))
# End def #}}}

_glob = globals()
__all__ = [n for n in _glob.keys() if isinstance(_glob[n], int)]
__all__ += ['libevent', 'TIMEVAL', 'EVENT', 'EVCB', 'EVBUFFER', 'BUFFEREVENT',
            'EVBUFFERCB', 'EVERRORCB', 'BUFFEREVENT_CLIENT', 'EVENT_CLIENT',
            'EVENT_SIGCB', 'EVENT_GOTSIG', 'ERRNO', 'flags_to_str', 'setnonblock',
            'to_timeval']
del _glob
