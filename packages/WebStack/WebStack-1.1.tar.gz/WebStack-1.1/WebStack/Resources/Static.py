#!/usr/bin/env python

"""
Resources for serving static content.

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

from WebStack.Generic import ContentType, EndOfResponse
import os

class DirectoryResource:

    "A resource serving the contents of a filesystem directory."

    def __init__(self, directory, media_types=None, unrecognised_media_type="application/data", urlencoding="utf-8"):

        """
        Initialise the resource to serve files from the given 'directory'.

        The optional 'media_types' dictionary can be used to map filename
        extensions to media types, where extensions consist of the part of a
        name after a "." character (such as "txt", "html"), and where media
        types are the usual content descriptions (such as "text/plain" and
        "text/html").

        If 'media_types' contains a mapping from None to a media type, then
        this mapping is used when no extension is present on a requested
        resource name.

        Where no media type can be found for a resource, a predefined media
        type is set which can be overridden by specifying a value for the
        optional 'unrecognised_media_type' parameter.

        The optional 'urlencoding' is used to decode "URL encoded" character
        values in the request path, and overrides the default encoding wherever
        possible.
        """

        self.directory = directory
        self.media_types = media_types or {}
        self.unrecognised_media_type = unrecognised_media_type
        self.urlencoding = urlencoding

    def respond(self, trans):

        "Respond to the given transaction, 'trans', by serving a file."

        parts = trans.get_virtual_path_info(self.urlencoding).split("/")
        filename = parts[1]
        out = trans.get_response_stream()

        # Test for the file's existence.

        pathname = os.path.abspath(os.path.join(self.directory, filename))
        if not (pathname.startswith(os.path.join(self.directory, "/")) and os.path.exists(pathname) and os.path.isfile(pathname)):
            self.not_found(trans, filename)

        # Get the extension.

        extension_parts = filename.split(".")

        if len(extension_parts) > 1:
            extension = extension_parts[-1]
            media_type = self.media_types.get(extension)
        else:
            media_type = self.media_types.get(None)

        # Set the content type.
        # NOTE: Add other parts of the content type such as character encodings.

        if media_type is not None:
            trans.set_content_type(ContentType(media_type))
        else:
            trans.set_content_type(ContentType(self.unrecognised_media_type))

        # Write the file to the client.

        f = open(os.path.join(self.directory, filename), "rb")
        out.write(f.read())
        f.close()

    def not_found(self, trans, filename):

        """
        Send the "not found" response using the given transaction, 'trans', and
        specifying the given 'filename' (if appropriate).
        """

        trans.set_response_code(404)
        trans.set_content_type(ContentType("text/plain"))
        out = trans.get_response_stream()
        out.write("Resource '%s' not found." % filename)
        raise EndOfResponse

# vim: tabstop=4 expandtab shiftwidth=4
