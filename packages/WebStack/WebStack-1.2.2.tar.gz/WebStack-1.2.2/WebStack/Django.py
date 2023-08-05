#!/usr/bin/env python

"""
Django classes.

Copyright (C) 2006, 2007 Paul Boddie <paul@boddie.org.uk>

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
from WebStack.Helpers import Environment
from WebStack.Helpers.Request import decode_value, FileContent, Cookie
from WebStack.Helpers.Response import ConvertingStream
from WebStack.Helpers.Auth import UserInfo
from django.http import HttpResponse
from StringIO import StringIO

class Transaction(WebStack.Generic.Transaction):

    """
    Django transaction interface.
    """

    def __init__(self, request):

        """
        Initialise the transaction with the Django 'request' object.
        """

        self.request = request

        # Attributes which may be changed later.

        self.content_type = None

        # The response is created here but must be modified later.
        # NOTE: It is unfortunate that Django wants to initialise the response
        # NOTE: with the content type immediately.

        self.response = HttpResponse()
        self.content = StringIO()

    def commit(self):

        "Commit the transaction by finishing some things off."

        self.content.seek(0)
        self.response.content = self.content.read()

    def rollback(self):

        """
        A special method, partially synchronising the transaction with
        framework-specific objects, but discarding previously emitted content
        that is to be replaced by an error message.
        """

        self.response = HttpResponse()
        self.content = StringIO()

    # Server-related methods.

    def get_server_name(self):

        "Returns the server name."

        return self.request.META.get("SERVER_NAME")

    def get_server_port(self):

        "Returns the server port as a string."

        return self.request.META.get("SERVER_PORT")

    # Request-related methods.

    def get_request_stream(self):

        """
        Returns the request stream for the transaction.
        """

        # Unfortunately, we get given a string from Django. Thus, we need to
        # create a stream around that string.

        return StringIO(self.request.raw_post_data)

    def get_request_method(self):

        """
        Returns the request method.
        """

        return self.request.META.get("REQUEST_METHOD")

    def get_headers(self):

        """
        Returns all request headers as a dictionary-like object mapping header
        names to values.
        """

        return Environment.get_headers(self.request.META)

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

        return self.parse_content_type(self.request.META.get("CONTENT_TYPE"))

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

        encoding = encoding or self.default_charset

        return decode_value(self.request.get_full_path(), encoding)

    def get_path_without_query(self, encoding=None):

        """
        Returns the entire path from the request minus the query string as a
        Unicode object containing genuine characters (as opposed to "URL
        encoded" character values).

        If the optional 'encoding' is set, use that in preference to the default
        encoding to convert the path into a form not containing "URL encoded"
        character values.
        """

        path = self.get_path(encoding)
        return path.split("?")[0]

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

        encoding = encoding or self.default_charset

        path_info = self.request.META.get("PATH_INFO") or ""
        return decode_value(path_info, encoding)

    def get_query_string(self):

        """
        Returns the query string from the path in the request.
        """

        return self.request.META.get("QUERY_STRING") or ""

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

        return self._get_fields(self.request.GET, encoding)

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

        fields = {}
        self._update_fields(fields, self._get_fields(self.request.POST, encoding))
        self._update_fields(fields, self._get_files())
        return fields

    def _get_fields(self, source, encoding=None):

        encoding = encoding or self.get_content_type().charset or self.default_charset

        fields = {}
        for name in source.keys():
            name = decode_value(name, encoding)
            fields[name] = []
            for value in source.getlist(name):
                value = decode_value(value, encoding)
                fields[name].append(value)
        return fields

    def _get_files(self):
        files = {}
        for name, file in self.request.FILES.items():
            files[name] = [FileContent(file.get("content", ""), {
                "Content-Type" : file.get("content-type", ""),
                "Content-Disposition" : "%s; filename=%s" % (name, file.get("filename", ""))
                })]
        return files

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

        fields = {}
        fields.update(self.get_fields_from_path(encoding))
        self._update_fields(fields, self.get_fields_from_body(encoding))
        return fields

    def _update_fields(self, fields, new_fields):
        for name, values in new_fields.items():
            if not fields.has_key(name):
                fields[name] = values
            else:
                fields[name] += values

    def get_user(self):

        """
        Extracts user information from the transaction.

        Returns a username as a string or None if no user is defined.
        """

        if self.user is not None:
            return self.user

        auth_header = self.get_headers().get("authorization")
        if auth_header:
            return UserInfo(auth_header).username
        else:
            return None

    def get_cookies(self):

        """
        Obtains cookie information from the request.

        Returns a dictionary mapping cookie names to cookie objects.
        """

        return self.process_cookies(self.request.COOKIES, using_strings=1)

    def get_cookie(self, cookie_name):

        """
        Obtains cookie information from the request.

        Returns a cookie object for the given 'cookie_name' or None if no such
        cookie exists.
        """

        value = self.request.COOKIES.get(self.encode_cookie_value(cookie_name))
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

        return self.response.status_code

    def set_response_code(self, response_code):

        """
        Set the 'response_code' using a numeric constant defined in the HTTP
        specification.
        """

        self.response.status_code = response_code

    def set_header_value(self, header, value):

        """
        Set the HTTP 'header' with the given 'value'.
        """

        self.response.headers[header] = value

    def set_content_type(self, content_type):

        """
        Sets the 'content_type' for the response.
        """

        self.content_type = content_type
        self.response.headers["Content-Type"] = str(content_type)

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

        self.response.set_cookie(self.encode_cookie_value(name), self.encode_cookie_value(value), path=path, expires=expires)

    def delete_cookie(self, cookie_name):

        """
        Adds to the response a request that the cookie with the given
        'cookie_name' be deleted/discarded by the client.
        """

        #self.response.delete_cookie(self.encode_cookie_value(cookie_name))

        # Create a special cookie, given that we do not know whether the browser
        # has been sent the cookie or not.
        # NOTE: Magic discovered in Webware.

        name = self.encode_cookie_value(cookie_name)
        self.response.set_cookie(name, "", path="/", expires=0, max_age=0)

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

        # NOTE: Dubious access to a more dictionary-like object.

        if create:
            self.request.session["_hack"] = "created"
        return Session(self.request.session)

    def expire_session(self):

        """
        Expires any session established according to information provided in the
        transaction.
        """

        # NOTE: Not trivially supported!

class Session:
    def __init__(self, session):
        self.session = session
    def __getattr__(self, name):
        return getattr(self.session, name)
    def keys(self):
        return self.session._session.keys()
    def values(self):
        return self.session._session.values()
    def items(self):
        return self.session._session.items()

# vim: tabstop=4 expandtab shiftwidth=4
