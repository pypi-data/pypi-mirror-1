#!/usr/bin/env python

"""
Response helper classes.
"""

class ConvertingStream:

    """
    A converting stream which converts Unicode text to plain strings.
    """

    def __init__(self, stream, encoding):

        "Set the actual response 'stream' and the desired output 'encoding'."

        self.stream = stream
        self.encoding = encoding

    def write(self, text):

        "Write the given 'text', either a plain string or a Unicode object."

        if type(text) == type(u""):
            self.stream.write(text.encode(self.encoding))
        else:
            self.stream.write(text)

# vim: tabstop=4 expandtab shiftwidth=4
