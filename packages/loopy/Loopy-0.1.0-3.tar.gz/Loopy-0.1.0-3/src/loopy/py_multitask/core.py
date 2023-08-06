# Module: template
# File: template.py
# Copyright (C) 2007 Ariel De Ocampo arieldeocampo@gmail.com
#
# This module is part of the ${__name__} project and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from types import GeneratorType
import sys
import collections
from copy import copy
import time, heapq

from multitask import TaskManager, _ChildTask

from loopy.core import *
from loopy.misc import clearlist, iscallable
from loopy.misc.decorators import property_


__all__ = ('TaskManagerEx', 'MultiTaskLoop', 'Task')

class TaskManagerEx(TaskManager): #{{{
    def __init__(self): #{{{
        super(TaskManagerEx, self).__init__()
        self._itercount = [0, 0]
    # End def #}}}

    def _enqueue(self, task, input=None, exc_info=()): #{{{
        if self._itercount[0] < 0:
            return
        return super(TaskManagerEx, self)._enqueue(task, input, exc_info)
    # End def #}}}

    def run_one(self, timeout=None): #{{{
        ret = True
        count, qlen = itercount = self._itercount
        if count <= 0:
            if self.has_io_waits():
                self._handle_io_waits(self._fix_run_timeout(timeout))

            if self.has_timeouts():
                self._handle_timeouts(self._fix_run_timeout(timeout))
            qlen = len(self._queue)
            if not qlen:
                return False
            clearlist(itercount)
            itercount.extend([0, qlen])

        task, input, exc_info = self._queue.popleft()
        try:
            if exc_info:
                output = task.throw(*exc_info)
            else:
                output = task.send(input)
        except StopIteration:
            if isinstance(task, _ChildTask):
                self._enqueue(task.parent, input=task.output)
        except:
            if isinstance(task, _ChildTask):
                # Propagate exception to parent
                self._enqueue(task.parent, exc_info=sys.exc_info())
            else:
                # No parent task, so just die
                raise
        else:
            self._handle_task_output(task, output)
        prev = count, qlen
        itercount[0] += 1
        count, qlen = itercount
        if not count:
            return False
        if count >= qlen:
            itercount = [0, len(self._queue)]
            ret = False
        self._itercount = itercount
        return ret
    # End def #}}}

    def run_next(self, timeout=None):
        # Run all tasks currently in the queue
        while self.run_one(timeout):
            pass

    def close(self): #{{{
        self._queue.clear()
        self._read_waits.clear() 
        self._write_waits.clear()
        self._exc_waits.clear()
        self._queue_waits.clear()
        clearlist(self._timeouts)
        ic = self._itercount
        clearlist(ic)
        ic.extend([-1, 0])
    # End def #}}}
# End class #}}}

class MultiTaskLoop(BaseEventLoop): #{{{
    def __init__(self): #{{{
        super(MultiTaskLoop, self).__init__(TaskManagerEx())
        self._count = 0
    # End def #}}}

    def hasevents(self): #{{{
        loop = self.event_loop
        cur = (loop.has_runnable() or loop.has_io_waits() or loop.has_timeouts())
        return cur or super(MultiTaskLoop, self).hasevents()
    # End def #}}}

    def loop(self, count=0): #{{{
        self._count, loop = count, self.event_loop
        if not count:
            loop.run()
        else:
            c = 1
            while c <= count:
                loop.run_one(0.0)
                c += 1
                count = self._count
    # End def #}}}

    def end_loop(self): #{{{
        self.event_loop.close()
        count = self._count
        if count:
            self._count = 0
    # End def #}}}

    def close(self): #{{{
        self.event_loop.stop()
        super(MultiTaskLoop, self).close()
    # End def #}}}

    def register(self, event, *args, **kwargs): #{{{
        if not isinstance(event, Task) and iscallable(event):
            event = Task(event)
        if not isinstance(event, Task):
            raise TypeError("Expected Task object, got %s object instead" %event.__class__.__name__)
        gen = event(*args, **kwargs)
        if not isinstance(gen, GeneratorType):
            raise TypeError("An event must be a generator")
        super(MultiTaskLoop, self).register(event)
        self.event_loop.add(gen)
    # End def #}}}
# End class #}}}

class Task(BaseEvent): #{{{
    __slots__ = ('_task', '_gen')
    def __init__(self, task=None): #{{{
        super(Task, self).__init__()
        if not task:
            task = self.callback
        elif task and not iscallable(task):
            raise TypeError("'task' must be a callable object or None: %s" %task.__class__.__name__)
        self._task = task
        self._gen = None
    # End def #}}}

    def callback(self, *args, **kwargs): #{{{
        yield
    # End def #}}}

    def __call__(self, *args, **kwargs): #{{{
        self._gen = gen = self._on_call(*args, **kwargs)
        return gen
    # End def #}}}

    def _on_call(self, *args, **kwargs): #{{{
        self.state = STATE_RUNNING
        task = self._task

        gen = task(*args, **kwargs)
        gfunc, input = lambda i: gen.next(), None
        gsend, exc_info = gen.send, sys.exc_info
        while 1:
            try:
                input = (yield gfunc(input))
            except StopIteration:
                break
            except:
                gen.throw(*exc_info())
            gfunc = gsend

        if self.state == STATE_RUNNING and not self.persists:
            self.state = STATE_DONE
            self.event_loop.delete(self)
    # End def #}}}

    def _on_close(self): #{{{
        if self.event_loop.hasevents():
            def close_gen(): #{{{
                gen = self._gen
                if gen:
                    gen.close()
                yield
             # End def #}}}
            self.event_loop.event_loop.add(close_gen())
    # End def #}}}

    @property_
    def event_loop(): #{{{
        def fget(self): #{{{
            return BaseEvent.event_loop.fget(self)
        # End def #}}}
        def fset(self, val): #{{{
            if not isinstance(val, MultiTaskLoop):
                raise TypeError("Expected MultiTaskLoop, got %s object instead" %val.__class__.__name__)
            BaseEvent.event_loop.fset(self, val)
        # End def #}}}
        return locals()
    # End def #}}}
# End class #}}}
