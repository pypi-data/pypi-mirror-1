#!/usr/bin/env python

"""
Zope classes.

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

--------

In places this resembles CGI a lot because Zope seems to recycle a lot of that
baggage.
"""

import WebStack.Generic
from WebStack.Helpers import Environment
from WebStack.Helpers.Request import Cookie, get_body_field_or_file, decode_value, filter_fields
from WebStack.Helpers.Response import ConvertingStream
from WebStack.Helpers.Auth import UserInfo
import cgi

class Transaction(WebStack.Generic.Transaction):

    """
    Zope transaction interface.
    """

    def __init__(self, request, adapter):

        """
        Initialise the transaction with the Zope 'request' object and the
        'adapter' which created this transaction.
        """

        self.request = request
        self.response = request.RESPONSE
        self.adapter = adapter

        # Cached information.

        self._fields = None

        # Attributes which may be changed later.

        self.content_type = None
        self.user = None
        self.path_info = None

    # Server-related methods.

    def get_server_name(self):

        "Returns the server name."

        return self.request.environ.get("SERVER_NAME")

    def get_server_port(self):

        "Returns the server port as a string."

        return self.request.environ.get("SERVER_PORT")

    # Request-related methods.

    def get_request_stream(self):

        """
        Returns the request stream for the transaction.

        NOTE: This method actually rewinds to the start of the stream, since
        NOTE: Zope likes to read everything automatically.
        """

        # NOTE: Possibly not safe.

        stdin = self.request.stdin
        stdin.seek(0)
        return stdin

    def get_request_method(self):

        """
        Returns the request method.
        """

        return self.request.environ.get("REQUEST_METHOD")

    def get_headers(self):

        """
        Returns all request headers as a dictionary-like object mapping header
        names to values.
        """

        return Environment.get_headers(self.request.environ)

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

        return self.parse_content_type(self.request.environ.get("CONTENT_TYPE"))

    def get_content_charsets(self):

        """
        Returns the character set preferences.

        NOTE: Not decently supported.
        """

        return self.parse_content_preferences(None)

    def get_content_languages(self):

        """
        Returns extracted language information from the transaction.

        NOTE: Not decently supported.
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

        # NOTE: Based on WebStack.CGI.get_path.

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

        # NOTE: Based on WebStack.CGI.get_path.

        path = decode_value(self.request.environ.get("SCRIPT_NAME") or "", encoding)
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

        product_path = "/".join(self.adapter.getPhysicalPath())
        path_info = self.request.environ.get("PATH_INFO") or ""
        real_path_info = path_info[len(product_path):]
        return decode_value(real_path_info, encoding)

    def get_query_string(self):

        """
        Returns the query string from the path in the request.
        """

        return self.request.environ.get("QUERY_STRING") or ""

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
        for name, values in cgi.parse_qs(self.get_query_string()).items():
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
        or a plain string (representing a file upload form field, for example).
        """

        all_fields = self._get_fields(encoding)
        fields_from_path = self.get_fields_from_path()
        return filter_fields(all_fields, fields_from_path)

    def _get_fields(self, encoding=None):
        if self._fields is not None:
            return self._fields

        encoding = encoding or self.get_content_type().charset or self.default_charset
        self._fields = {}

        for field_name, field_values in self.request.form.items():
            field_name = decode_value(field_name, encoding)

            # Find the body values.

            if type(field_values) == type([]):
                self._fields[field_name] = []
                for field_str in field_values:
                    self._fields[field_name].append(get_body_field_or_file(field_str, encoding))
            else:
                self._fields[field_name] = [get_body_field_or_file(field_values, encoding)]

        return self._fields

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
        or a plain string (representing a file upload form field, for example).

        Where a given field name is used in both the path and message body to
        specify values, the values from both sources will be combined into a
        single list associated with that field name.
        """

        # NOTE: Zope seems to provide only body fields upon POST requests.

        if self.get_request_method() == "GET":
            return self._get_fields(encoding)
        else:
            fields = {}
            fields.update(self.get_fields_from_path())
            for name, values in self._get_fields(encoding).items():
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

        auth_header = self.request._auth
        if auth_header:
            return UserInfo(auth_header).username
        else:
            return None

    def get_cookies(self):

        """
        Obtains cookie information from the request.

        Returns a dictionary mapping cookie names to cookie objects.
        """

        return self.process_cookies(self.request.cookies, using_strings=1)

    def get_cookie(self, cookie_name):

        """
        Obtains cookie information from the request.

        Returns a cookie object for the given 'cookie_name' or None if no such
        cookie exists.
        """

        value = self.request.cookies.get(self.encode_cookie_value(cookie_name))
        if value is not None:
            return Cookie(cookie_name, self.decode_cookie_value(value))
        else:
            return None

    # Response-related methods.

    def get_response_stream(self):

        """
        Returns the response stream for the transaction.
        """

        # Unicode can upset this operation. Using either the specified charset
        # or a default encoding.

        encoding = self.get_response_stream_encoding()
        return ConvertingStream(self.response, encoding)

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

        return self.response.status

    def set_response_code(self, response_code):

        """
        Set the 'response_code' using a numeric constant defined in the HTTP
        specification.
        """

        self.response.setStatus(response_code)

    def set_header_value(self, header, value):

        """
        Set the HTTP 'header' with the given 'value'.
        """

        self.response.setHeader(header, value)

    def set_content_type(self, content_type):

        """
        Sets the 'content_type' for the response.
        """

        self.content_type = content_type
        self.response.setHeader("Content-Type", str(content_type))

    # Higher level response-related methods.

    def set_cookie(self, cookie):

        """
        Stores the given 'cookie' object in the response.
        """

        self.set_cookie_value(cookie.name, cookie.value)

    def set_cookie_value(self, name, value, path=None, expires=None):

        """
        Stores a cookie with the given 'name' and 'value' in the response.

        The optional 'path' is a string which specifies the scope of the cookie,
        and the optional 'expires' parameter is a value compatible with the
        time.time function, and indicates the expiry date/time of the cookie.
        """

        self.response.setCookie(self.encode_cookie_value(name), self.encode_cookie_value(value))

    def delete_cookie(self, cookie_name):

        """
        Adds to the response a request that the cookie with the given
        'cookie_name' be deleted/discarded by the client.
        """

        self.response.expireCookie(self.encode_cookie_value(cookie_name))

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

        return self.request.SESSION

    def expire_session(self):

        """
        Expires any session established according to information provided in the
        transaction.
        """

        self.request.SESSION.invalidate()

# vim: tabstop=4 expandtab shiftwidth=4
