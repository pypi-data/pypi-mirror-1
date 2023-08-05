#! /usr/bin/env python

from distutils.core import setup

import RDFCalendar

setup(
    name         = "RDFCalendar",
    description  = "Conversion of iCalendar/vCard resources to RDF information",
    author       = "Paul Boddie",
    author_email = "paul@boddie.org.uk",
    url          = "http://www.boddie.org.uk/python/RDFCalendar.html",
    version      = RDFCalendar.__version__,
    packages     = ["RDFCalendar"],
    scripts      = ["tools/iCalendar.py", "tools/freebusy.py"]
    )
