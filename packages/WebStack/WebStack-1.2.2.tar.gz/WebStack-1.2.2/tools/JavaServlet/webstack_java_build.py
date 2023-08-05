#!/usr/bin/env python

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

def make_app(handler, appdir, webstack_home, web_xml_template_name):

    """
    Make the application directory from the given 'handler', application
    directory 'appdir', the 'webstack_home' where the WebStack package can be
    found, and the deployment descriptor with the given 'web_xml_template_name'.
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

    copy_directory(os.path.join(webstack_home, "tools", "JavaServlet", "classes"),
        os.path.join(appname, "WEB-INF"))

    # Copy the WebStack package.

    copy_directory(os.path.join(webstack_home, "WebStack"),
        os.path.join(appname, "WEB-INF", "jython"))

    # Copy the application itself.

    copy_directory(appdir, os.path.join(appname, "WEB-INF", "jython"))

    # Copy the handler.

    handler_filename = os.path.split(handler)[1]
    copy_file(handler, os.path.join(appname, handler_filename))

    # Configure the deployment descriptor.

    f = open(os.path.join(webstack_home, "tools", "JavaServlet", web_xml_template_name))
    web_xml = f.read()
    f.close()
    web_xml = web_xml % (jython_home, handler_filename)

    # Write the deployment descriptor.

    f = open(os.path.join(appname, "WEB-INF", "web.xml"), "w")
    f.write(web_xml)
    f.close()

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 5:
        print "Please specify..."
        print "  * The location of the application handler."
        print "    eg. .../WebStack-x.y/examples/JavaServlet/SimpleApp.py"
        print "  * The location of the application."
        print "    eg. .../WebStack-x.y/examples/Common/Simple"
        print "  * The location of the WebStack package distribution or where"
        print "    WebStack documentation and extras have been installed."
        print "    eg. .../WebStack-x.y"
        print "    eg. /usr/share/doc/python2.4-webstack"
        print "  * The name of the deployment descriptor template."
        print "    eg. web.xml"
        print "You can also specify some additional libraries for the application..."
        print "  eg. $CATALINA_HOME/common/lib/activation.jar"
        print "      $CATALINA_HOME/common/lib/mail.jar"
        sys.exit(1)

    print "Making application directory..."
    make_app(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])

    if len(sys.argv) > 5:
        print "Copying additional libraries..."
        appname = get_appname(sys.argv[1])
        for library in sys.argv[5:]:
            library_dir, library_name = os.path.split(library)
            library_dest = os.path.join(appname, "WEB-INF", "lib", library_name)
            copy_file(library, library_dest)

    print "Now copy or move the application directory to your servlet container."

# vim: tabstop=4 expandtab shiftwidth=4
