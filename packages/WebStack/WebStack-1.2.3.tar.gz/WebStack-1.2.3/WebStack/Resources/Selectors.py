#!/usr/bin/env python

"""
Resources which "select" other resources, sometimes causing desirable
side-effects.

Copyright (C) 2007 Paul Boddie <paul@boddie.org.uk>

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

class PathSelector:

    "Set a request's current path and processed path info on an attribute."

    def __init__(self, resource, add_slash=1, attribute_name="root", path_encoding="utf-8"):

        """
        Initialise the selector with a 'resource' (to which all requests shall
        be forwarded), specifying whether a "/" character shall be added to
        stored paths using the optional 'add_slash' parameter (default is true),
        along with an optional 'attribute_name' (indicating the name of the
        attribute on which the path information shall be stored), and the
        optional 'path_encoding' for interpreting URL-encoded path values.
        """

        self.resource = resource
        self.add_slash = add_slash
        self.attribute_name = attribute_name
        self.path_encoding = path_encoding

    def _slash(self):
        if self.add_slash:
            return "/"
        else:
            return ""

    def respond(self, trans):

        """
        Respond to the transaction 'trans' by storing the current path and
        processed virtual path info on the named transaction attribute, then
        forwarding the transaction to the previously specified resource.
        """

        pwi = trans.get_path_without_info(self.path_encoding)

        # Make a note of the path given the following general rule:
        #    path_without_info + path_info
        # == path_without_info + processed_virtual_path_info + virtual_path_info

        attributes = trans.get_attributes()
        attributes[self.attribute_name] = trans.encode_path(
            pwi + trans.get_processed_virtual_path_info(self.path_encoding) + self._slash(),
            self.path_encoding
            )

        self.resource.respond(trans)

class EncodingSelector:

    """
    Set the default encoding (or "charset") on transactions presented to this
    resource.
    """

    def __init__(self, resource, encoding):

        """
        Initialise the selector with a 'resource' (to which all requests shall
        be forwarded), specifying the 'encoding' which shall be used as the
        default encoding (or "charset") for all transactions handled by this
        resource.
        """

        self.resource = resource
        self.encoding = encoding

    def respond(self, trans):

        """
        Respond to the transaction 'trans' by setting the default encoding (or
        "charset") on 'trans', then forwarding the transaction to the previously
        specified resource.
        """

        trans.default_charset = self.encoding
        self.resource.respond(trans)

# vim: tabstop=4 expandtab shiftwidth=4
