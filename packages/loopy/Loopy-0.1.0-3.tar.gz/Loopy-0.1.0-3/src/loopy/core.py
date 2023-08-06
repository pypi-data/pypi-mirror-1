# Module: template
# File: template.py
# Copyright (C) 2006 Ariel De Ocampo arieldeocampo@gmail.com
#
# This module is part of the loopy project and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php
from weakref import ref

from loopy.misc.decorators import property_
from loopy.misc.singleton import ACLNamespace

__all__ = ('BaseEventLoop', 'BaseEvent')

STATE_UNBOUND = 1
STATE_BOUND = 2
STATE_ACTIVE = 4
STATE_RUNNING = 8
STATE_DONE = 16
STATE_CLOSED = 32

class BaseEventLoop(object): #{{{
    def __init__(self, event_loop): #{{{
        self._events = {}
        self._event_loop = event_loop
    # End def #}}}

    def __contains__(self, event): #{{{
        return hash(event) in self._events
    # End def #}}}

    def __iter__(self): #{{{
        return self._events.itervalues()
    # End def #}}}

    def __delete__(self): #{{{
        self.close()
    # End def #}}}

    def close(self): #{{{
        self.clear()
    # End def #}}}

    def clear(self): #{{{
        E = self._events
        for ekey, ev in E.iteritems():
            ev.close()
        E.clear()
    # End def #}}}

    def loop(self, count=0): #{{{
        raise NotImplemented
    # End def #}}}

    def end_loop(self): #{{{
        raise NotImplemented
    # End def #}}}

    def hasevents(self): #{{{
        return bool(self._events)
    # End def #}}}

    def register(self, event, *args, **kwargs): #{{{
        if not isinstance(event, BaseEvent):
            raise TypeError("Expected BaseEvent object, got %s object instead" %event.__class__.__name__)
        event.state = STATE_ACTIVE
        if event in self:
            if event.persists:
                return False
        else:
            self._events[hash(event)] = event
            event.event_loop = self
        return True
    # End def #}}}

    def delete(self, event): #{{{
        old = self._events.pop(hash(event))
        old.close()
    # End def #}}}

    def isregistered(self, event): #{{{
        return event in self
    # End def #}}}

    # Properties #{{{
    event_loop = property(lambda s: s._event_loop)
    # End properties #}}}
# End class #}}}

class BaseEvent(object): #{{{
    __slots__ = ('_vars', '_event_loop', '_state', '_persists', '_has_fd')
    def __init__(self, **kw): #{{{
        self._event_loop = None
        self._vars = self._create_varstore()
        self._state = STATE_UNBOUND
        self._persists = bool(kw.get('persists', False))
        self._has_fd = bool(kw.get('has_fd', False))
    # End def #}}}

    def _create_varstore(self): #{{{
        class Variables(ACLNamespace): #{{{
            pass
        # End class #}}}
        return Variables
    # End def #}}}

    def __call__(self, *args, **kwargs): #{{{
        self.state = STATE_RUNNING
        self._on_call(*args, **kwargs)
        if self.state == STATE_RUNNING and not self.persists:
            self.state = STATE_DONE
            self.event_loop.delete(self)
    # End def #}}}

    def _on_call(self, *args, **kwargs): #{{{
        self.callback()
    # End def #}}}

    def callback(self): #{{{
        raise NotImplementedError
    # End def #}}}

    def __delete__(self): #{{{
        self.close()
    # End def #}}}

    def close(self): #{{{
        if self._state == STATE_CLOSED:
            return
        self._on_close()
        if self._has_fd:
            os.close(self.fileno)
        if self.persists:
            self._remove_persistent_event()
        self._state = STATE_CLOSED
    # End def #}}}

    def _on_close(self): #{{{
        pass
    # End def #}}}

    def _remove_persistent_event(self): #{{{
        pass
    # End def #}}}

    # Properties #{{{
    fileno = property()
    # End properties #}}}

    @property_
    def state(): #{{{
        def fget(self): #{{{
            return self._state
        # End def #}}}
        def fset(self, val): #{{{
            states = set([STATE_UNBOUND,
                          STATE_BOUND,
                          STATE_ACTIVE,
                          STATE_RUNNING,
                          STATE_DONE,
                          STATE_CLOSED])
            if val not in states:
                raise ValueError("Attempt to set invalid state")
            self._state = val
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
    def event_loop(): #{{{
        def fget(self): #{{{
            ev = self._event_loop
            if ev:
                ev = ev()
            return ev
        # End def #}}}
        def fset(self, val): #{{{
            if not isinstance(val, BaseEventLoop):
                raise TypeError("Expected BaseEventLoop, got %s object instead" %val.__class__.__name__)
            elif self._event_loop:
                raise TypeError("Cannot bind: already bound to an existing event loop")
            self._event_loop = ref(val)
            self._state = STATE_BOUND
        # End def #}}}
        return locals()
    # End def #}}}

    @property_
    def variables(): #{{{
        def fget(self): #{{{
            return self._vars
        # End def #}}}
        return locals()
    # End def #}}}
    v = variables
# End class #}}}

_glob = globals()
__all__ += tuple(n for n in _glob.keys() if isinstance(_glob[n], int))
