#!/usr/bin/env python

"""
Request helper classes.

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

class MessageBodyStream:

    """
    A naive stream class, providing a non-blocking stream for transactions when
    reading the message body. According to the HTTP standard, the following
    things decide how long the message is:

        * Use of the Content-Length header field (see 4.4 Message Length).
        * Use of the Transfer-Coding header field (see 3.6 Transfer Codings),
          particularly when the "chunked" coding is used.

    NOTE: For now, we don't support the Transfer-Coding business.
    """

    def __init__(self, stream, headers):

        """
        Initialise the object with the given underlying 'stream'. The supplied
        'headers' in a dictionary-style object are used to examine the nature of
        the request.
        """

        self.stream = stream
        self.headers = headers
        self.length = int(headers.get("Content-Length") or 0)

    def read(self, limit=None):

        "Reads all remaining data from the message body."

        if limit is not None:
            limit = min(limit, self.length)
        else:
            limit = self.length
        data = self.stream.read(limit)
        self.length = self.length - len(data)
        return data

    def readline(self):

        "Reads a single line of data from the message body."

        data = []
        while self.length > 0:
            data.append(self.read(1))
            if data[-1] == "\n":
                break
        return "".join(data)

    def readlines(self):

        """
        Reads all remaining data from the message body, splitting it into lines
        and returning the data as a list of lines.
        """

        lines = self.read().split("\n")
        for i in range(0, len(lines) - 1):
            lines[i] = lines[i] + "\n"
        return lines

    def close(self):

        "Closes the stream."

        self.stream.close()

class HeaderValue:

    "A container for header information."

    def __init__(self, principal_value, **attributes):

        """
        Initialise the container with the given 'principal_value' and optional
        keyword attributes representing the key=value pairs which accompany the
        'principal_value'.
        """

        self.principal_value = principal_value
        self.attributes = attributes

    def __getattr__(self, name):
        if self.attributes.has_key(name):
            return self.attributes[name]
        else:
            raise AttributeError, name

    def __str__(self):

        """
        Format the header value object, producing a string suitable for the
        response header field.
        """

        l = []
        if self.principal_value:
            l.append(self.principal_value)
            for name, value in self.attributes.items():
                l.append("; ")
                l.append("%s=%s" % (name, value))

        # Make sure that only ASCII is used.

        return "".join(l).encode("US-ASCII")

class ContentType(HeaderValue):

    "A container for content type information."

    def __init__(self, media_type, charset=None, **attributes):

        """
        Initialise the container with the given 'media_type', an optional
        'charset', and optional keyword attributes representing the key=value
        pairs which qualify content types.
        """

        if charset is not None:
            attributes["charset"] = charset
        HeaderValue.__init__(self, media_type, **attributes)

    def __getattr__(self, name):
        if name == "media_type":
            return self.principal_value
        elif name == "charset":
            return self.attributes.get("charset")
        elif self.attributes.has_key(name):
            return self.attributes[name]
        else:
            raise AttributeError, name

class Cookie:

    """
    A simple cookie class for frameworks which do not return cookies in
    structured form. Instances of this class contain the following attributes:

      * name - the name associated with the cookie
      * value - the value retained by the cookie
    """

    def __init__(self, name, value):
        self.name = name
        self.value = value

class FileContent:

    """
    A simple class representing uploaded file content. This is useful in holding
    metadata as well as being an indicator of such content in environments such
    as Jython where it is not trivial to differentiate between plain strings and
    Unicode in a fashion also applicable to CPython.

    Instances of this class contain the following attributes:

      * content - a plain string containing the contents of the uploaded file
      * headers - a dictionary containing the headers associated with the
                  uploaded file
    """

    def __init__(self, content, headers=None):

        """
        Initialise the object with 'content' and optional 'headers' describing
        the content.
        """

        self.content = content
        self.headers = headers or {}

    def __str__(self):
        return self.content

def parse_header_value(header_class, header_value_str):

    """
    Create an object of the given 'header_class' by determining the details
    of the given 'header_value_str' - a string containing the value of a
    particular header.
    """

    if header_value_str is None:
        return header_class(None)

    l = header_value_str.split(";")
    attributes = {}

    # Find the attributes.

    principal_value, attributes_str = l[0].strip(), l[1:]

    for attribute_str in attributes_str:
        t = attribute_str.split("=")
        if len(t) > 1:
            name, value = t[0].strip(), t[1].strip()
            attributes[name] = value

    return header_class(principal_value, **attributes)

def parse_headers(headers):

    """
    Parse the given 'headers' dictionary (containing names mapped to values),
    returing a dictionary mapping names to HeaderValue objects.
    """

    new_headers = {}
    for name, value in headers.items():
        new_headers[name] = parse_header_value(HeaderValue, value)
    return new_headers

def get_storage_items(storage_body):

    """
    Return the items (2-tuples of the form key, values) from the 'storage_body'.
    This is used in conjunction with FieldStorage objects.
    """

    items = []
    for key in storage_body.keys():
        items.append((key, storage_body[key]))
    return items

def get_body_fields(field_items, encoding):

    """
    Returns a dictionary mapping field names to lists of field values for all
    entries in the given 'field_items' (2-tuples of the form key, values) using
    the given 'encoding'.
    This is used in conjunction with FieldStorage objects.
    """

    fields = {}

    for field_name, field_values in field_items:
        field_name = decode_value(field_name, encoding)

        if type(field_values) == type([]):
            fields[field_name] = []
            for field_value in field_values:
                fields[field_name].append(get_body_field_or_file(field_value, encoding))
        else:
            fields[field_name] = [get_body_field_or_file(field_values, encoding)]

    return fields

def get_body_field_or_file(field_value, encoding):

    """
    Returns the appropriate value for the given 'field_value' either for a
    normal form field (thus employing the given 'encoding') or for a file
    upload field (returning a plain string).
    """

    if hasattr(field_value, "headers") and field_value.headers.has_key("content-type"):

        # Detect stray FileUpload objects (eg. with Zope).

        if hasattr(field_value, "read"):
            return FileContent(field_value.read(), parse_headers(field_value.headers))
        else:
            return FileContent(field_value.value, parse_headers(field_value.headers))
    else:
        return get_body_field(field_value, encoding)

def get_body_field(field_str, encoding):

    """
    Returns the appropriate value for the given 'field_str' string using the
    given 'encoding'.
    """

    # Detect stray FieldStorage objects (eg. with Webware).

    if hasattr(field_str, "value"):
        return get_body_field(field_str.value, encoding)
    else:
        return decode_value(field_str, encoding)

def decode_value(s, encoding):
    if encoding is not None:
        try:
            return unicode(s, encoding)
        except UnicodeError:
            pass
    # NOTE: Hacks to permit graceful failure.
    return unicode(s, "iso-8859-1")

def get_fields_from_query_string(query_string, decoder):

    """
    Returns a dictionary mapping field names to lists of values for the data
    encoded in the given 'query_string'. Use the given 'decoder' function or
    method to process the URL-encoded values.
    """

    fields = {}

    for pair in query_string.split("&"):
        t = pair.split("=")
        name = decoder(t[0])

        if len(t) == 2:
            value = decoder(t[1])
        else:
            value = ""

        # NOTE: Remove empty names.

        if name:
            if not fields.has_key(name):
                fields[name] = []
            fields[name].append(value)

    return fields

def filter_fields(all_fields, fields_from_path):

    """
    Taking items from the 'all_fields' dictionary, produce a new dictionary
    which does not contain items from the 'fields_from_path' dictionary.
    Return a new dictionary.
    """

    fields = {}
    for field_name, field_values in all_fields.items():

        # Find the path values for this field (for filtering below).

        if fields_from_path.has_key(field_name):
            field_from_path_values = fields_from_path[field_name]
            if type(field_from_path_values) != type([]):
                field_from_path_values = [field_from_path_values]
        else:
            field_from_path_values = []

        fields[field_name] = []
        for field_value in field_values:

            # Filter path values.

            if field_value not in field_from_path_values:
                fields[field_name].append(field_value)

        # Remove filtered fields.

        if fields[field_name] == []:
            del fields[field_name]

    return fields

# vim: tabstop=4 expandtab shiftwidth=4
