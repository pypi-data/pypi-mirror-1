#! /usr/bin/env python

from distutils.core import setup

import RDFMessage

setup(
    name         = "RDFMessage",
    description  = "Conversion of message resources to RDF information.",
    author       = "Paul Boddie",
    author_email = "paul@boddie.org.uk",
    url          = "http://www.boddie.org.uk/python/RDFMessage.html",
    version      = RDFMessage.__version__,
    packages     = ["RDFMessage"],
    scripts      = ["tools/Mailbox.py"]
    )
