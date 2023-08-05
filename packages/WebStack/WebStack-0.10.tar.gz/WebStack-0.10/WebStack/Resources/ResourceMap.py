#!/usr/bin/env python

"""
Mapping from names to resources.

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
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307  USA
"""

import WebStack.Generic

class MapResource:

    "A resource mapping names to other resources."

    def __init__(self, mapping, directory_redirects=1):

        """
        Initialise the resource with a 'mapping' of names to resources. The
        'mapping' should be a dictionary-like object employing simple names
        without "/" characters; the special value None is used where no name
        corresponds to that used in the request path and may be used to map to
        a "catch all" resource.

        The optional 'directory_redirects' parameter, if set to a true value (as
        is the default setting), causes a redirect adding a trailing "/"
        character if the request path does not end with such a character.
        """

        self.mapping = mapping
        self.directory_redirects = directory_redirects

    def respond(self, trans):

        """
        Using the path information from the given transaction 'trans', invoke
        mapped resources. Otherwise return an error condition.
        """

        # Get the path info.

        parts = trans.get_virtual_path_info().split("/")

        # Where the published resource has a path info value defined (ie. its
        # path info consists of a "/" character plus some other text), the first
        # part should always be empty and there should always be a second part.
        # Where the published resource has no path info defined, there will only
        # be one part. In the latter case, we define the name to be None,
        # although the name will not be relevant if directory_redirects is set.

        if len(parts) > 1:
            name = parts[1]
        elif self.directory_redirects:
            self.send_redirect(trans)
        else:
            name = None

        # Get the mapped resource.

        resource = self.mapping.get(name)
        if resource is None:
            resource = self.mapping.get(None)

        # If a resource was found, change the transaction's path info.
        # eg. "/this/next" -> "/next"
        # eg. "/this/" -> "/"
        # eg. "/this" -> ""

        new_path = parts[0:1] + parts[2:]
        new_path_info = "/".join(new_path)
        trans.set_virtual_path_info(new_path_info)

        # Invoke the transaction, transferring control completely.

        if resource is not None:
            resource.respond(trans)
            return

        # Otherwise, signal an error.

        self.send_error(trans)

    def send_error(self, trans):

        "Send the error using the given 'trans'."

        trans.set_response_code(404)
        trans.set_content_type(WebStack.Generic.ContentType("text/plain"))
        out = trans.get_response_stream()
        out.write("Resource '%s' not found." % trans.get_path_info())

    def send_redirect(self, trans):

        """
        Send a redirect using the given 'trans', adding a "/" character to the
        end of the request path.
        """

        query_string = trans.get_query_string()
        if query_string:
            query_string = "?" + query_string

        trans.set_response_code(302)
        trans.set_header_value("Location", trans.get_path_without_query() + "/" + query_string)
        raise WebStack.Generic.EndOfResponse

# vim: tabstop=4 expandtab shiftwidth=4
