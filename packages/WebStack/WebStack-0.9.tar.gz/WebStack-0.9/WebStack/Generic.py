#!/usr/bin/env python

"""
Generic Web framework interfaces.
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
from WebStack.Helpers.Request import Cookie

class EndOfResponse(Exception):

    "An exception which signals the end of a response."

    pass

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

    def get_path(self):

        """
        Returns the entire path from the request.
        """

        raise NotImplementedError, "get_path"

    def get_path_without_query(self):

        """
        Returns the entire path from the request minus the query string.
        """

        raise NotImplementedError, "get_path_without_query"

    def get_path_info(self):

        """
        Returns the "path info" (the part of the URL after the resource name
        handling the current request) from the request.
        """

        raise NotImplementedError, "get_path_info"

    def get_query_string(self):

        """
        Returns the query string from the path in the request.
        """

        raise NotImplementedError, "get_query_string"

    # Higher level request-related methods.

    def get_fields_from_path(self):

        """
        Extracts fields (or request parameters) from the path specified in the
        transaction. The underlying framework may refuse to supply fields from
        the path if handling a POST transaction.

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
        """

        self.path_info = path_info

    def get_virtual_path_info(self):

        """
        An application-specific method which either returns path info set in the
        'set_virtual_path_info' method, or the normal path info found in the
        request.
        """

        return self.path_info or self.get_path_info()

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
