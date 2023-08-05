#! /usr/bin/env python

from distutils.core import setup

import RDFFormats

setup(
    name         = "RDFFormats",
    description  = "General support for conversion of data to RDF information.",
    author       = "Paul Boddie",
    author_email = "paul@boddie.org.uk",
    url          = "http://www.boddie.org.uk/python/RDFFormats.html",
    version      = RDFFormats.__version__,
    packages     = ["RDFFormats"]
    )
