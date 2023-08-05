#!/usr/bin/env python

"""
Response helper classes.

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
