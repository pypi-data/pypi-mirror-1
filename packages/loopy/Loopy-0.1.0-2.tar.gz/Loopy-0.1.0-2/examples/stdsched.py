# Module: template
# File: template.py
# Copyright (C) 2007 Ariel De Ocampo arieldeocampo@gmail.com
#
# This module is part of the ${__name__} project and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php
from time import time

from loopy.stdsched.core import *

class print_time(SchedEvent): #{{{
    __slots__ = ()
    def callback(self): #{{{
        print 'From print_time', time()
    # End def #}}}
# End class #}}}

class hello(SchedEvent): #{{{
    __slots__ = ()
    def __init__(self, **kw): #{{{
        super(hello, self).__init__(**kw)
        self.v.count = 0
    # End def #}}}
    def callback(self): #{{{
        self.delay = 0
        count = self.v.count
        print 'Hello world:', count
        count += 1
        if count < 5:
            self.event_loop.register(self)
        self.v.count = count
    # End def #}}}
# End class #}}}

if __name__ == '__main__':
    print time()
    evloop = SchedLoop()
    evloop.register(print_time(delay=1))
    evloop.register(print_time(delay=3))
    evloop.register(hello(delay=4))
    evloop.loop()
    print time()
