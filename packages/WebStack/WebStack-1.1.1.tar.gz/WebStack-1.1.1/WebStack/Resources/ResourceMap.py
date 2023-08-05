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
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA
"""

import WebStack.Generic

class MapResource:

    "A resource mapping names to other resources."

    def __init__(self, mapping, pass_through=0, directory_redirects=1, urlencoding="utf-8"):

        """
        Initialise the resource with a 'mapping' of names to resources. The
        'mapping' should be a dictionary-like object employing simple names
        without "/" characters; the special value None is used to specify a
        "catch all" resource which receives all requests whose virtual path
        info does not match any of the names in the mapping. For example:

        mapping is {"mammals" : ..., "reptiles" : ..., None : ...}

        /mammals/cat -> matches "mammals"
        /reptiles/python -> matches "reptiles"
        /creatures/goblin -> no match, handled by None

        When this resource matches a name in the virtual path info to one of the
        names in the mapping, it removes the section of the virtual path info
        corresponding to that name before dispatching to the corresponding
        resource. For example:

        /mammals/dog -> match with "mammals" in mapping -> /dog

        By default, where the first part of the virtual path info does not
        correspond to any of the names in the mapping, the first piece of the
        virtual path info is removed before dispatching to the "catch all"
        resource. For example:

        /creatures/unicorn -> no match -> /unicorn

        However, the optional 'pass_through' parameter, if set to a true value
        (which is not the default setting), changes the above behaviour in cases
        where no matching name is found: in such cases, no part of the virtual
        path info is removed, and the request is dispatched to the "catch all"
        resource unchanged. For example:

        /creatures/unicorn -> no match -> /creatures/unicorn

        With 'pass_through' set to a true value, care must be taken if this
        resource is set as its own "catch all" resource. For example:

        map_resource = MapResource(...)
        map_resource.mapping[None] = map_resource

        The optional 'directory_redirects' parameter, if set to a true value (as
        is the default setting), causes a redirect adding a trailing "/"
        character if the request path does not end with such a character.

        The optional 'urlencoding' is used to decode "URL encoded" character
        values in the request path, and overrides the default encoding wherever
        possible.
        """

        self.mapping = mapping
        self.pass_through = pass_through
        self.directory_redirects = directory_redirects
        self.urlencoding = urlencoding

    def respond(self, trans):

        """
        Using the path information from the given transaction 'trans', invoke
        mapped resources. Otherwise return an error condition.
        """

        # Get the path info.

        parts = trans.get_virtual_path_info(self.urlencoding).split("/")

        # Where the published resource has a path info value defined (ie. its
        # path info consists of a "/" character plus some other text), the first
        # part should always be empty and there should always be a second part.
        # Where the published resource has no path info defined, there will only
        # be one part. In the latter case, we define the name to be the empty
        # string, although the name will not be relevant if directory_redirects
        # is set.

        if len(parts) > 1:
            name = parts[1]
        elif self.directory_redirects:
            self.send_redirect(trans)
        else:
            self.send_error(trans)
            return

        # Get the mapped resource.

        resource = self.mapping.get(name)
        if resource is None:
            resource = self.mapping.get(None)
            catch_all_resource = 1
        else:
            catch_all_resource = 0

        # If a resource was found, change the transaction's path info.
        # eg. "/this/next" -> "/next"
        # eg. "/this/" -> "/"
        # eg. "/this" -> ""
        # Such changes are not made if the resource is in "pass through" mode
        # and where the "catch all" resource is being used. In such situations
        # this resource just passes control to the "catch all" resource along
        # with all the path information intact.

        if not (catch_all_resource and self.pass_through):
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
        out.write("Resource '%s' not found." % trans.get_path_info(self.urlencoding))

    def send_redirect(self, trans):

        """
        Send a redirect using the given 'trans', adding a "/" character to the
        end of the request path.
        """

        path_without_query = trans.get_path_without_query(self.urlencoding)
        query_string = trans.get_query_string()
        if query_string:
            query_string = "?" + query_string
        trans.redirect(trans.encode_path(path_without_query, self.urlencoding) + "/" + query_string)

# vim: tabstop=4 expandtab shiftwidth=4
