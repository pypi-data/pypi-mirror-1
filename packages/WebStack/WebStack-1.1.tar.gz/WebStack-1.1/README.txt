Introduction
------------

WebStack is a package which provides a common API for Python Web
applications, regardless of the underlying server or framework environment.
It should be possible with WebStack to design and implement an application,
to choose a deployment environment, and then to be able to deploy the
application in a different environment later on without having to go back
and rewrite substantial parts of the application.

Quick Start
-----------

Try running the demo:

python tools/demo.py

An introductory guide to creating applications can be found in the docs
directory - see docs/index.html for the start page.

Contact, Copyright and Licence Information
------------------------------------------

The current Web page for WebStack at the time of release is:

http://www.boddie.org.uk/python/WebStack.html

Copyright and licence information can be found in the docs directory - see
docs/COPYING.txt, docs/LICENCE.txt and docs/LICENCE-PyServlet.txt for more
information.

Framework Support
-----------------

Currently, BaseHTTPRequestHandler (via BaseHTTPServer in the standard
library), CGI, Jython/Java Servlet API, mod_python, Twisted, Webware, WSGI
and Zope 2 are supported. Each framework has its own set of strengths and
weaknesses, but the idea is that deployment concerns can be considered
separately from the implementation of application functionality. Consult the
NOTES.txt files in each framework's subdirectory of the docs directory for
some notes on how applications may be run in each environment.

Tested Frameworks           Release Information
-----------------           -------------------

BaseHTTPRequestHandler      Python 2.2.2, Python 2.3.3, Python 2.4.1
CGI                         Apache 2.0.44, Apache 2.0.53, AOLserver 4.0.10, lighttpd 1.3.15
Jython/Java Servlet API     Jython 2.1, Java JDK 1.3.1_02, Tomcat 4.1.31 (Servlet 2.3)
mod_python                  3.0.3 (3.1.3 for framework cookie and session support)
Twisted                     1.0.5, 1.3.0
Webware                     0.8.1, CVS (2004-02-06), 0.9b2
WSGI                        run_with_cgi (PEP 333)
Zope                        2.7.2-0, 2.8.0-final

New in WebStack 1.1 (Changes since WebStack 1.0)
------------------------------------------------

  * Added a Repositories package to provide session-like support for
    different kinds of storage.
  * Added an explicit filesystem encoding to the Calendar example and adopted
    the DirectoryRepository from the Repositories package.
  * Added get_path_without_info, update_path and redirect methods to the
    Transaction class.
  * Added get_attributes (attribute support) to the Transaction class.
  * Added a values method to Helpers.Session.Wrapper.
  * Fixed get_processed_virtual_path_info (to match from right to left).
  * Improved/fixed exception handling in the adapters so that transactions are
    committed as the final act of an adapter experiencing an unhandled
    exception. This should result in session stores being closed properly.
  * Changed the Helpers.Session.SessionStore to use DirectoryRepository.
  * Made the "not found" behaviour of DirectoryResource more configurable.
  * Added documentation for MapResource and DirectoryResource.
  * Fixed the distribution names in the Ubuntu changelog.

New in WebStack 1.0 (Changes since WebStack 0.10)
-------------------------------------------------

  * Changed the behaviour of get_path, get_path_without_query, get_path_info,
    get_virtual_path_info, get_processed_virtual_path_info and
    get_fields_from_path to return Unicode data decoded using the optional
    encoding parameter or a common default encoding.
  * Fixed file upload values so that FileContent objects are returned for such
    fields in get_fields_from_body and get_fields.
    (Warning! Except for Twisted!)
  * Fixed the JavaServlet support so that streams and file content are
    obtained as "almost" plain strings.
  * Updated/fixed LoginResource and LoginRedirectResource to use the updated
    path API and to handle special characters properly.
  * Added convenience methods to Transaction for the decoding and encoding of
    path values (to and from Unicode objects) - see the decode_path and
    encode_path methods.
  * Added the notion of processed virtual path info - the part of the original
    path info not represented in the current virtual path info.
  * Added "pass through" behaviour to ResourceMap.MapResource (prompted by a
    patch from Scott Robinson).
  * Fixed ResourceMap.MapResource to handle non-existent resources properly
    (where the virtual path info is only one component in length).
  * Added Debian package support.
  * Added automatic session directory creation for the WebStack sessions
    implementation.
  * Added support for the repeated retrieval of sessions from the same
    WebStack session store, avoiding deadlocks.
  * Fixed the calendar example, making it perform a proper function.
  * Made the BaseHTTPRequestHandler and Twisted SimpleWithLogin applications
    include the Login application, since Konqueror (at least) does not share
    cookies across different port numbers on the same host.
  * Added the SimpleWithLogin and Login applications to the demonstration.
  * Improved the documentation, adding information on request headers, and
    describing file upload and session support limitations.
  * Improved the AOLserver-related notes for CGI and Webware, adding a patch
    for Webware in order to work around AOLserver issues.

