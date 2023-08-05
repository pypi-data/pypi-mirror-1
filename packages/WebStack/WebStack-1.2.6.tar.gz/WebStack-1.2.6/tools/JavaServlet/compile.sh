#!/bin/bash

if [[ $JYTHON_LIB == "" ]]; then
    echo "Please set JYTHON_LIB to refer to the Jython .jar file."
    echo
    echo "For example:"
    echo
    echo "JYTHON_LIB=/usr/share/jython/jython.jar $0"
    exit 1
fi

if [[ $SERVLET_LIB == "" ]]; then
    echo "Please set SERVLET_LIB to refer to the servlet library .jar file."
    echo
    echo "For example:"
    echo
    echo "SERVLET_LIB=/usr/share/java/servlet-api.jar $0"
    echo "SERVLET_LIB=\$CATALINA_HOME/common/lib/servlet.jar $0"
    exit 1
fi

cd `dirname $0`/classes
CLASSPATH=$SERVLET_LIB:$JYTHON_LIB \
    javac uk/org/boddie/webstack/util/PyServlet.java
find uk/org/boddie/webstack/util -name "*.class" | jar -cvf webstack-pyservlet.jar -@
