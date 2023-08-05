#!/usr/bin/env python

"""
Environment helper functions.
"""

def get_headers(env):

    """
    Get the headers from the given environment 'env', which should be a
    dictionary-like object.

    Returns a dictionary-like object containing likely headers.
    """

    headers = {}
    for cgi_key, value in env.items():
        if cgi_key.startswith("HTTP_"):
            header_name = cgi_key[len("HTTP_"):].replace("_", "-").lower()
            headers[header_name] = value

    return headers

# vim: tabstop=4 expandtab shiftwidth=4