New in WebStack 0.10 (Changes since WebStack 0.9)
-------------------------------------------------

  * Changes to make the tools/demo.py script work on Windows (and other)
    platforms (suggested by Jim Madsen).
  * Fixed end of header newlines for CGI (suggested by Matt Harrison).
  * Minor documentation fixes and improvements, adding information on
    AOLserver in the CGI and Webware notes.
  * Changed the mod_python server name method to use the server object rather
    than the connection object.
  * Added a parameter to the ResourceMap.MapResource class to permit automatic
    redirects into resource hierarchies when no trailing "/" was given in the
    URL; changed the updated virtual path info so that empty values may be set
    (the guarantee that "/" will always appear no longer applies).
  * Fixed virtual path info retrieval when the value is an empty string.

New in WebStack 0.9 (Changes since WebStack 0.8)
------------------------------------------------

  * Standardised error handling in the adapters so that tracebacks can be
    suppressed and an internal server error condition raised.
  * Added overriding of path info in transactions.
  * Added a ResourceMap resource for dispatching to different resources
    according to path components.
  * Standardised deployment for some frameworks (see docs/deploying.html).
  * Introductory documentation in XHTML format.
  * Added server name and port methods to the transaction.
  * Added a simple demonstration application, incorporating many of the
    examples and launched under a single script.
  * Fixed mod_python native sessions.
  * Fixed Zope request stream access.
  * WebStack is now licensed under the LGPL - see docs/COPYING.txt for
    details.

New in WebStack 0.8 (Changes since WebStack 0.7)
------------------------------------------------

  * Added a standard exception, EndOfResponse, which can be used to
    immediately stop the processing/production of a response; this is useful
    when resources need to issue a redirect without unnecessary content being
    generated, for example.
  * Fixed path information for Zope.
  * Added WSGI support.
  * Verified Twisted 1.3.0 support with Python 2.3.3.

New in WebStack 0.7 (Changes since WebStack 0.6)
------------------------------------------------

  * Fixed path information semantics.
  * Fixed file upload semantics.
  * Fixed content type handling for Unicode output and for interpreting
    request body fields/parameters (although some improvement remains).
  * Added a method to discover the chosen response stream encoding.
  * Fixed field/parameter retrieval so that path and body fields are distinct,
    regardless of the framework employed.
  * Added a method to get a combination of path and body fields (suggested by
    Jacob Smullyan).
  * Introduced Zope 2 support.
  * Improved Jython/Java Servlet API support (although a special PyServlet
    class must now be used, and certain libraries must be deployed with
    applications).
  * Introduced authentication/authorisation support for Jython/Java Servlet
    API.
  * Session support has been added (except for Webware 0.8.1).
  * Alternative cookie support for mod_python has been added.
  * Cookie support now supports encoded Unicode sequences for names and
    values.

New in WebStack 0.6 (Changes since WebStack 0.5)
------------------------------------------------

  * Introduced Jython/Java Servlet API support.
  * Minor fixes to example applications and to BaseHTTPRequestHandler.

New in WebStack 0.5 (Changes since WebStack 0.4)
------------------------------------------------

  * Changed request body fields/parameters so that they are now represented
    using Unicode objects rather than plain strings.
  * Introduced better support for Unicode in response streams.

New in WebStack 0.4 (Changes since WebStack 0.3)
------------------------------------------------

  * Added application definition of user identity, permitting alternative
    authentication mechanisms.
  * Improved BaseHTTPRequestHandler and mod_python reliability around fields
    from request bodies.
  * Provided stream and environment parameterisation in the CGI adapter.
  * Added LoginRedirect and Login examples.
  * Added get_path_without_query and fixed get_path behaviour.

New in WebStack 0.3 (Changes since WebStack 0.2)
------------------------------------------------

  * Added better header support for Webware (suggested by Ian Bicking).
  * Introduced CGI and Java Servlet support (the latter is currently
    broken/unfinished).
  * Introduced support for cookies.

Future Work
-----------

(Essential)

