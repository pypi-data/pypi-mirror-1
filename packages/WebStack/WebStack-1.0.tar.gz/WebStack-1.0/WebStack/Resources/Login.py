#!/usr/bin/env python

"""
Login resources which redirect clients back to an application after a successful
login.

Copyright (C) 2004, 2005 Paul Boddie <paul@boddie.org.uk>

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA
"""

import WebStack.Generic
from WebStack.Helpers.Auth import get_token

class LoginResource:

    "A resource providing a login screen."

    encoding = "utf-8"

    def __init__(self, authenticator, use_redirect=1, urlencoding=None):

        """
        Initialise the resource with an 'authenticator'.

        If the optional 'use_redirect' flag is set to 0, a confirmation screen
        is given instead of redirecting the user back to the original
        application.

        The optional 'urlencoding' parameter allows a special encoding to be
        used in producing the redirection path.
        """

        self.authenticator = authenticator
        self.use_redirect = use_redirect
        self.urlencoding = urlencoding or self.encoding

    def respond(self, trans):

        "Respond using the transaction 'trans'."

        fields_path = trans.get_fields_from_path(self.urlencoding)
        fields_body = trans.get_fields_from_body(self.encoding)

        # NOTE: Handle missing redirects better.

        if fields_body.has_key("app"):
            apps = fields_body["app"]
            app = apps[0]
        elif fields_path.has_key("app"):
            apps = fields_path["app"]
            app = apps[0]
        else:
            app = u""

        if fields_body.has_key("path"):
            paths = fields_body["path"]
            path = paths[0]
        elif fields_path.has_key("path"):
            paths = fields_path["path"]
            path = paths[0]
        else:
            path = u""

        if fields_body.has_key("qs"):
            qss = fields_body["qs"]
            qs = qss[0]
        elif fields_path.has_key("qs"):
            qss = fields_path["qs"]
            qs = qss[0]
        else:
            qs = u""

        # Check for a submitted login form.

        if fields_body.has_key("login"):
            if self.authenticator.authenticate(trans):
                self._redirect(trans, app, path, qs)
                return

        # Otherwise, show the login form.

        self._show_login(trans, app, path, qs)

    def _redirect(self, trans, app, path, qs):

        """
        Redirect the client using 'trans' and the given 'app', 'path' and 'qs'
        details.
        """

        if self.use_redirect:
            trans.set_header_value("Location", app + trans.encode_path(path, self.urlencoding) + qs)
            trans.set_response_code(302) # was 307

        # Show the success page anyway.

        self._show_success(trans, app, path, qs)

    def _show_login(self, trans, app, path, qs):

        """
        Writes a login screen using the transaction 'trans', including details of the
        'app', 'path' and 'qs' which the client was attempting to access.
        """

        trans.set_content_type(WebStack.Generic.ContentType("text/html", self.encoding))
        out = trans.get_response_stream()
        out.write("""
<html>
  <head>
    <title>Login Example</title>
  </head>
  <body>
    <h1>Login</h1>
    <form method="POST">
      <p>Username: <input name="username" type="text" size="12"/></p>
      <p>Password: <input name="password" type="text" size="12"/></p>
      <p><input name="login" type="submit" value="Login"/></p>
      <input name="app" type="hidden" value="%s"/>
      <input name="path" type="hidden" value="%s"/>
      <input name="qs" type="hidden" value="%s"/>
    </form>
  </body>
</html>
""" % (app, path, qs))

    def _show_success(self, trans, app, path, qs):

        # When authentication fails or is yet to take place, show the login
        # screen.

        trans.set_content_type(WebStack.Generic.ContentType("text/html", self.encoding))
        out = trans.get_response_stream()
        out.write("""
<html>
  <head>
    <title>Login Example</title>
  </head>
  <body>
    <h1>Login Successful</h1>
    <p>Please proceed <a href="%s%s%s">to the application</a>.</p>
  </body>
</html>
""" % (app, trans.encode_path(path, self.urlencoding), qs))

class LoginAuthenticator:

    def __init__(self, secret_key, credentials, cookie_name=None):

        """
        Initialise the authenticator with a 'secret_key', the authenticator's registry of
        'credentials' and an optional 'cookie_name'.

        The 'credentials' must be an object which supports tests of the form
        '(username, password) in credentials'.
        """

        self.secret_key = secret_key
        self.credentials = credentials
        self.cookie_name = cookie_name or "LoginAuthenticator"

    def authenticate(self, trans):

        """
        Authenticate the sender of the transaction 'trans', returning 1 (true) if they are
        recognised, 0 (false) otherwise.
        """

        # Process any supplied parameters.

        fields = trans.get_fields_from_body()

        if fields.has_key("username") and fields.has_key("password"):
            usernames, passwords = fields["username"], fields["password"]

            # Insist on only one username and password.

            if len(usernames) == 1 and len(passwords) == 1:
                username, password = usernames[0], passwords[0]

                # Check against the class's credentials.

                if (username, password) in self.credentials:

                    # Make a special cookie token.

                    self.set_token(trans, username)
                    return 1

        return 0

    def set_token(self, trans, username):

        "Set an authentication token in 'trans' with the given 'username'."

        trans.set_cookie_value(
            self.cookie_name,
            get_token(username, self.secret_key),
            path="/"
        )

# vim: tabstop=4 expandtab shiftwidth=4
