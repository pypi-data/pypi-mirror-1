#!/usr/bin/env python

"""
Login redirection resources, sending unauthenticated users to a login screen
URL.

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

from WebStack.Helpers.Auth import get_token
import WebStack.Generic

class LoginRedirectResource:

    "A resource redirecting to a login URL."

    encoding = "utf-8"

    def __init__(self, login_url, app_url, resource, authenticator, anonymous_parameter_name=None,
        anonymous_username="anonymous", logout_parameter_name=None, logout_url="/",
        use_logout_redirect=1, urlencoding=None):

        """
        Initialise the resource with a 'login_url', an 'app_url' where the
        'resource' for the application being protected should be reachable, and
        an 'authenticator'.

        If the optional 'anonymous_parameter_name' is set, clients providing a
        parameter of that name in the URL will not be authenticated, but then
        such clients will get a predefined user identity associated with them,
        configurable using the optional 'anonymous_username'.

        If the optional 'logout_parameter_name' is set, clients providing a
        parameter of that name in the URL will become logged out. After logging
        out, clients are redirected to a location which can be configured by the
        optional 'logout_url'.

        If the optional 'use_logout_redirect' flag is set to 0, a confirmation
        screen is given instead of redirecting the user to the 'logout_url'.

        The optional 'urlencoding' parameter allows a special encoding to be
        used in producing the redirection path.
        """

        self.login_url = login_url
        self.app_url = app_url
        self.resource = resource
        self.authenticator = authenticator
        self.anonymous_parameter_name = anonymous_parameter_name
        self.anonymous_username = anonymous_username
        self.logout_parameter_name = logout_parameter_name
        self.logout_url = logout_url
        self.use_logout_redirect = use_logout_redirect
        self.urlencoding = urlencoding or self.encoding

    def respond(self, trans):

        "Respond using the given transaction 'trans'."

        fields_path = trans.get_fields_from_path(self.urlencoding)

        # Check for the logout parameter, if appropriate.

        if self.logout_parameter_name is not None and fields_path.has_key(self.logout_parameter_name):

            # Remove the special cookie token, then pass on the transaction.

            self.authenticator.unset_token(trans)

            # Redirect to the logout URL.

            if self.use_logout_redirect:
                trans.set_header_value("Location", self.logout_url)
                trans.set_response_code(302) # was 307

            # Show the logout confirmation anyway.

            self._show_logout(trans, self.logout_url)

        # Check the authentication details with the specified authenticator.

        elif self.authenticator.authenticate(trans):

            # If successful, pass on the transaction.

            self.resource.respond(trans)

        # Check for the anonymous parameter, if appropriate.

        elif self.anonymous_parameter_name is not None and fields_path.has_key(self.anonymous_parameter_name):

            # Make a special cookie token, then pass on the transaction.

            self.authenticator.set_token(trans, self.anonymous_username)
            self.resource.respond(trans)

        else:

            # Redirect to the login URL.

            path = trans.get_path_without_query(self.urlencoding)
            qs = trans.get_query_string()
            if qs:
                qs = "?" + qs
            trans.redirect("%s?app=%s&path=%s&qs=%s" % (
                self.login_url,
                trans.encode_path(self.app_url, self.urlencoding),
                trans.encode_path(path, self.urlencoding),
                trans.encode_path(qs, self.urlencoding))
                )

    def _show_logout(self, trans, redirect):

        """
        Write a confirmation page to 'trans' containing the 'redirect' URL which the
        client should be sent to upon logout.
        """

        # When logout takes place, show the login screen.

        trans.set_content_type(WebStack.Generic.ContentType("text/html", self.encoding))
        out = trans.get_response_stream()
        out.write("""
<html>
  <head>
    <title>Logout</title>
  </head>
  <body>
    <h1>Logout Successful</h1>
    <p>Please proceed <a href="%s">to the application</a>.</p>
  </body>
</html>
""" % redirect)

class LoginRedirectAuthenticator:

    """
    An authenticator which verifies the credentials provided in a special login cookie.
    """

    def __init__(self, secret_key, cookie_name=None):

        "Initialise the authenticator with a 'secret_key' and an optional 'cookie_name'."

        self.secret_key = secret_key
        self.cookie_name = cookie_name or "LoginAuthenticator"

    def authenticate(self, trans):

        """
        Authenticate the originator of 'trans', updating the object if successful and
        returning 1 (true) if successful, 0 (false) otherwise.
        """

        cookie = trans.get_cookie(self.cookie_name)
        if cookie is None or cookie.value is None:
            return 0

        # Test the token from the cookie against a recreated token using the
        # given information.

        username = cookie.value.split(":")[0]
        if cookie.value == get_token(username, self.secret_key):

            # Update the transaction with the user details.

            trans.set_user(username)
            return 1
        else:
            return 0

    def set_token(self, trans, username):

        "Set an authentication token in 'trans' with the given 'username'."

        trans.set_cookie_value(
            self.cookie_name,
            get_token(username, self.secret_key),
            path="/"
        )

        # Update the transaction with the user details.

        trans.set_user(username)

    def unset_token(self, trans):

        "Unset the authentication token in 'trans'."

        trans.delete_cookie(self.cookie_name)

# vim: tabstop=4 expandtab shiftwidth=4
