#!/usr/bin/env python

"Login resources which redirect clients back to an application after a successful login."

import WebStack.Generic
from WebStack.Helpers.Auth import get_token

class LoginResource:

    "A resource providing a login screen."

    def __init__(self, authenticator, use_redirect=1):

        """
        Initialise the resource with an 'authenticator'.

        If the optional 'use_redirect' flag is set to 0, a confirmation screen is given
        instead of redirecting the user back to the original application.
        """

        self.authenticator = authenticator
        self.use_redirect = use_redirect

    def respond(self, trans):

        "Respond using the transaction 'trans'."

        fields_path = trans.get_fields_from_path()
        fields_body = trans.get_fields_from_body()

        # NOTE: Handle missing redirects better.

        if fields_body.has_key("redirect"):
            redirects = fields_body["redirect"]
            redirect = redirects[0]
        elif fields_path.has_key("redirect"):
            redirects = fields_path["redirect"]
            redirect = redirects[0]
        else:
            redirect = ""

        # Check for a submitted login form.

        if fields_body.has_key("login"):
            if self.authenticator.authenticate(trans):
                self._redirect(trans, redirect)
                return

        # Otherwise, show the login form.

        self._show_login(trans, redirect)

    def _redirect(self, trans, redirect):

        "Redirect the client using 'trans' and the given 'redirect' URL."

        if self.use_redirect:
            trans.set_header_value("Location", redirect)
            trans.set_response_code(302) # was 307

        # Show the success page anyway.

        self._show_success(trans, redirect)

    def _show_login(self, trans, redirect):

        """
        Writes a login screen using the transaction 'trans', including details of the
        'redirect' URL which the client was attempting to access.
        """

        trans.set_content_type(WebStack.Generic.ContentType("text/html"))
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
      <input name="redirect" type="hidden" value="%s"/>
    </form>
  </body>
</html>
""" % redirect)

    def _show_success(self, trans, redirect):

        # When authentication fails or is yet to take place, show the login
        # screen.

        trans.set_content_type(WebStack.Generic.ContentType("text/html"))
        out = trans.get_response_stream()
        out.write("""
<html>
  <head>
    <title>Login Example</title>
  </head>
  <body>
    <h1>Login Successful</h1>
    <p>Please proceed <a href="%s">to the application</a>.</p>
  </body>
</html>
""" % redirect)

    def _decode(self, url):

        "Decode the given 'url' for redirection purposes."

        return url.replace("%3f", "?").replace("%26", "&")

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
