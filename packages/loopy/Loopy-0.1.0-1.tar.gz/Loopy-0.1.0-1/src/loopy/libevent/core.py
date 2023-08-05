# Module: loop.libevent.core
# File: core.py
# Copyright (C) 2007 Ariel De Ocampo arieldeocampo@gmail.com
#
# This module is part of the loopy project and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from ctypes import *
from weakref import ref

import os
from operator import attrgetter

from loopy.core import *
from loopy.libevent.wrapper import *
from loopy.misc.decorators import property_

__all__ = ('EventLoop', 'Event', 'BufferedEvent', 'SignalEvent', 'TimeoutEvent')

class EventLoop(BaseEventLoop): #{{{
    def __init__(self): #{{{
        super(EventLoop, self).__init__(libevent.event_init())
        self._END_DISPATCH_PTR_ = CFUNCTYPE(c_int)(self._end_dispatch)
        self._count = 0
    # End def #}}}

    def __contains__(self, key): #{{{
        if isinstance(key, Event):
            key = hash(key)
        return super(EventLoop, self).__contains__(key)
    # End def #}}}

    def _end_dispatch(self): #{{{
        return -1
    # End def #}}}

    def loop(self, count=0): #{{{
        self._count = count
        if count == None:
            libevent.event_base_dispatch(self._event_loop)
        elif not count:
            libevent.event_base_loop(self._event_loop)
        else:
            c = 1
            while c <= count:
                libevent.event_base_loop(self._event_loop, EVLOOP_ONCE|EVLOOP_NONBLOCK)
                c += 1
                count = self._count
    # End def #}}}

    def end_loop(self, timeout=None): #{{{
        count = self._count
        if count == None:
            EVENT_SIGCB.value = cast(self._END_DISPATCH_PTR_, c_void_p).value
            EVENT_GOTSIG.value = -1
        elif not count:
            libevent.event_base_loopexit(self._event_loop, to_timeval(timeout))
        elif count:
            self._count = 0
    # End def #}}}

    def close(self): #{{{
        EVENT_SIGCB.value = None
        super(EventLoop, self).close()
    # End def #}}}

    def hasevents(self): #{{{
        pass
    # End def #}}}

    def register(self, event, *args, **kwargs): #{{{
        if not isinstance(event, Event):
            raise TypeError("Expected Event object, got %s object instead" %event.__class__.__name__)
        elif isinstance(event, BufferedEvent):
            return self.register_buffered(event)
        event_map = self._events
        client = event._event
        ev = client.ev
        cur_p = pointer(ev)
        key = hash(event)
        event.state = STATE_ACTIVE
        if event in self:
            if event.persists:
                return False
        else:
            self._events[key] = event
            event.event_loop = self
            libevent.event_set(cur_p, ev.ev_fd, ev.ev_flags, ev.ev_callback, None)
            libevent.event_base_set(self._event_loop, cur_p)

        to_p = None
        if client.timeout:
            to_p = pointer(ev.ev_timeout)
        if libevent.event_add(cur_p, to_p) == -1:
            raise Exception('ERROR!!! EVENT_ADD!!!')
        return True
    # End def #}}}

    def register_signal(self, signal): #{{{
        if isinstance(signal, int):
            signal = SignalEvent(signal)
        if not isinstance(signal, SignalEvent):
            raise TypeError("Expected SignalEvent object, got %s object instead" %signal.__class__.__name__)
        return self.register(signal)
    # End def #}}}

    def register_buffered(self, event): #{{{
        if not isinstance(event, Event):
            raise TypeError("Expected Event object, got %s object instead" %event.__class__.__name__)
        elif not isinstance(event, BufferedEvent):
            raise TypeError("Expected BufferedEvent object, got %s object instead" %event.__class__.__name__)
        event_map = self._events
        client = event.event
        key = hash(event)
        event.state = STATE_ACTIVE
        if event in self:
            return False
        else:
            self._events[key] = event
            event.event_loop = self

            # Create the buffered event
            args = attrgetter('readcb_ptr', 'writecb_ptr', 'errorcb_ptr')(client) + (None,)
            client.buf_ev = buf_ev = cast(libevent.bufferevent_new(event.fileno, *args), POINTER(BUFFEREVENT))
            if libevent.bufferevent_base_set(self._event_loop, buf_ev) == -1:
                raise Exception('ERROR!!! BUFFEREVENT_BASE_SET!!!')
            to_read, to_write = attrgetter('timeout_read', 'timeout_write')(client)
            if to_read or to_write:
                libevent.bufferevent_settimeout(buf_ev, to_read, to_write)

            # We have to enable it before our callbacks will be called
            if libevent.bufferevent_enable(buf_ev, EV_READ) == -1:
                raise Exception('ERROR!!! BUFFEREVENT_ENABLE!!!')
        return True
    # End def #}}}

