#!/usr/bin/env jython

"A simple Jython-based installer for the Web applications."

import os

def copy_file(source, destination):

    """
    Copy a file from 'source' to 'destination'. Note that 'destination' must
    include the name of the file - it cannot be a directory name.
    """

    print "Copying", source, "to", destination

    # Do things by the book, since Jython/Java won't copy the file contents in
    # all cases presumably due to finalisation issues.

    f = open(source, "rb")
    s = f.read()
    f.close()

    f = open(destination, "wb")
    f.write(s)
    f.close()

def recurse(dirs_and_files, dirname, names):

    """
    A recursive directory and file collector for os.path.walk. The provided
    'dirs_and_files' list must contain two lists (one for directory names, one
    for filenames). The 'dirname' and 'names' parameters are supplied by the
    os.path.walk mechanism.
    """

    if dirname.endswith("/CVS"):
        return
    dirs_and_files[0].append(dirname)
    for name in names:
        if os.path.isfile(os.path.join(dirname, name)):
            dirs_and_files[1].append(os.path.join(dirname, name))

def copy_directory(source, destination):

    """
    Copy a directory found at 'source' in the filesystem to the 'destination'.
    Note that 'destination' is the parent directory of the newly created
    directory.
    """

    # Remove trailing directory separators.

    source = os.path.normpath(source)
    prefix = os.path.split(source)[0]
    dirs_and_files = [[], []]
    os.path.walk(source, recurse, dirs_and_files)

    for dirname in dirs_and_files[0]:

        # Remove the prefix from the name and create the object under the destination.
        # NOTE: Joining "" to the path in Jython doesn't add the path separator.

        new_dirname = dirname[len(os.path.join(prefix, "x")) - 1:]
        print "Making", new_dirname, "under", destination
        os.mkdir(os.path.join(destination, new_dirname))

    for filename in dirs_and_files[1]:

        # Remove the prefix from the name and create the object under the destination.
        # NOTE: Joining "" to the path in Jython doesn't add the path separator.

        new_filename = filename[len(os.path.join(prefix, "x")) - 1:]
        copy_file(filename, os.path.join(destination, new_filename))

def get_appname(handler):
    return os.path.split(os.path.splitext(handler)[0])[1]

