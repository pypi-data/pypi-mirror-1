#!/usr/bin/env python

"""
Resources for serving static content.

Copyright (C) 2004, 2005, 2006 Paul Boddie <paul@boddie.org.uk>

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

    def __init__(self, directory, media_types=None,
        unrecognised_media_type="application/data", content_types=None,
        unrecognised_content_type=None, default_encoding=None,
        urlencoding="utf-8"):

        """
        Initialise the resource to serve files from the given 'directory'.

        The optional 'content_types' dictionary can be used to map filename
        extensions to content types, where extensions consist of the part of a
        name after a "." character (such as "txt", "html"), and where content
        types are typically WebStack.Generic.ContentType objects.

        The optional 'media_types' dictionary can be used to map filename
        extensions to media types, where extensions consist of the part of a
        name after a "." character (such as "txt", "html"), and where media
        types are the usual content descriptions (such as "text/plain" and
        "text/html").

        If 'content_types' or 'media_types' contain a mapping from None to a
        content or media type, then this mapping is used when no extension is
        present on a requested resource name.

        Where no content or media type can be found for a resource, a
        predefined media type is set which can be overridden by specifying a
        value for the optional 'unrecognised_media_type' or for the
        'unrecognised_content_type' parameter - the latter overriding the former
        if specified.

        The optional 'default_encoding' is used to specify the character
        encoding used in any content type produced from a media type (or for
        the unrecognised media type). If set to None (as is the default), no
        encoding declaration is produced for file content associated with media
        types.

        The optional 'urlencoding' is used to decode "URL encoded" character
        values in the request path, and overrides the default encoding wherever
        possible.
        """

        self.directory = directory
        self.content_types = content_types or {}
        self.media_types = media_types or {}
        self.unrecognised_media_type = unrecognised_media_type
        self.unrecognised_content_type = unrecognised_content_type
        self.default_encoding = default_encoding
        self.urlencoding = urlencoding

    def respond(self, trans):

        "Respond to the given transaction, 'trans', by serving a file."

        parts = trans.get_virtual_path_info(self.urlencoding).split("/")
        filename = parts[1]
        out = trans.get_response_stream()

        # Test for the file's existence.

        pathname = os.path.abspath(os.path.join(self.directory, filename))
        if not (pathname.startswith(os.path.join(self.directory, "/")) and \
            os.path.exists(pathname) and os.path.isfile(pathname)):

            self.not_found(trans, filename)

        # Get the extension.

        extension_parts = filename.split(".")

        if len(extension_parts) > 1:
            extension = extension_parts[-1]
            content_type = self.content_types.get(extension)
            media_type = self.media_types.get(extension)
        else:
            content_type = self.content_types.get(None)
            media_type = self.media_types.get(None)

        # Set the content type.

        if content_type is not None:
            trans.set_content_type(content_type)
        elif media_type is not None:
            trans.set_content_type(ContentType(media_type, self.default_encoding))
        elif self.unrecognised_content_type is not None:
            trans.set_content_type(self.unrecognised_content_type)
        else:
            trans.set_content_type(
                ContentType(self.unrecognised_media_type, self.default_encoding))

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

class FileResource:

    "A file serving resource."

    def __init__(self, filename, content_type):
        self.filename = filename
        self.content_type = content_type

    def respond(self, trans):
        trans.set_content_type(self.content_type)
        f = open(self.filename, "rb")
        trans.get_response_stream().write(f.read())
        f.close()

# vim: tabstop=4 expandtab shiftwidth=4