#    def delete(self, event): #{{{
#        super(EventLoop, self).delete(event)
#        event.close()
#    # End def #}}}
# End class #}}}

class Event(BaseEvent): #{{{
    __slots__ = ('_event',)
    def __init__(self, **kw): #{{{
        timeout = kw.pop('timeout', None)
        flags = kw.pop('flags', EV_TIMEOUT)
        super(Event, self).__init__(**kw)
        to_val = to_timeval(timeout)
        ev = EVENT(ev_flags=c_int(flags),
                    ev_fd=c_int(0),
                    ev_callback=EVCB(self.__call__))
        client = EVENT_CLIENT(ev=ev, timeout=0)
        if to_val:
            ev.ev_timeout = to_val
            client.timeout = 1
        self._event = client
        self._persists = bool(flags & EV_PERSIST)
    # End def #}}}

    def _on_close(self): #{{{
        pass
    # End def #}}}

    def repeat(self): #{{{
        raise NotImplementedError
    # End def #}}}

    def _remove_persistent_event(self): #{{{
        libevent.event_del(pointer(self.event))
    # End def #}}}

    @property_
    def fileno(): #{{{
        def fget(self): #{{{
            return self.event.ev_fd
        # End def #}}}
        return locals()
    # End def #}}}

    @property_
    def flags(): #{{{
        def fget(self): #{{{
            return self.event.ev_flags
        # End def #}}}
        return locals()
    # End def #}}}

    @property_
    def persists(): #{{{
        def fget(self): #{{{
            return self._persists
        # End def #}}}
        def fset(self, val): #{{{
            cur = self.event.ev_flags
            if val:
                cur |= EV_PERSIST
            else:
                cur ^= EV_PERSIST
            self.event.ev_flags = c_int(cur)
            self._persists = bool(val)
        # End def #}}}
        return locals()
    # End def #}}}

    @property_
    def readable(): #{{{
        def fget(self): #{{{
            return bool(self.event.ev_flags & EV_READ)
        # End def #}}}
        def fset(self, val): #{{{
            cur = self.event.ev_flags
            if val:
                cur |= EV_READ
            else:
                cur ^= EV_READ
            self.event.ev_flags = c_int(cur)
        # End def #}}}
        return locals()
    # End def #}}}

    @property_
    def writable(): #{{{
        def fget(self): #{{{
            return bool(self.event.ev_flags & EV_WRITE)
        # End def #}}}
        def fset(self, val): #{{{
            cur = self.event.ev_flags
            if val:
                cur |= EV_WRITE
            else:
                cur ^= EV_WRITE
            self.event.ev_flags = c_int(cur)
        # End def #}}}
        return locals()
    # End def #}}}

    @property_
    def timed(): #{{{
        def fget(self): #{{{
            return bool(self.event.ev_flags & EV_TIMEOUT)
        # End def #}}}
        def fset(self, val): #{{{
            cur = self.event.ev_flags
            if val:
                cur |= EV_TIMEOUT
            else:
                cur ^= EV_TIMEOUT
            self.event.ev_flags = c_int(cur)
        # End def #}}}
        return locals()
    # End def #}}}

    @property_
    def event(): #{{{
        def fget(self): #{{{
            return self._event.ev
        # End def #}}}
        return locals()
    # End def #}}}

    @property_
    def event_loop(): #{{{
        def fget(self): #{{{
            return BaseEvent.event_loop.fget(self)
        # End def #}}}
        def fset(self, val): #{{{
            if not isinstance(val, EventLoop):
                raise TypeError("Expected EventLoop, got %s object instead" %val.__class__.__name__)
            BaseEvent.event_loop.fset(self, val)
        # End def #}}}
        return locals()
    # End def #}}}

# End class #}}}