Twisted 1.3.0 does not provide file upload metadata, and Twisted Web 0.5.0
also seems to be missing this functionality. It isn't obvious whether Twisted
Web2 will just copy its predecessors and provide a similarly limited API.
Perhaps the Twisted support needs to resemble the CGI support much more when
handling fields.

JythonServlet libraries need to be configured using sys.add_package when
these do not feature in the compiled-in list. Adding such configuration to
the handler may be most appropriate (since the web.xml file can be too
arcane), but this needs testing.

(Important)

Field access needs testing, especially for anything using the
cgi.FieldStorage class, and the way file uploads are exposed should be
reviewed (currently the meta-data is not exposed). The acquisition of fields
from specific sources should be tested with different request methods - some
frameworks provide path fields in the body fields dictionary, others (eg.
Zope) change the fields exposed depending on request method.

Interpretation of path field encodings needs to be verified. Currently,
stray path fields are handled (eg. in WebStack.Helpers.Request) as being
ISO-8859-1, but it might be the case that some such fields might be
submitted as UTF-8. The decode_path method on Transaction does do much of the
work that is likely to be required, however. Still, a good policy for decoding
path fields, reducing the number of times one might specify the encoding in
various method calls, may be important.

An interesting test of encodings is to introduce things like the following to
the path info and query string sections of the URL: %25F0?%E6=%F8&%25F0=%F8
This should produce the following decoded result: %F0?æ=ø&%F0=ø
(The above needs to be read in ISO-8859-1 or ISO-8859-15.)

Cookie objects need defining strictly, especially since the standard library
Cookie object behaves differently to mod_python (and possibly Webware)
Cookie objects. Moreover, the set_cookie_value method needs to provide
access to the usual cookie parameters as supported by the frameworks. The
standard library Cookie module has issues with Unicode cookie names (and
possibly values) - this is worked around, but it would be best to resolve
this comprehensively.

UTF-16 (and possibly other encodings) causes problems with HTML form data
sent in POST requests using the application/x-www-form-urlencoded content
type.  This should be reviewed at a later date when proper standardisation
has taken place.

Session support, especially through WebStack.Helpers.Session, should be
reviewed and be made compatible with non-cookie mechanisms.

Locking in the session support and in DirectoryRepository should be improved.

HeaderValue objects should be employed more extensively. Thus, the header
access methods may need to change their behaviour slightly. The get_headers
method should potentially return a list for each item in the dictionary.

WSGI support could demand that a special "end of headers" method be
introduced into WebStack, thus making response output more efficient (and
probably also for other frameworks, too).

The algorithm employed in the WebStack.Helpers.Auth.get_token function
should be reviewed and improved for better security.

Investigate proper support for HEAD, OPTIONS and other request methods.

Consider packages for different operating systems (other than Debian).

Provide some 500 error content when handle_errors is true.

(Completed/rejected)

The location of deployed applications in the filesystem should be exposed to
those applications. (This is actually available in the __file__ module
variable.)

Path information should be consistent across all frameworks, and the "path
info" value should be meaningful. (This should now be correct.)

Investigate the nicer functions in the cgi module, discarding the "magic"
stuff like FieldStorage. (These nicer functions are used by projects like
Twisted - as of 1.3.0 at least - and do not give the necessary information we
require.)

Release Procedures
------------------

Update the WebStack/__init__.py __version__ attribute.
Change the version number and package filename/directory in the documentation.
Change code examples in the documentation if appropriate.
Update the release notes (see above).
Check the setup.py file and ensure that all package directories are mentioned.
Check the release information in the PKG-INFO file and in the package
changelog (and other files).
Tag, export.
Generate the PyServlet classes.
Generate the API documentation.
Remove generated .pyc files: rm `find . -name "*.pyc"`
Archive, upload.
Upload the introductory documentation.
Update PyPI, PythonInfo Wiki, Vaults of Parnassus entries.

Generating the API Documentation
--------------------------------

In order to prepare the API documentation, it is necessary to generate some
Web pages from the Python source code. For this, the epydoc application must
be available on your system. Then, inside the distribution directory, run the
apidocs.sh tool script as follows:

./tools/apidocs.sh

Some warnings may be generated by the script, but the result should be a new
apidocs directory within the distribution directory.

Making Packages
---------------

To make Debian-based packages:

  1. Create new package directories under packages if necessary.
  2. Make a symbolic link in the distribution's root directory to keep the
     Debian tools happy:

     ln -s packages/ubuntu-hoary/python2.4-webstack/debian/

  3. Run the package builder:

     dpkg-buildpackage -rfakeroot

  4. Locate and tidy up the packages in the parent directory of the
     distribution's root directory.
