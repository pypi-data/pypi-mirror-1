#!/usr/bin/env python

"""
Generic Web framework interfaces.

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

The WebStack architecture consists of the following layers:

  * Framework - The underlying Web framework implementation.
  * Adapter   - Code operating under the particular framework which creates
                WebStack abstractions and issues them to the application.
  * Resources - Units of functionality operating within the hosted Web
                application.

Resources can act as both content producers within an application and as request
dispatchers to other resources; in the latter role, they may be referred to as
directors.
"""

import urllib
from WebStack.Helpers.Request import Cookie, parse_header_value, ContentType, HeaderValue

class EndOfResponse(Exception):

    "An exception which signals the end of a response."

    pass

class Transaction:

    """
    A generic transaction interface containing framework-specific methods to be
    overridden.
    """

    # The default charset ties output together with body field interpretation.

    default_charset = "iso-8859-1"

    def commit(self):

        """
        A special method, synchronising the transaction with framework-specific
        objects.
        """

        pass

    # Utility methods.

    def parse_header_value(self, header_class, header_value_str):

        """
        Create an object of the given 'header_class' by determining the details
        of the given 'header_value_str' - a string containing the value of a
        particular header.
        """

        # Now uses the WebStack.Helpers.Request function of the same name.

        return parse_header_value(header_class, header_value_str)

    def parse_content_type(self, content_type_field):

        """
        Parse the given 'content_type_field' - a value found comparable to that
        found in an HTTP request header for "Content-Type".
        """

        return self.parse_header_value(ContentType, content_type_field)

    def format_header_value(self, value):

        """
        Format the given header 'value'. Typically, this just ensures the usage
        of US-ASCII.
        """

        return value.encode("US-ASCII")

    def encode_cookie_value(self, value):

        """
        Encode the given cookie 'value'. This ensures the usage of US-ASCII
        through the encoding of Unicode objects as URL-encoded UTF-8 text.
        """

        return urllib.quote(value.encode("UTF-8")).encode("US-ASCII")

    def decode_cookie_value(self, value):

        """
        Decode the given cookie 'value'.
        """

        return unicode(urllib.unquote(value), "UTF-8")

    def process_cookies(self, cookie_dict, using_strings=0):

        """
        Process the given 'cookie_dict', returning a dictionary mapping cookie names
        to cookie objects where the names and values have been decoded from the form
        used in the cookies retrieved from the request.

        The optional 'using_strings', if set to 1, treats the 'cookie_dict' as a
        mapping of cookie names to values.
        """

        cookies = {}
        for name in cookie_dict.keys():
            if using_strings:
                value = cookie_dict[name]
            else:
                cookie = cookie_dict[name]
                value = cookie.value
            cookie_name = self.decode_cookie_value(name)
            cookie_value = self.decode_cookie_value(value)
            cookies[cookie_name] = Cookie(cookie_name, cookie_value)
        return cookies

    def parse_content_preferences(self, accept_preference):

        """
        Returns the preferences as requested by the user agent. The preferences are
        returned as a list of codes in the same order as they appeared in the
        appropriate environment variable. In other words, the explicit weighting
        criteria are ignored.

        As the 'accept_preference' parameter, values for language and charset
        preferences are appropriate.
        """

        if accept_preference is None:
            return []

        accept_defs = accept_preference.split(",")
        accept_prefs = []
        for accept_def in accept_defs:
            t = accept_def.split(";")
            if len(t) >= 1:
                accept_prefs.append(t[0].strip())
        return accept_prefs

    def convert_to_list(self, value):

        """
        Returns a single element list containing 'value' if it is not itself a list, a
        tuple, or None. If 'value' is a list then it is itself returned; if 'value' is a
        tuple then a new list containing the same elements is returned; if 'value' is None
        then an empty list is returned.
        """

        if type(value) == type([]):
            return value
        elif type(value) == type(()):
            return list(value)
        elif value is None:
            return []
        else:
            return [value]

    # Public utility methods.

    def decode_path(self, path, encoding=None):

        """
        From the given 'path', use the optional 'encoding' (if specified) to decode the
        information and convert it to Unicode. Upon failure for a specified 'encoding'
        or where 'encoding' is not specified, use the default character encoding to
        perform the conversion.

        Returns the 'path' as a Unicode value without "URL encoded" character values.
        """

        unquoted_path = urllib.unquote(path)
        if encoding is not None:
            try:
                return unicode(unquoted_path, encoding)
            except UnicodeError:
                pass
        return unicode(unquoted_path, self.default_charset)

    def encode_path(self, path, encoding=None):

        """
        Encode the given 'path', using the optional 'encoding' (if specified) or the
        default encoding where 'encoding' is not specified, and produce a suitable "URL
        encoded" string.
        """

        if encoding is not None:
            return urllib.quote(path.encode(encoding))
        else:
            return urllib.quote(path.encode(self.default_charset))

    # Server-related methods.

    def get_server_name(self):

        "Returns the server name."

        raise NotImplementedError, "get_server_name"

    def get_server_port(self):

        "Returns the server port as a string."

        raise NotImplementedError, "get_server_port"

    # Request-related methods.

    def get_request_stream(self):

        """
        Returns the request stream for the transaction.
        """

        raise NotImplementedError, "get_request_stream"

    def get_request_method(self):

        """
        Returns the request method.
        """

        raise NotImplementedError, "get_request_method"

    def get_headers(self):

        """
        Returns all request headers as a dictionary-like object mapping header
        names to values.
        """

        raise NotImplementedError, "get_headers"

    def get_header_values(self, key):

        """
        Returns a list of all request header values associated with the given
        'key'. Note that according to RFC 2616, 'key' is treated as a
        case-insensitive string.
        """

        raise NotImplementedError, "get_header_values"

    def get_content_type(self):

        """
        Returns the content type specified on the request, along with the
        charset employed.
        """

        raise NotImplementedError, "get_content_type"

    def get_content_charsets(self):

        """
        Returns the character set preferences.
        """

        raise NotImplementedError, "get_content_charsets"

    def get_content_languages(self):

        """
        Returns extracted language information from the transaction.
        """

        raise NotImplementedError, "get_content_languages"

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

        raise NotImplementedError, "get_path"

    def get_path_without_query(self, encoding=None):

        """
        Returns the entire path from the request minus the query string as a
        Unicode object containing genuine characters (as opposed to "URL
        encoded" character values).

        If the optional 'encoding' is set, use that in preference to the default
        encoding to convert the path into a form not containing "URL encoded"
        character values.
        """

        raise NotImplementedError, "get_path_without_query"

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

        raise NotImplementedError, "get_path_info"

    def get_path_without_info(self, encoding=None):

        """
        Returns the entire path from the request minus the query string and the
        "path info" as a Unicode object containing genuine characters (as
        opposed to "URL encoded" character values).

        If the optional 'encoding' is set, use that in preference to the default
        encoding to convert the path into a form not containing "URL encoded"
        character values.
        """

        entire_path = self.get_path_without_query(encoding)
        path_info = self.get_path_info(encoding)
        return entire_path[:-len(path_info)]

    def get_query_string(self):

        """
        Returns the query string from the path in the request.
        """

        raise NotImplementedError, "get_query_string"

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

        raise NotImplementedError, "get_fields_from_path"

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

        raise NotImplementedError, "get_fields_from_body"

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

        raise NotImplementedError, "get_fields"

    def get_user(self):

        """
        Extracts user information from the transaction.

        Returns a username as a string or None if no user is defined.
        """

        raise NotImplementedError, "get_user"

    def get_cookies(self):

        """
        Obtains cookie information from the request.

        Returns a dictionary mapping cookie names to cookie objects.
        """

        raise NotImplementedError, "get_cookies"

    def get_cookie(self, cookie_name):

        """
        Obtains cookie information from the request.

        Returns a cookie object for the given 'cookie_name' or None if no such
        cookie exists.
        """

        raise NotImplementedError, "get_cookie"

    # Response-related methods.

    def get_response_stream(self):

        """
        Returns the response stream for the transaction.
        """

        raise NotImplementedError, "get_response_stream"

    def get_response_stream_encoding(self):

        """
        Returns the response stream encoding.
        """

        raise NotImplementedError, "get_response_stream_encoding"

    def get_response_code(self):

        """
        Get the response code associated with the transaction. If no response
        code is defined, None is returned.
        """

        raise NotImplementedError, "get_response_code"

    def set_response_code(self, response_code):

        """
        Set the 'response_code' using a numeric constant defined in the HTTP
        specification.
        """

        raise NotImplementedError, "set_response_code"

    def set_header_value(self, header, value):

        """
        Set the HTTP 'header' with the given 'value'.
        """

        raise NotImplementedError, "set_header_value"

    def set_content_type(self, content_type):

        """
        Sets the 'content_type' for the response.
        """

        raise NotImplementedError, "set_content_type"

    # Higher level response-related methods.

    def set_cookie(self, cookie):

        """
        Stores the given 'cookie' object in the response.
        """

        raise NotImplementedError, "set_cookie"

    def set_cookie_value(self, name, value, path=None, expires=None):

        """
        Stores a cookie with the given 'name' and 'value' in the response.

        The optional 'path' is a string which specifies the scope of the cookie,
        and the optional 'expires' parameter is a value compatible with the
        time.time function, and indicates the expiry date/time of the cookie.
        """

        raise NotImplementedError, "set_cookie_value"

    def delete_cookie(self, cookie_name):

        """
        Adds to the response a request that the cookie with the given
        'cookie_name' be deleted/discarded by the client.
        """

        raise NotImplementedError, "delete_cookie"

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

        raise NotImplementedError, "get_session"

    def expire_session(self):

        """
        Expires any session established according to information provided in the
        transaction.
        """

        raise NotImplementedError, "expire_session"

    # Application-specific methods.

    def set_user(self, username):

        """
        An application-specific method which sets the user information with
        'username' in the transaction. This affects subsequent calls to
        'get_user'.
        """

        self.user = username

    def set_virtual_path_info(self, path_info):

        """
        An application-specific method which sets the 'path_info' in the
        transaction. This affects subsequent calls to 'get_virtual_path_info'.

        Note that the virtual path info should either be an empty string, or it
        should begin with "/" and then (optionally) include other details.
        Virtual path info strings which omit the leading "/" - ie. containing
        things like "xxx" or even "xxx/yyy" - do not really make sense and may
        not be handled correctly by various WebStack components.
        """

        self.path_info = path_info

    def get_virtual_path_info(self, encoding=None):

        """
        An application-specific method which either returns path info set in the
        'set_virtual_path_info' method, or the normal path info found in the
        request.

        If the optional 'encoding' is set, use that in preference to the default
        encoding to convert the path into a form not containing "URL encoded"
        character values.
        """

        if self.path_info is not None:
            return self.path_info
        else:
            return self.get_path_info(encoding)

    def get_processed_virtual_path_info(self, encoding=None):

        """
        An application-specific method which returns the virtual path info that
        is considered "processed"; that is, the part of the path info which is
        not included in the virtual path info.

        If the optional 'encoding' is set, use that in preference to the default
        encoding to convert the path into a form not containing "URL encoded"
        character values.

        Where the virtual path info is identical to the path info, an empty
        string is returned.

        Where the virtual path info is a substring of the path info, the path
        info preceding that substring is returned.

        Where the virtual path info is either an empty string or not a substring
        of the path info, the entire path info is returned.

        Generally, one should expect the following relationship between the path
        info, virtual path info and processed virtual path info:

        path info == processed virtual path info + virtual path info
        """

        real_path_info = self.get_path_info(encoding)
        virtual_path_info = self.get_virtual_path_info(encoding)

        if virtual_path_info == "":
            return real_path_info

        i = real_path_info.rfind(virtual_path_info)
        if i == -1:
            return real_path_info
        else:
            return real_path_info[:i]

    def get_attributes(self):

        """
        An application-specific method which obtains a dictionary mapping names
        to attribute values that can be used to store arbitrary information.

        Since the dictionary of attributes is retained by the transaction during
        its lifetime, such a dictionary can be used to store information that an
        application wishes to communicate amongst its components and resources
        without having to pass objects other than the transaction between them.

        The returned dictionary can be modified using normal dictionary-like
        methods. If no attributes existed previously, a new dictionary is
        created and associated with the transaction.
        """

        if not hasattr(self, "_attributes"):
            self._attributes = {}
        return self._attributes

    # Utility methods.

    def update_path(self, path, relative_path):

        """
        Transform the given 'path' using the specified 'relative_path'. For
        example:

        trans.update_path("/parent/node", "other") -> "/parent/other"

        trans.update_path("/parent/node/", "other") -> "/parent/node/other"

        trans.update_path("/parent/node", "../other") -> "/other"

        trans.update_path("/parent/node/", "../other") -> "/parent/other"

        trans.update_path("/parent/node", "../../other") -> "/other"

        trans.update_path("/parent/node/", "../../other") -> "/other"

        Where 'relative_path' begins with "/", the 'path' is reset to "/" and
        the components of the 'relative_path' are then applied to that new path:

        trans.update_path("/parent/node", "/other") -> "/other"

        Where 'relative_path' ends with "/", the final "/" is added to the
        result:

        trans.update_path("/parent/node", "other/") -> "/parent/other/"

        Where 'relative_path' is empty, the result is 'path' minus the last
        component, unless it was an empty component:

        trans.update_path("/parent/node", "") -> "/parent/"

        trans.update_path("/parent/node/", "") -> "/parent/node/"
        """

        rparts = relative_path.split("/")

        if relative_path.startswith("/"):
            parts = [""]
            del rparts[0]
        elif relative_path == "":
            parts = path.split("/")
            parts[-1] = ""
            del rparts[0]
        else:
            parts = path.split("/")
            del parts[-1]

        for rpart in rparts:
            if rpart == ".":
                continue
            elif rpart == "..":
                if len(parts) > 1:
                    parts = parts[:-1]
            else:
                parts.append(rpart)

        return "/".join(parts)

    def redirect(self, path, code=302):

        """
        Send a redirect response to the client, providing the given 'path' as
        the suggested location of a resource. The optional 'code' (set to 302 by
        default) may be used to change the exact meaning of the response
        according to the HTTP specifications.

        Note that 'path' should be a plain string suitable for header output.
        Use the 'encode_path' method to convert Unicode objects into such
        strings.
        """

        self.set_response_code(code)
        self.set_header_value("Location", path)
        raise EndOfResponse

class Resource:

    "A generic resource interface."

    def respond(self, trans):

        """
        An application-specific method which performs activities on the basis of
        the transaction object 'trans'.
        """

        raise NotImplementedError, "respond"

class Authenticator:

    "A generic authentication component."

    def authenticate(self, trans):

        """
        An application-specific method which authenticates the sender of the
        request described by the transaction object 'trans'. This method should
        consider 'trans' to be read-only and not attempt to change the state of
        the transaction.

        If the sender of the request is authenticated successfully, the result
        of this method evaluates to true; otherwise the result of this method
        evaluates to false.
        """

        raise NotImplementedError, "authenticate"

    def get_auth_type(self):

        """
        An application-specific method which returns the authentication type to
        be used. An example value is 'Basic' which specifies HTTP basic
        authentication.
        """

        raise NotImplementedError, "get_auth_type"

    def get_realm(self):

        """
        An application-specific method which returns the name of the realm for
        which authentication is taking place.
        """

        raise NotImplementedError, "get_realm"

# vim: tabstop=4 expandtab shiftwidth=4
