#!/usr/bin/env python

from WebStack.Adapters import JavaServlet
from Calendar import CalendarResource
from javax.servlet.http import HttpServlet

class CalendarApp(HttpServlet):
    def __init__(self):
        HttpServlet.__init__(self)

        # Choose or customise one of the following if the example fails.

        self.dispatcher = JavaServlet.Dispatcher(CalendarResource())
        #self.dispatcher = JavaServlet.Dispatcher(CalendarResource("iso-8859-1"))

    def service(self, request, response):
        self.dispatcher.service(request, response)

# vim: tabstop=4 expandtab shiftwidth=4
