# Module: template
# File: template.py
# Copyright (C) 2006 Ariel De Ocampo arieldeocampo@gmail.com
#
# This module is part of the <WHAT-HAVE-YOU> project and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php
from setuptools import setup, find_packages

setup(
  name="Loopy",
  version="0.1.0-3",
  description="""Generic Event Loop Interface + Example Implementations""",
  author="Ariel De Ocampo",
  author_email = 'arieldeocampo@gmail.com',
  license = 'MIT License',
  long_description = """\
Loopy
======

Loopy defines a generic event loop interface from which to build adaptations
of other event loops. It is similar in purpose to the liboop_  library but 
written in pure python.

Currently, loopy includes implementations of libevent_, multitask_, and the standard
library module sched_.

.. _liboop: http://liboop.ofb.net
.. _libevent: http://www.monkey.org/~provos/libevent
.. _multitask: http://o2s.csail.mit.edu/o2s-wiki/multitask
.. _sched: http://docs.python.org/lib/module-sched.html
""",

  install_requires = [
      "multitask >= 0.1.0"
  ],
  packages=find_packages('src'),
  package_dir={'': 'src'},
  classifiers = [
      "Development Status :: 3 - Alpha",
      "Intended Audience :: Developers",
      "License :: OSI Approved :: MIT License",
      "Programming Language :: Python",
      "Topic :: Software Development :: Libraries :: Python Modules"
  ]
)

