#! /usr/bin/env python

from distutils.core import setup

import pprocess

setup(
    name         = "pprocess",
    description  = "Elementary parallel programming for Python",
    author       = "Paul Boddie",
    author_email = "paul@boddie.org.uk",
    url          = "http://www.boddie.org.uk/python/pprocess.html",
    version      = pprocess.__version__,
    py_modules   = ["pprocess"]
    )
