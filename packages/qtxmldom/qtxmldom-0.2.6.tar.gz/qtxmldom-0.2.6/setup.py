#! /usr/bin/env python

from distutils.core import setup

import qtxmldom

setup(
    name         = "qtxmldom",
    description  = "PyXML-style API for the qtxml/khtml Python bindings",
    author       = "Paul Boddie",
    author_email = "paul@boddie.org.uk",
    url          = "http://www.boddie.org.uk/python/qtxmldom.html",
    version      = qtxmldom.__version__,
    packages     = ["qtxmldom"]
    )
