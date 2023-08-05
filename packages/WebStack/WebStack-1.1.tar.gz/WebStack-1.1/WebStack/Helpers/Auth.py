#!/usr/bin/env python

"""
Authentication/authorisation helper classes and functions.

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
