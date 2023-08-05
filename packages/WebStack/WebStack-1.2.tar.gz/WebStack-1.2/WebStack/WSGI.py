#!/usr/bin/env python

"""
WSGI classes.

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

import WebStack.Generic
import os, sys
from WebStack.Helpers.Request import MessageBodyStream, get_body_fields, decode_value, get_storage_items, Cookie
from WebStack.Helpers.Response import ConvertingStream
from WebStack.Helpers.Auth import UserInfo
from WebStack.Helpers.Session import SessionStore
from WebStack.Helpers import Environment
from cgi import parse_qs, FieldStorage
from Cookie import SimpleCookie
from StringIO import StringIO

class Transaction(WebStack.Generic.Transaction):

    """
    WSGI transaction interface.
    """

    def __init__(self, env):

        """
        Initialise the transaction using the given WSGI environment 'env'.
        """

        self.env = env

        # Other attributes of interest in instances of this class.

        self.content_type = None
        self.response_code = 200
        self.content = StringIO()
        self.headers_out = {}
        self.cookies_out = SimpleCookie()

        # Define the incoming cookies.

        self.cookies_in = SimpleCookie(self.env.get("HTTP_COOKIE"))

        # Cached information.

        self.storage_body = None

        # Special objects retained throughout the transaction.

        self.session_store = None

    def commit(self):

        """
        A special method, synchronising the transaction with framework-specific
        objects.
        """

        # Close the session store.

        if self.session_store is not None:
            self.session_store.close()

    def rollback(self):

        """
        A special method, partially synchronising the transaction with
        framework-specific objects, but discarding previously emitted content
        that is to be replaced by an error message.
        """

        self.content = StringIO()
        self.headers_out = {}
        self.cookies_out = SimpleCookie()

    def get_wsgi_headers(self):
        wsgi_headers = []

        if self.content_type is not None:
            wsgi_headers.append(("Content-type", str(self.content_type)))

        for header, value in self.headers_out.items():
            wsgi_headers.append(
                (self.format_header_value(header), self.format_header_value(value))
            )

        # NOTE: Nasty deconstruction of Morsel values.

        for value in self.cookies_out.values():
            parts = str(value).split(": ")
            wsgi_headers.append(
                (parts[0], ": ".join(parts[1:]))
            )

        return wsgi_headers

    def get_wsgi_content(self):
        self.content.seek(0)
        return self.content.read()

    # Server-related methods.

    def get_server_name(self):

        "Returns the server name."

        return self.env.get("SERVER_NAME")

    def get_server_port(self):

        "Returns the server port as a string."

        return self.env.get("SERVER_PORT")

    # Request-related methods.

    def get_request_stream(self):

        """
        Returns the request stream for the transaction.
        """

        return self.env["wsgi.input"]

    def get_request_method(self):

        """
        Returns the request method.
        """

        return self.env.get("REQUEST_METHOD")

    def get_headers(self):

        """
        Returns all request headers as a dictionary-like object mapping header
        names to values.
        """

        return Environment.get_headers(self.env)

    def get_header_values(self, key):

        """
        Returns a list of all request header values associated with the given
        'key'. Note that according to RFC 2616, 'key' is treated as a
        case-insensitive string.
        """

        return self.convert_to_list(self.get_headers().get(key))

    def get_content_type(self):

        """
        Returns the content type specified on the request, along with the
        charset employed.
        """

        return self.parse_content_type(self.env.get("CONTENT_TYPE"))

    def get_content_charsets(self):

        """
        Returns the character set preferences.
        """

        return self.parse_content_preferences(None)

    def get_content_languages(self):

        """
        Returns extracted language information from the transaction.
        """

        return self.parse_content_preferences(None)

    def get_path(self, encoding=None):

        """
        Returns the entire path from the request as a Unicode object. Any "URL
        encoded" character values in the part of the path before the query
        string will be decoded and presented as genuine characters; the query
        string will remain "URL encoded", however.

        If the optional 'encoding' is set, use that in preference to the default
        encoding to convert the path into a form not containing "URL encoded"
        character values.
        """

        path = self.get_path_without_query(encoding)
        qs = self.get_query_string()
        if qs:
            return path + "?" + qs
        else:
            return path

    def get_path_without_query(self, encoding=None):

        """
        Returns the entire path from the request minus the query string as a
        Unicode object containing genuine characters (as opposed to "URL
        encoded" character values).

        If the optional 'encoding' is set, use that in preference to the default
        encoding to convert the path into a form not containing "URL encoded"
        character values.
        """

        path = decode_value(self.env.get("SCRIPT_NAME") or "", encoding)
        path += self.get_path_info(encoding)
        return path

    def get_path_info(self, encoding=None):

        """
        Returns the "path info" (the part of the URL after the resource name
        handling the current request) from the request as a Unicode object
        containing genuine characters (as opposed to "URL encoded" character
        values).

        If the optional 'encoding' is set, use that in preference to the default
        encoding to convert the path into a form not containing "URL encoded"
        character values.
        """

        return decode_value(self.env.get("PATH_INFO") or "", encoding)

    def get_query_string(self):

        """
        Returns the query string from the path in the request.
        """

        return self.env.get("QUERY_STRING") or ""

    # Higher level request-related methods.

    def get_fields_from_path(self, encoding=None):

        """
        Extracts fields (or request parameters) from the path specified in the
        transaction. The underlying framework may refuse to supply fields from
        the path if handling a POST transaction. The optional 'encoding'
        parameter specifies the character encoding of the query string for cases
        where the default encoding is to be overridden.

        Returns a dictionary mapping field names to lists of values (even if a
        single value is associated with any given field name).
        """

        fields = {}
        for name, values in parse_qs(self.get_query_string(), keep_blank_values=1).items():
            name = decode_value(name, encoding)
            fields[name] = []
            for value in values:
                value = decode_value(value, encoding)
                fields[name].append(value)
        return fields

    def get_fields_from_body(self, encoding=None):

        """
        Extracts fields (or request parameters) from the message body in the
        transaction. The optional 'encoding' parameter specifies the character
        encoding of the message body for cases where no such information is
        available, but where the default encoding is to be overridden.

        Returns a dictionary mapping field names to lists of values (even if a
        single value is associated with any given field name). Each value is
        either a Unicode object (representing a simple form field, for example)
        or a WebStack.Helpers.Request.FileContent object (representing a file
        upload form field).
        """

        encoding = encoding or self.get_content_type().charset or self.default_charset

        if self.storage_body is None:
            self.storage_body = FieldStorage(fp=self.get_request_stream(),
                headers={"content-type" : str(self.get_content_type())},
                environ={"REQUEST_METHOD" : self.get_request_method()},
                keep_blank_values=1)

        # Avoid strange design issues with FieldStorage by checking the internal
        # field list directly.

        fields = {}
        if self.storage_body.list is not None:

            # Traverse the storage, finding each field value.

            fields = get_body_fields(get_storage_items(self.storage_body), encoding)

        return fields

    def get_fields(self, encoding=None):

        """
        Extracts fields (or request parameters) from both the path specified in
        the transaction as well as the message body. The optional 'encoding'
        parameter specifies the character encoding of the message body for cases
        where no such information is available, but where the default encoding
        is to be overridden.

        Returns a dictionary mapping field names to lists of values (even if a
        single value is associated with any given field name). Each value is
        either a Unicode object (representing a simple form field, for example)
        or a WebStack.Helpers.Request.FileContent object (representing a file
        upload form field).

        Where a given field name is used in both the path and message body to
        specify values, the values from both sources will be combined into a
        single list associated with that field name.
        """

        # Combine the two sources.

        fields = {}
        fields.update(self.get_fields_from_path())
        for name, values in self.get_fields_from_body(encoding).items():
            if not fields.has_key(name):
                fields[name] = values
            else:
                fields[name] += values
        return fields

    def get_user(self):

        """
        Extracts user information from the transaction.

        Returns a username as a string or None if no user is defined.
        """

        if self.user is not None:
            return self.user
        else:
            return self.env.get("REMOTE_USER")

    def get_cookies(self):

        """
        Obtains cookie information from the request.

        Returns a dictionary mapping cookie names to cookie objects.
        """

        return self.process_cookies(self.cookies_in)

    def get_cookie(self, cookie_name):

        """
        Obtains cookie information from the request.

        Returns a cookie object for the given 'cookie_name' or None if no such
        cookie exists.
        """

        cookie = self.cookies_in.get(self.encode_cookie_value(cookie_name))
        if cookie is not None:
            return Cookie(cookie_name, self.decode_cookie_value(cookie.value))
        else:
            return None

    # Response-related methods.

    def get_response_stream(self):

        """
        Returns the response stream for the transaction.
        """

        # Return a stream which is later emptied into the real stream.
        # Unicode can upset this operation. Using either the specified charset
        # or a default encoding.

        encoding = self.get_response_stream_encoding()
        return ConvertingStream(self.content, encoding)

    def get_response_stream_encoding(self):

        """
        Returns the response stream encoding.
        """

        if self.content_type:
            encoding = self.content_type.charset
        else:
            encoding = None
        return encoding or self.default_charset

    def get_response_code(self):

        """
        Get the response code associated with the transaction. If no response
        code is defined, None is returned.
        """

        return self.response_code

    def set_response_code(self, response_code):

        """
        Set the 'response_code' using a numeric constant defined in the HTTP
        specification.
        """

        self.response_code = response_code

    def set_header_value(self, header, value):

        """
        Set the HTTP 'header' with the given 'value'.
        """

        # The header is not written out immediately due to the buffering in use.

        self.headers_out[header] = value

    def set_content_type(self, content_type):

        """
        Sets the 'content_type' for the response.
        """

        # The content type has to be written as a header, before actual content,
        # but after the response line. This means that some kind of buffering is
        # required. Hence, we don't write the header out immediately.

        self.content_type = content_type

    # Higher level response-related methods.

    def set_cookie(self, cookie):

        """
        Stores the given 'cookie' object in the response.
        """

        # NOTE: If multiple cookies of the same name could be specified, this
        # NOTE: could need changing.

        self.set_cookie_value(cookie.name, cookie.value)

    def set_cookie_value(self, name, value, path=None, expires=None):

        """
        Stores a cookie with the given 'name' and 'value' in the response.

        The optional 'path' is a string which specifies the scope of the cookie,
        and the optional 'expires' parameter is a value compatible with the
        time.time function, and indicates the expiry date/time of the cookie.
        """

        name = self.encode_cookie_value(name)
        self.cookies_out[name] = self.encode_cookie_value(value)
        if path is not None:
            self.cookies_out[name]["path"] = path
        if expires is not None:
            self.cookies_out[name]["expires"] = expires

    def delete_cookie(self, cookie_name):

        """
        Adds to the response a request that the cookie with the given
        'cookie_name' be deleted/discarded by the client.
        """

        # Create a special cookie, given that we do not know whether the browser
        # has been sent the cookie or not.
        # NOTE: Magic discovered in Webware.

        name = self.encode_cookie_value(cookie_name)
        self.cookies_out[name] = ""
        self.cookies_out[name]["path"] = "/"
        self.cookies_out[name]["expires"] = 0
        self.cookies_out[name]["max-age"] = 0

    # Session-related methods.

    def get_session(self, create=1):

        """
        Gets a session corresponding to an identifier supplied in the
        transaction.

        If no session has yet been established according to information
        provided in the transaction then the optional 'create' parameter
        determines whether a new session will be established.

        Where no session has been established and where 'create' is set to 0
        then None is returned. In all other cases, a session object is created
        (where appropriate) and returned.
        """

        # NOTE: Requires configuration.

        if self.session_store is None:
            self.session_store = SessionStore(self, "WebStack-sessions")
        return self.session_store.get_session(create)

    def expire_session(self):

        """
        Expires any session established according to information provided in the
        transaction.
        """

        # NOTE: Requires configuration.

        if self.session_store is None:
            self.session_store = SessionStore(self, "WebStack-sessions")
        self.session_store.expire_session()

# vim: tabstop=4 expandtab shiftwidth=4