class BufferedEvent(object): #{{{
    __slots__ = ()
    def __init__(self, *args, **kwargs): #{{{
        super(BufferedEvent, self).__init__(*args, **kwargs)
        fd = self._event.ev.ev_fd
        to_read = int(kwargs.get('timeout_read', 0))
        to_write = int(kwargs.get('timeout_write', 0))
        if to_read < 0 or to_write < 0:
            raise ValueError("timeout values must be >= 0")
        bev = BUFFEREVENT_CLIENT(ev_fd=fd, timeout_read=to_read, timeout_write=to_write,
                                 readcb_ptr=EVBUFFERCB(self.__readcb__),
                                 writecb_ptr=EVBUFFERCB(self.__writecb__),
                                 errorcb_ptr=EVERRORCB(self.__errorcb__))
        self._event = bev
        self._persists = True
    # End def #}}}

    def _on_close(self): #{{{
        ev = self.event.buf_ev
        libevent.bufferevent_free(ev)
        self._persists = False
    # End def #}}}

    def write(self, data): #{{{
        bev = self.event.buf_ev
        if libevent.bufferevent_enable(bev, EV_WRITE) == -1:
            raise Exception('ERROR!!! BUFFEREVENT_ENABLE WRITE!!! WRITE!!!')
        evbuf = cast(libevent.evbuffer_new(), POINTER(EVBUFFER))
        libevent.evbuffer_add(evbuf, cast(data, c_char_p), len(data))
        libevent.evbuffer_drain(bev.contents.input, bev.contents.input.contents.off)
        libevent.bufferevent_write_buffer(bev, evbuf)
        libevent.evbuffer_free(evbuf)
    # End def #}}}

    def on_read(self): #{{{
        raise NotImplementedError("on_read callback not implemented")
    # End def #}}}

    def on_write(self): #{{{
        raise NotImplementedError("on_write callback not implemented")
    # End def #}}}

    def on_error(self): #{{{
        raise NotImplementedError("on_error callback not implemented")
    # End def #}}}

    def on_eof(self): #{{{
        raise NotImplementedError("on_eof callback not implemented")
    # End def #}}}

    def __readcb__(self, bev, arg): #{{{
        self.state = STATE_RUNNING
        self.on_read()
        self.state = STATE_ACTIVE
    # End def #}}}

    def __writecb__(self, bev, arg): #{{{
        self.state = STATE_RUNNING
        self.on_write()
        bev = self.event.buf_ev
        if libevent.bufferevent_disable(bev, EV_WRITE) == -1:
            raise Exception('ERROR!!! BUFFEREVENT_DISABLE WRITE!!! WRITE_CALLBACK!!!')
        self.state = STATE_ACTIVE
    # End def #}}}

    def __errorcb__(self, bev, what, arg): #{{{
        self.state = STATE_RUNNING
        if what & EVBUFFER_EOF:
            self.on_eof()
        else:
            self.on_error()
        self.state = STATE_DONE
        self.event_loop.delete(self)
    # End def #}}}

    @property_
    def flags(): #{{{
        def fget(self): #{{{
            return EV_READ | EV_WRITE | EV_PERSIST
        # End def #}}}
        return locals()
    # End def #}}}

    @property_
    def persists(): #{{{
        def fget(self): #{{{
            return self._persists
        # End def #}}}
        return locals()
    # End def #}}}

    @property_
    def readable(): #{{{
        def fget(self): #{{{
            return True
        # End def #}}}
        return locals()
    # End def #}}}

    @property_
    def writable(): #{{{
        def fget(self): #{{{
            return True
        # End def #}}}
        return locals()
    # End def #}}}

    @property_
    def timed(): #{{{
        def fget(self): #{{{
            return False
        # End def #}}}
        return locals()
    # End def #}}}

    @property_
    def event(): #{{{
        def fget(self): #{{{
            return self._event
        # End def #}}}
        return locals()
    # End def #}}}

    @property_
    def read_buffer(): #{{{
        def fget(self): #{{{
            buf_ev = self.event.buf_ev.contents.input.contents
            len = buf_ev.off
            ret = cast(buf_ev.buffer, c_char_p).value[:len]
            return ret
        # End def #}}}
        return locals()
    # End def #}}}

    @property_
    def write_buffer(): #{{{
        def fget(self): #{{{
            buf_ev = self.event.buf_ev.contents.output.contents
            len = buf_ev.off
            ret = cast(buf_ev.buffer, c_char_p).value[:len]
            return ret
        # End def #}}}
        return locals()
    # End def #}}}
# End class #}}}

class SignalEvent(Event): #{{{
    __slots__ = ()
    def __init__(self, signal, timeout=None): #{{{
        super(SignalEvent, self).__init__(timeout=timeout, flags=EV_SIGNAL|EV_PERSIST)
        self.event.ev_fd = signal
    # End def #}}}

    def callback(self): #{{{
#        self.event_loop.delete(self)
        self.event_loop.end_loop()
    # End def #}}}

    @property_
    def signal(): #{{{
        def fget(self): #{{{
            return self.event.ev_fd
        # End def #}}}
        return locals()
    # End def #}}}
# End class #}}}

class TimeoutEvent(Event): #{{{
    __slots__ = ()
    def __init__(self, timeout=0): #{{{
        super(TimeoutEvent, self).__init__(timeout=timeout, flags=EV_TIMEOUT)
    # End def #}}}
# End class #}}}

