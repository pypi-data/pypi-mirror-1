#!/usr/bin/env python

"""
Environment helper functions.

Copyright (C) 2004, 2005, 2007 Paul Boddie <paul@boddie.org.uk>

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

import WebStack.Helpers.Request

cgi_names = ("CONTENT_LENGTH", "CONTENT_TYPE")

def get_headers(env):

    """
    Get the headers from the given environment 'env', which should be a
    dictionary-like object.

    Returns a dictionary-like object containing likely headers.
    """

    headers = WebStack.Helpers.Request.HeaderDict()

    for cgi_key, value in env.items():
        if cgi_key.startswith("HTTP_"):
            header_name = cgi_key[len("HTTP_"):].replace("_", "-")
            headers[header_name] = value
        elif cgi_key in cgi_names:
            header_name = cgi_key.replace("_", "-")
            headers[header_name] = value

    return headers

# vim: tabstop=4 expandtab shiftwidth=4
