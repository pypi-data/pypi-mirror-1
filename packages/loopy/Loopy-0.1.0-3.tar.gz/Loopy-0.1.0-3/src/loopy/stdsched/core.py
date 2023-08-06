# Module: template
# File: template.py
# Copyright (C) 2007 Ariel De Ocampo arieldeocampo@gmail.com
#
# This module is part of the ${__name__} project and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from time import time, sleep
from sched import scheduler
import heapq

from loopy.core import *
from loopy.misc.decorators import property_

__all__ = ('SchedEx', 'SchedLoop', 'SchedEvent')

class SchedEx(scheduler): #{{{
    def clear(self): #{{{
        pop = heapq.heappop
        while q:
            pop(q)
    # End def #}}}

    def run(self): #{{{
        q = self.queue
        delayfunc = self.delayfunc
        timefunc = self.timefunc
        while q:
            time, priority, action, argument = checked_event = q[0]
            now = timefunc()
            if now < time:
                delayfunc(time - now)
            else:
                self._run_next(q, delayfunc, checked_event, action, argument)
    # End def #}}}

    def _run_next(self, q, delayfunc, checked_event, action, argument): #{{{
        if self.empty():
            return
        event = heapq.heappop(q)
        # Verify that the event was not removed or altered
        # by another thread after we last looked at q[0].
        if event is checked_event:
            void = action(*argument)
            delayfunc(0)   # Let other threads run
        else:
            heapq.heappush(event)
    # End def #}}}

    def run_next(self): #{{{
        q = self.queue
        delayfunc = self.delayfunc
        _, _, action, argument = checked_event = q[0]
        self._run_next(q, delayfunc, checked_event, action, argument)
    # End def #}}}
# End class #}}}

class SchedLoop(BaseEventLoop): #{{{
    def __init__(self, time=time, sleep=sleep): #{{{
        self._count = 0
        self._queue = None
        super(SchedLoop, self).__init__(SchedEx(time, sleep))
    # End def #}}}

    def loop(self, count=0): #{{{
        self._count = count
        event_loop = self.event_loop
        if self._queue:
            event_loop.queue = self._queue
            self._queue = None
        if not count:
            event_loop.run()
        else:
            c = 1
            while c <= count:
                event_loop.run_next()
                c += 1
                count = self._count
    # End def #}}}

    def end_loop(self): #{{{
        self._count = 0
        event_loop = self.event_loop
        self._queue = event_loop.queue
        event_loop.clear()
    # End def #}}}

    def clear(self): #{{{
        self._count = 0
        self._queue = None
        self.event_loop.clear()
    # End def #}}}

    def hasevents(self): #{{{
        return not self.event_loop.empty()
    # End def #}}}

    def register(self, event, *args, **kwargs): #{{{
        if not isinstance(event, SchedEvent):
            raise TypeError("Expected SchedEvent object, got %s object instead" %event.__class__.__name__)
        delay, priority = event.delay, event.priority
        if not super(SchedLoop, self).register(event):
            return False
        self.event_loop.enter(delay, priority, event, args)
        return True
    # End def #}}}

    def isregistered(self, event): #{{{
        return event in self
    # End def #}}}
# End class #}}}

class SchedEvent(BaseEvent): #{{{
    __slots__ = ('_timeval',)
    def __init__(self, **kw): #{{{
        delay = self._format_delay(kw.pop('delay', 1))
        priority = self._format_priority(kw.pop('priority', 1))
        super(SchedEvent, self).__init__(**kw)
        self._timeval = [delay, priority]
    # End def #}}}

    def callback(self, *args): #{{{
        raise NotImplementedError
    # End def #}}}

#    def _on_close(self): #{{{
##        self.event_loop.delete(self)
#        pass
#    # End def #}}}

    @property_
    def event_loop(): #{{{
        def fget(self): #{{{
            return BaseEvent.event_loop.fget(self)
        # End def #}}}
        def fset(self, val): #{{{
            if not isinstance(val, SchedLoop):
                raise TypeError("Expected SchedLoop, got %s object instead" %val.__class__.__name__)
            BaseEvent.event_loop.fset(self, val)
        # End def #}}}
        return locals()
    # End def #}}}

    def _format_delay(self, val): #{{{
        return int(val)
    # End def #}}}

    def _format_priority(self, val): #{{{
        return int(val)
    # End def #}}}

    @property_
    def delay(): #{{{
        def fget(self): #{{{
            return self._timeval[0]
        # End def #}}}
        def fset(self, val): #{{{
            self._timeval[0] = self._format_delay(val)
        # End def #}}}
        return locals()
    # End def #}}}

    @property_
    def priority(): #{{{
        def fget(self): #{{{
            return self._timeval[1]
        # End def #}}}
        def fset(self, val): #{{{
            self._timeval[1] = self._format_priority(val)
        # End def #}}}
        return locals()
    # End def #}}}
# End class #}}}
