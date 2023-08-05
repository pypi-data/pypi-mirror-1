#!/usr/bin/env python

"A test of authentication/authorisation."

import WebStack.Generic

class AuthResource:

    "A resource demanding authentication."

    def respond(self, trans):
        trans.set_content_type(WebStack.Generic.ContentType("text/html"))

        # Write out confirmation, otherwise.

        out = trans.get_response_stream()
        out.write("""
<html>
  <body>
    <h1>Authorised</h1>
    <p>Hello user %s!</p>
  </body>
</html>
""" % (
    trans.get_user(),
))

class AuthAuthenticator:

    "An authenticator for the application."

    def authenticate(self, trans):
        user = trans.get_user()
        return user == "badger"

    def get_auth_type(self):
        return "Basic"

    def get_realm(self):
        return "AuthResource"

# vim: tabstop=4 expandtab shiftwidth=4
