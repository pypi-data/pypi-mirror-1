#!/usr/bin/env python

"Mapping from names to resources."

import WebStack.Generic

class MapResource:

    "A resource mapping names to other resources."

    def __init__(self, mapping):

        """
        Initialise the resource with a 'mapping' of names to resources. The
        'mapping' should be a dictionary-like object employing simple names
        without "/" characters; the special value None is used where no name
        is found in the request path.
        """

        self.mapping = mapping

    def respond(self, trans):

        """
        Using the path information from the given transaction 'trans', invoke
        mapped resources. Otherwise return an error condition.
        """

        # Get the path info.

        parts = trans.get_virtual_path_info().split("/")

        # The first part should always be empty.

        if len(parts) > 1:
            name = parts[1]
        else:
            name = None

        # Get the mapped resource.

        resource = self.mapping.get(name)

        # If a resource was found, change the transaction's path info, then
        # invoke the transaction, transferring control completely.

        new_path = parts[0:1] + (parts[2:] or [""])
        new_path_info = "/".join(new_path)
        trans.set_virtual_path_info(new_path_info)

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

# vim: tabstop=4 expandtab shiftwidth=4
