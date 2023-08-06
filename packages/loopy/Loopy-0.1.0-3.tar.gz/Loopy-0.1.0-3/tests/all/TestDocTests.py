# Module: template
# File: template.py
# Copyright (C) 2006 Ariel De Ocampo arieldeocampo@gmail.com
#
# This module is part of the <WHAT-HAVE-YOU> project and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

import unittest
from smanstal.tests import addtest, mkdocsuite

# All tests go here
from os.path import abspath, sep, join as joinpath
apidocdir = joinpath(sep.join(abspath(__file__).split(sep)[:-3]), 'doc', 'api')

# Create suite function for this module
suite = addtest(mkdocsuite(apidocdir, recurse=True))

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())

