# Module: template
# File: template.py
# Copyright (C) 2006 Ariel De Ocampo arieldeocampo@gmail.com
#
# This module is part of the <WHAT-HAVE-YOU> project and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

import unittest
from smanstal.tests import addtest, mksuite

import sys
from os.path import abspath, sep, isdir, join, dirname, basename

basepackage = None

def set_private_packages(basedir): #{{{
    basedir = abspath(basedir)
    if not isdir(basedir):
        raise OSError("No such directory: '%s'" %basedir)
    paths = (['util', 'python'], ['tests', 'alltests'], ['pkg', None])
    syspaths = [join(basedir, *p[:-1]) for p in paths]
    oldpath = sys.path
    sys.path = syspaths + sys.path
    sysmod = sys.modules
    for p in paths:
        name = p[-1]
        if not name:
            continue
        sysmod['/%s/_private/%s' %(basepackage, '/'.join(p))] = __import__(name)
        sysmod.pop(name, None)
    sys.path = oldpath
# End def #}}}

# Create suite function for this package
#suite = addtest(__file__)(mksuite(__file__))

def init(): #{{{
    basedir = abspath(__file__)
    basedir = join(sep, *dirname(basedir).split(sep)[1:-1])
    global basepackage
    if not basepackage:
        basepackage = basename(basedir)
    set_private_packages(basedir)
# End def #}}}

if __name__ == '__main__':
    # Set up environment
    init()
    alltests = __import__('/%s/_private/tests/alltests' %basepackage)
    python = __import__('/%s/_private/util/python' %basepackage)
    app_version = __import__('/%s/_private/util/python.version' %basepackage)

    alltests = alltests.__file__
    suite = addtest(alltests)(mksuite(alltests))

    # Run the tests
    unittest.TextTestRunner(verbosity=2).run(suite())
