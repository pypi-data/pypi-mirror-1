#!/usr/bin/env python

"A very simple application for test purposes."

class VerySimpleResource:

    "A very simple resource."

    def respond(self, trans):
        out = trans.get_response_stream()
        print >>out, "Hello world."

# vim: tabstop=4 expandtab shiftwidth=4
