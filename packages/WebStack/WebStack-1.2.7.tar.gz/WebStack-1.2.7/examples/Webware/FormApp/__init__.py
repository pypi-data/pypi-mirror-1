#!/usr/bin/env python

"""
Webware plug-in code.
"""

__version__ = "0.1"

from WebStack.Adapters.Webware import WebStackServletFactory
from Form import FormResource

# NOTE: Initialising a shared resource.

resource = FormResource()

def InstallInWebKit(appServer):
    global resource
    app = appServer.application()

    # NOTE: Allow .form files only. Really, we'd like any kind of file, but
    # NOTE: that would severely undermine the servlet factory concept.

    app.addServletFactory(WebStackServletFactory(app, resource, [".form"]))

# vim: tabstop=4 expandtab shiftwidth=4
