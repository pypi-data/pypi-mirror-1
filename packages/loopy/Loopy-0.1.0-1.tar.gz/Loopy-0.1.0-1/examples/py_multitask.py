# Module: template
# File: template.py
# Copyright (C) 2007 Ariel De Ocampo arieldeocampo@gmail.com
#
# This module is part of the loopy project and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from loopy.py_multitask.core import *
from multitask import *
from select import error as selecterr

if __name__ == '__main__':
    class printer(Task): #{{{
        def callback(self, name): #{{{
            for i in xrange(1, 4):
                if i == 2 and name == 'first':
                    print 'REMOVING EVENT:', name
                    self.event_loop.delete(self)
#                    print 'ENDING LOOP...'
#                    self.event_loop.end_loop()
                print '%s:\t%d' % (name, i)
                yield
        # End def #}}}
    # End class #}}}

    queue = Queue()

    def receiver():
        print 'receiver started'
        print 'receiver received: %s' % (yield queue.get())
        print 'receiver finished'

    def sender():
        print 'sender started'
        yield queue.put('from sender')
        print 'sender finished'

    def bad_descriptor():
        print 'bad_descriptor running'
        try:
            yield readable(12)
        except selecterr, err:
            print 'exception in bad_descriptor', str(err)

    def sleeper():
        print 'sleeper started'
        yield sleep(1)
        print 'sleeper finished'

    def timeout_immediately():
        print 'timeout_immediately running'
        try:
            yield Queue().get(timeout=0)
        except Timeout:
            print 'timeout_immediately timed out'

    loop = MultiTaskLoop()
    register = loop.register
    register(printer(), 'first')
    register(printer(), 'second')
    register(printer(), 'third')

    register(receiver)
    register(bad_descriptor)
    register(sender)
    register(sleeper)
    register(timeout_immediately)
    loop.loop()
