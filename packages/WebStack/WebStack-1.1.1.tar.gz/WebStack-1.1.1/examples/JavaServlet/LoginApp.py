#!/usr/bin/env python

from WebStack.Adapters import JavaServlet
from WebStack.Resources.Login import LoginResource, LoginAuthenticator
from javax.servlet.http import HttpServlet

# NOTE: Not sure if the resource should be maintained in a resource pool.

resource = LoginResource(
    LoginAuthenticator(
        secret_key="horses",
        credentials=(
            ("badger", "abc"),
            ("vole", "xyz"),
        )
    ),
    use_redirect=0
)

class LoginApp(HttpServlet):
    def __init__(self):
        global resource
        HttpServlet.__init__(self)
        self.dispatcher = JavaServlet.Dispatcher(resource)

    def service(self, request, response):
        self.dispatcher.service(request, response)

# vim: tabstop=4 expandtab shiftwidth=4
