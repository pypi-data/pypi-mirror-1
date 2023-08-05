#! /usr/bin/env python

from distutils.core import setup

import jailtools

setup(
    name         = "jailtools",
    description  = "Modules for restricted execution of Python programs",
    author       = "Paul Boddie",
    author_email = "paul@boddie.org.uk",
    url          = "http://www.boddie.org.uk/python/jailtools.html",
    version      = jailtools.__version__,
    py_modules   = ["jailtools", "jailtalk"],
    scripts      = ["jailtools.py", "jailtalk.py"]
    )
