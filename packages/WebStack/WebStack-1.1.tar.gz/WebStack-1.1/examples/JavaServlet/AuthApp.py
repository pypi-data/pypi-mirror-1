#!/usr/bin/env python

from WebStack.Adapters import JavaServlet
from Auth import AuthResource, AuthAuthenticator
from javax.servlet.http import HttpServlet

class AuthApp(HttpServlet):
    def __init__(self):
        HttpServlet.__init__(self)
        self.dispatcher = JavaServlet.Dispatcher(AuthResource(), AuthAuthenticator())

    def service(self, request, response):
        self.dispatcher.service(request, response)

# vim: tabstop=4 expandtab shiftwidth=4
