#!/usr/bin/env python

"""
Request helper classes.
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

class Cookie:

    """
    A simple cookie class for frameworks which do not return cookies in
    structured form.
    """

    def __init__(self, name, value):
        self.name = name
        self.value = value

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
        if type(field_values) == type([]):
            fields[field_name] = []
            for field_value in field_values:
                fields[field_name].append(get_body_field(field_value.value, encoding))
        else:
            fields[field_name] = [get_body_field(field_values.value, encoding)]

    return fields

def get_body_field(field_str, encoding):

    """
    Returns the appropriate value for the given 'field_str' string using the
    given 'encoding'.
    """

    # Detect stray FieldStorage objects (eg. with Webware) or stray FileUpload
    # objects (eg. with Zope).

    if hasattr(field_str, "value"):
        return get_body_field(field_str.value, encoding)
    elif hasattr(field_str, "read"):
        return field_str.read()
    elif encoding is not None:
        try:
            return unicode(field_str, encoding)
        except UnicodeError:
            # NOTE: Hacks to permit graceful failure.
            try:
                return unicode(field_str, "iso-8859-1")
            except UnicodeError:
                return u""
    else:
        return field_str

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
