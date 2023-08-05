#!/usr/bin/env python

"Make a configuration file for an Apache-resident application."

import os, sys
import glob

class ApacheServer:
    def __init__(self, apache_site_dir):
        self.apache_site_dir = apache_site_dir
        self.directories = [apache_site_dir, os.path.split(apache_site_dir)[0]]

    def get_user_from_config(self):
        return self.get_item_from_config("User")

    def get_server_root_from_config(self):
        return self.get_item_from_config("ServerRoot")

    def get_item_from_config(self, item_name):
        item = None
        for apache_dir in self.directories:
            for conf_filename in glob.glob(os.path.join(apache_dir, "*.conf")):
                conf_file = open(conf_filename)
                for line in conf_file.readlines():
                    line_parts = self.parse_line(line)
                    if len(line_parts) > 1 and line_parts[0] == item_name:
                        item = line_parts[1]
                        conf_file.close()
                        return item
                conf_file.close()
        return None

    def parse_line(self, line):
        parts = line.split('"')
        new_parts = []
        for i in range(0, len(parts)):
            part = parts[i]
            if i % 2 == 0:
                new_parts += part.split()
            else:
                new_parts.append(part)
        return new_parts

cgi_template = """
ScriptAlias %s "%s"
"""

mod_python_template = """
Alias %s "%s"

<Directory "%s">
    AddHandler python-program %s
    PythonHandler %s
    PythonDebug On
</Directory>
"""

if __name__ == "__main__":
    try:
        app_type = sys.argv[1]
        app_location = sys.argv[2]
        apache_site_dir = sys.argv[3]
        site_name = sys.argv[4]
        url_path = sys.argv[5]
        if app_type == "mod_python":
            suffix = sys.argv[6]
        elif app_type != "CGI":
            print "Please specify either CGI or mod_python as the application type."
            sys.exit(1)

    except IndexError:
        print "config.py CGI|mod_python <app-location> <apache-site-dir> <site-name> <url-path> [<suffix>]"
        print
        print "CGI configures a CGI application"
        print "mod_python configures a mod_python application"
        print
        print "<app-location> is the full path to your application"
        print "eg. %s/examples/CGI/SimpleHandler.py" % os.getcwd()
        print
        print "<apache-site-dir> is the directory where site configuration files are stored"
        print "eg. /etc/apache2/sites-available"
        print
        print "<site-name> is the name of the site within Apache"
        print "eg. simple"
        print
        print "<url-path> is the path at which your application will be published"
        print "eg. /cgi/simple"
        print
        print "mod_python options:"
        print
        print "<suffix> is the ending which published resources in the application should have"
        print "eg. .simple"
        sys.exit(1)

    # Derived information.

    handler_dir, handler_name = os.path.split(app_location)
    handler_name, extension = os.path.splitext(handler_name)
    if handler_name == "" or extension != ".py":
        print "Please specify the path to actual handler module file."
        print "eg. %s/examples/ModPython/SimpleApp/SimpleHandler.py" % os.getcwd()
        sys.exit(1)

    # Initialise an object representing an Apache server.

    apache_server = ApacheServer(apache_site_dir)

    # Set up the template and the sessions directory location.

    if app_type == "CGI":
        template = cgi_template % (url_path, app_location)
        sessions_dir = os.path.join(handler_dir, "WebStack-sessions")

    elif app_type == "mod_python":
        template = mod_python_template % (url_path, handler_dir, handler_dir, suffix, handler_name)
        server_root = apache_server.get_server_root_from_config() or apache_site_dir
        sessions_dir = os.path.join(server_root, "WebStack-sessions")

    # Set up the site filename.

    site_filename = os.path.join(apache_site_dir, site_name)

    if os.path.exists(site_filename):
        answer = raw_input("Overwrite existing site file? (Y|N) ")
        if answer.upper() == "N":
            print "Not overwriting."
            sys.exit(1)

    # Write the site file.

    try:
        f = open(site_filename, "wb")
        f.write(template)
        f.close()
    except IOError:
        print "Could not write the site file. Check your user privileges."
        print
        raise

    # Set up the sessions directory.

    if not os.path.exists(sessions_dir):
        answer = raw_input("Create sessions directory at %s? (Y|N) " % sessions_dir)
        if answer.upper() == "Y":
            os.mkdir(sessions_dir)

    # Find the user who should own the sessions directory.

    try:
        import pwd
        username = apache_server.get_user_from_config()
        if username is None:
            print "Not able to determine the Web server user."
        else:
            print "Found", username, "as the Web server user."
            try:
                t = pwd.getpwnam(username)
                uid, gid = t[2:4]
                answer = raw_input("Set %s, %s as user, group on the sessions directory? (Y|N) " % (uid, gid))
                if answer.upper() == "Y":
                    os.chown(sessions_dir, uid, gid)

            except KeyError:
                print "User not found in the password database."
            except OSError:
                print "Not able to change the ownership. Check your user privileges."

    except ImportError:
        print "Not configuring the sessions directory ownership."

    # Check the permissions on the application.

    if app_type == "CGI":
        try:
            import stat
            details = os.stat(app_location)
            mode = stat.S_IMODE(details[stat.ST_MODE])

            # Check for incorrect permissions.

            flags = stat.S_IRUSR|stat.S_IXUSR|stat.S_IRGRP|stat.S_IXGRP|stat.S_IROTH|stat.S_IXOTH

            # Set correct permissions.

            if mode & flags == flags:
                print "Correct permissions found were", oct(mode), "for", app_location
            else:
                answer = raw_input("Change the permissions on %s? (Y|N) " % app_location)
                if answer.upper() == "Y":
                    print "Setting mode", oct(flags), "on", app_location
                    os.chmod(app_location, flags)

        except ImportError:
            print "Not changing the permissions on the application."

    print "--------"
    print "Configuration completed."
    print "You may need to run an administrative tool to add the new site '%s' to Apache." % site_name
    print "eg. a2ensite"
    print "You may also want to check any sys.path definitions in your application."

# vim: tabstop=4 expandtab shiftwidth=4
