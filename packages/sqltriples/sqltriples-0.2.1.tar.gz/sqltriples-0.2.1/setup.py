#! /usr/bin/env python

from distutils.core import setup

import sqltriples

setup(
    name         = "sqltriples",
    description  = "A simple SQL-accessible RDF triple store",
    author       = "Paul Boddie",
    author_email = "paul@boddie.org.uk",
    url          = "http://www.boddie.org.uk/python/sqltriples.html",
    version      = sqltriples.__version__,
    py_modules   = ["sqltriples"],
    scripts      = ["tools/sqltriples_admin.py"]
    )
