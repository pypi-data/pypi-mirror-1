#! /usr/bin/env python

from distutils.core import setup

import parallel

setup(
    name         = "parallel",
    description  = "Elementary parallel programming for Python",
    author       = "Paul Boddie",
    author_email = "paul@boddie.org.uk",
    url          = "http://www.python.org/pypi/parallel",
    version      = parallel.__version__,
    py_modules   = ["parallel"]
    )