def make_app(handler, root_resources, webstack_tools_home, webstack_package_home,
    jython_cachedir, web_xml_template_name, packages, libraries):

    """
    Make the application directory from the given 'handler' and
    'root_resources', the 'webstack_tools_home' where the tools directory is
    found, the 'webstack_package_home' where the WebStack package is found, the
    'jython_cachedir' where Jython classes are cached, the deployment descriptor
    with the given 'web_xml_template_name', and the specified 'packages'
    (locations of application packages) and 'libraries' (locations of required
    library files).
    """

    appname = get_appname(handler)
    print "Making", appname

    os.mkdir(appname)
    os.mkdir(os.path.join(appname, "WEB-INF"))
    os.mkdir(os.path.join(appname, "WEB-INF", "jython"))
    os.mkdir(os.path.join(appname, "WEB-INF", "lib"))

    # Copy the Jython runtime.

    jython_home = sys.exec_prefix
    copy_file(os.path.join(jython_home, "jython.jar"),
        os.path.join(appname, "WEB-INF", "lib", "jython.jar"))

    # Copy the special PyServlet classes.

    #copy_directory(os.path.join(webstack_tools_home, "tools", "JavaServlet", "classes"),
    #    os.path.join(appname, "WEB-INF"))

    copy_file(os.path.join(webstack_tools_home, "tools", "JavaServlet", "classes", "webstack-pyservlet.jar"),
        os.path.join(appname, "WEB-INF", "lib", "webstack-pyservlet.jar"))

    # Copy the WebStack package.

    copy_directory(os.path.join(webstack_package_home, "WebStack"),
        os.path.join(appname, "WEB-INF", "jython"))

    # Copy the application packages.

    for appdir in packages:
        copy_directory(appdir, os.path.join(appname, "WEB-INF", "jython"))

    # Copy the libraries.

    if libraries:
        for library in libraries:
            library_dir, library_name = os.path.split(library)
            library_dest = os.path.join(appname, "WEB-INF", "lib", library_name)
            copy_file(library, library_dest)

    # Copy the handler.

    handler_filename = os.path.split(handler)[1]
    copy_file(handler, os.path.join(appname, handler_filename))

    # Copy the root resources.

    for root_resource in root_resources:
        root_resource_filename = os.path.split(root_resource)[1]
        copy_file(root_resource, os.path.join(appname, root_resource_filename))

    # Find additional Jython paths.

    jython_paths = []
    for path in sys.path:
        if path.startswith(jython_home) and path != os.path.join(jython_home, "Lib"):
            jython_paths.append(path)

    jython_path = ":".join(jython_paths)

    # Create the cache directory if necessary.

    if not os.path.exists(jython_cachedir):
        os.mkdir(jython_cachedir)

    # Configure the deployment descriptor.

    f = open(os.path.join(webstack_tools_home, "tools", "JavaServlet", web_xml_template_name))
    web_xml = f.read()
    f.close()
    web_xml = web_xml % (jython_home, jython_path, jython_cachedir, handler_filename)

    # Write the deployment descriptor.

    f = open(os.path.join(appname, "WEB-INF", "web.xml"), "w")
    f.write(web_xml)
    f.close()

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 8:
        print "Syntax:"
        print
        print "jython webstack_java_build.py <handler> [ <resource>... ] \\"
        print "  --webstack <home> <tools> <cachedir> <descriptor> <app> \\"
        print "  [ --libraries <library>... ]"
        print
        print "Please specify..."
        print
        print "The location of the application handler. For example:"
        print
        print "    .../WebStack-x.y/examples/JavaServlet/SimpleApp.py"
        print
        print "Any other top-level resources, such as JSP templates. For example:"
        print
        print "    .../WebStack-x.y/examples/JavaServlet/test.jsp"
        print
        print "After the --webstack marker, the details of the WebStack distribution"
        print "are required, such as..."
        print
        print "The location of the WebStack package distribution. For example:"
        print
        print "    .../WebStack-x.y"
        print "    /usr/lib/python2.4/site-packages"
        print
        print "The location of the WebStack tools have been installed. For example:"
        print
        print "    .../WebStack-x.y"
        print "    /usr/share/doc/python2.4-webstack"
        print
        print "The location of the Jython cache directory. For example:"
        print
        print "    /home/paulb/.jython-cache"
        print
        print "The name of the deployment descriptor template. For example:"
        print
        print "    web.xml"
        print "    jsp-web.xml"
        print "    protected-web.xml"
        print
        print "The location of the application packages. For example:"
        print
        print "    .../WebStack-x.y/examples/Common/Simple"
        print
        print "You can also specify some additional libraries for the application"
        print "after a special '--libraries' marker. For example:"
        print
        print "    $CATALINA_HOME/common/lib/activation.jar"
        print "    $CATALINA_HOME/common/lib/mail.jar"
        print
        print "With Apache Tomcat 4.1.x, activation.jar and mail.jar are usually"
        print "required."
        sys.exit(1)

    webstack_index = sys.argv.index("--webstack")

    try:
        libraries_index = sys.argv.index("--libraries")
    except ValueError:
        libraries_index = len(sys.argv)

    print "Handler, root resources are..."
    handler, root_resources = sys.argv[1], sys.argv[2:webstack_index]
    print handler, root_resources

    print "WebStack distribution details are..."
    webstack_package_home, webstack_tools_home, jython_cachedir, web_xml = sys.argv[webstack_index+1:webstack_index+5]
    print webstack_package_home, webstack_tools_home

    print "Packages..."
    packages = sys.argv[webstack_index+5:libraries_index]
    print packages

    print "Libraries..."
    libraries = sys.argv[libraries_index+1:]
    print libraries

    print "Making application directory..."
    make_app(handler, root_resources, webstack_tools_home, webstack_package_home, jython_cachedir, web_xml, packages, libraries)

    print "Now copy or move the application directory to your servlet container."

# vim: tabstop=4 expandtab shiftwidth=4
