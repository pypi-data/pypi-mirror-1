# Module: template
# File: template.py
# Copyright (C) 2006 Ariel De Ocampo arieldeocampo@gmail.com
#
# This module is part of the <WHAT-HAVE-YOU> project and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

import unittest
from smanstal.tests import BaseUnitTest, addtest, mksuite
from smanstal.types.module import fromfile

# All tests go here
from os.path import abspath, sep, join as joinpath
testpkg = joinpath(sep.join(abspath(__file__).split(sep)[:-2]), 'unit', '__init__.py')

mod = fromfile(testpkg)
TestUnitTests = mod.suite()

# EXAMPLE:
# from anyall.tests import suite as anyall_testsuite
# TestUnitTests = anyall_testsuite()

# Create suite function for this module
suite = addtest(mksuite(__file__))

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())

