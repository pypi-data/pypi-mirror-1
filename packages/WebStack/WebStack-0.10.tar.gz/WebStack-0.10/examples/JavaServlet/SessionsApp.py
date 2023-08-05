#!/usr/bin/env python

from WebStack.Adapters import JavaServlet
from Sessions import SessionsResource
from javax.servlet.http import HttpServlet

class SessionsApp(HttpServlet):
    def __init__(self):
        HttpServlet.__init__(self)
        self.dispatcher = JavaServlet.Dispatcher(SessionsResource())

    def service(self, request, response):
        self.dispatcher.service(request, response)

# vim: tabstop=4 expandtab shiftwidth=4
