# Module: template
# File: template.py
# Copyright (C) 2006 Ariel De Ocampo arieldeocampo@gmail.com
#
# This module is part of the <WHAT-HAVE-YOU> project and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from types import FunctionType as function
from loopy.misc import ismagicname

__all__ = ('Singleton', 'Namespace', 'ACLNamespace')

class SingletonType(type): #{{{
    def __call__(cls, *args, **kwargs): #{{{
        return cls
    # End def #}}}

    def __setattr__(cls, k, v): #{{{
        if isinstance(v, function) and not isinstance(v, (staticmethod, classmethod)):
            v = classmethod(v)
        super(SingletonType, cls).__setattr__(k, v)
    # End def #}}}

    def __new__(stcls, classname, bases, clsdict): #{{{
        for k, v in clsdict.iteritems():
            if isinstance(v, function) and not isinstance(v, (staticmethod, classmethod)):
                clsdict[k] = classmethod(v)
        return super(SingletonType, stcls).__new__(stcls, classname, bases, clsdict)
    # End def #}}}
# End class #}}}

class Singleton(object): #{{{
    __metaclass__ = SingletonType
# End class #}}}

class NamespaceType(SingletonType): #{{{
    def __setattr__(cls, k, v): #{{{
        if isinstance(v, function) and not isinstance(v, (staticmethod, classmethod)):
            v = staticmethod(v)
        super(SingletonType, cls).__setattr__(k, v)
    # End def #}}}

    def __new__(nscls, classname, bases, clsdict): #{{{
        for k, v in clsdict.iteritems():
            if isinstance(v, function) and not isinstance(v, (staticmethod, classmethod)):
                clsdict[k] = staticmethod(v)
        return type.__new__(nscls, classname, bases, clsdict)
    # End def #}}}
# End class #}}}

class Namespace(object): #{{{
    __metaclass__ = NamespaceType
# End class #}}}

class ACLNamespaceType(NamespaceType): #{{{
    def __setattr__(cls, k, v): #{{{
        type.__setattr__(cls, k, v)
    # End def #}}}

    def __new__(ronst, classname, bases, clsdict): #{{{
        vals, pop = {}, clsdict.pop
        getvals, setvals, delvals = vals.__getitem__, vals.__setitem__, vals.__delitem__
        read = frozenset(clsdict.pop('__getprop__', ()))
        write = frozenset(clsdict.pop('__setprop__', ()))
        delete = frozenset(clsdict.pop('__delprop__', ()))
        setattr(ronst, '__getprop__', property(lambda s: read))
        setattr(ronst, '__setprop__', property(lambda s: write))
        setattr(ronst, '__delprop__', property(lambda s: delete))
        def mkread(k): #{{{
            if (not read and not write and not delete) or k in read:
                def _(s): #{{{
                    try:
                        return vals[k]
                    except KeyError:
                        raise AttributeError("'%s' object has no attribute '%s'" %(s.__class__.__name__, k))
                # End def #}}}
                return _
        # End def #}}}
        def mkwrite(k, val): #{{{
            if k in write:
                def _(s, v): #{{{
                    vals[k] = v
                # End def #}}}
                return _
        # End def #}}}
        def mkdel(k): #{{{
            if k in delete:
                def _(s): #{{{
                    try:
                        del vals[k]
                    except KeyError:
                        raise AttributeError("'%s' object has no attribute '%s'" %(s.__class__.__name__, k))
                # End def #}}}
                return _
        # End def #}}}
        for k, v in clsdict.items():
            if not ismagicname(k):
                vals[k] = pop(k)
                args = [mkread(k), mkwrite(k, v), mkdel(k)]
                setattr(ronst, k, property(*args))
        return type.__new__(ronst, classname, bases, clsdict)
    # End def #}}}
# End class #}}}

class ACLNamespace(Namespace): #{{{
    __metaclass__ = ACLNamespaceType
# End class #}}}
