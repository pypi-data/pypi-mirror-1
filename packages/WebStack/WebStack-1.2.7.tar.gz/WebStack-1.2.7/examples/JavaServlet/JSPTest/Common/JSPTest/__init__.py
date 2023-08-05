#!/usr/bin/env python

"A simple application for test purposes."

import WebStack.Generic

class JSPTestResource:

    "A simple resource."

    def respond(self, trans):

        # Store some information in attributes.

        print "Attributes..."
        attr = trans.get_attributes()
        attr["hello"] = "world"
        rd = trans.get_servlet().getServletConfig().getServletContext().getRequestDispatcher("/test.jsp")
        print "Forward..."
        rd.forward(trans.request, trans.response)

# vim: tabstop=4 expandtab shiftwidth=4
