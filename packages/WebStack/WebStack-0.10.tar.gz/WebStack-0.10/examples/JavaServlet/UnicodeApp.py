#!/usr/bin/env python

from WebStack.Adapters import JavaServlet
from Unicode import UnicodeResource
from javax.servlet.http import HttpServlet

class UnicodeApp(HttpServlet):
    def __init__(self):
        HttpServlet.__init__(self)
        self.dispatcher = JavaServlet.Dispatcher(UnicodeResource())

    def service(self, request, response):
        self.dispatcher.service(request, response)

# vim: tabstop=4 expandtab shiftwidth=4
