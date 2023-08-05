#!/usr/bin/env python

from WebStack.Adapters import JavaServlet
from Simple import SimpleResource
from WebStack.Resources.LoginRedirect import LoginRedirectResource, LoginRedirectAuthenticator
from javax.servlet.http import HttpServlet

# NOTE: Not sure if the resource should be maintained in a resource pool.

resource = LoginRedirectResource(
    login_url="http://localhost:8080/LoginApp/",
    app_url="http://localhost:8080",
    resource=SimpleResource(),
    authenticator=LoginRedirectAuthenticator(secret_key="horses"),
    anonymous_parameter_name="anonymous",
    logout_parameter_name="logout"
    )

class SimpleWithLoginApp(HttpServlet):
    def __init__(self):
        global resource
        HttpServlet.__init__(self)
        self.dispatcher = JavaServlet.Dispatcher(resource)

    def service(self, request, response):
        self.dispatcher.service(request, response)

# vim: tabstop=4 expandtab shiftwidth=4
