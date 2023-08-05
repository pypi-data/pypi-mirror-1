#! /usr/bin/env python

from distutils.core import setup

import WebStack

setup(
    name         = "WebStack",
    description  = "Common API for Web applications",
    author       = "Paul Boddie",
    author_email = "paul@boddie.org.uk",
    url          = "http://www.boddie.org.uk/python/WebStack.html",
    version      = WebStack.__version__,
    packages     = ["WebStack", "WebStack.Adapters", "WebStack.Adapters.Helpers", "WebStack.Helpers", "WebStack.Resources"]
    )
