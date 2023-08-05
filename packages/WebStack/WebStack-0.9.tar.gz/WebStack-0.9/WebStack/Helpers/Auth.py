#!/usr/bin/env python

"""
Authentication/authorisation helper classes and functions.
"""

import base64
import md5

class UserInfo:

    """
    A class used to represent user information in terms of the authentication
    scheme employed and the user details.
    """

    def __init__(self, auth_header):

        """
        Initialise the object with the value of the 'auth_header' - that is, the
        HTTP Authorization header.
        """

        self.scheme, auth_details = auth_header.split(" ")
        if self.scheme == "Basic":

            # NOTE: Assume that no username or password contains ":".

            self.username, self.password = base64.decodestring(auth_details).split(":")

        else:

            # NOTE: Other schemes not yet supported.

            self.username, self.password = None, None

def get_token(plaintext, secret_key):

    """
    Return a string containing an authentication token made from the given
    'plaintext' and 'secret_key'.
    """

    return plaintext + ":" + md5.md5(plaintext + secret_key).hexdigest()

# vim: tabstop=4 expandtab shiftwidth=4
