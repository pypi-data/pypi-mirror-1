# Module: template
# File: template.py
# Copyright (C) 2007 Ariel De Ocampo arieldeocampo@gmail.com
#
# This module is part of the loopy project and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from types import (FunctionType as function, BuiltinFunctionType as bfunction, 
        MethodType as method, BuiltinMethodType as bmethod, ModuleType, ClassType)

# Provide facility to clear lists similar to dict.clear
def clearlist(listobj): #{{{
    while listobj:
        listobj.pop()
# End def #}}}

def ismagicname(obj): #{{{
    return isinstance(obj, basestring) and obj.startswith('__') and obj.endswith('__')
# End def #}}}

def isclass(obj): #{{{
    return isinstance(obj, ClassType) or hasattr(obj, '__bases__')
# End def #}}}

def iscallable(obj): #{{{
    return bool(isinstance(obj, (function, bfunction, method, bmethod)) or
                isclass(obj) or 
                hasattr(obj, '__call__'))
# End def #}}}
