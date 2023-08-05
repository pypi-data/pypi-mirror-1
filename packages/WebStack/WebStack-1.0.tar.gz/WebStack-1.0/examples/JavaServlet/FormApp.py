#!/usr/bin/env python

from WebStack.Adapters import JavaServlet
from Form import FormResource
from javax.servlet.http import HttpServlet

class FormApp(HttpServlet):
    def __init__(self):
        HttpServlet.__init__(self)
        self.dispatcher = JavaServlet.Dispatcher(FormResource())

    def service(self, request, response):
        self.dispatcher.service(request, response)

# vim: tabstop=4 expandtab shiftwidth=4
