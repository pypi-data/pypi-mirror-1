#!/bin/sh
### ====================================================================== ###
##                                                                          ##
##  SwiftMQ Router start script                                             ##
##                                                                          ##
### ====================================================================== ###

DIRNAME=`dirname $0`
PROGNAME=`basename $0`
cygwin=false;
darwin=false;
case "`uname`" in
    CYGWIN*)
        cygwin=true
        ;;

    Darwin*)
        darwin=true
        ;;
esac

# For Cygwin, ensure paths are in UNIX format before anything is touched
if $cygwin ; then
    [ -n "$SWIFTMQ_HOME" ] &&
        SWIFTMQ_HOME=`cygpath --unix "$SWIFTMQ_HOME"`
    [ -n "$JAVA_HOME" ] &&
        JAVA_HOME=`cygpath --unix "$JAVA_HOME"`
    [ -n "$JAVAC_JAR" ] &&
        JAVAC_JAR=`cygpath --unix "$JAVAC_JAR"`
fi

# Setup SWIFTMQ_HOME
if [ "x$SWIFTMQ_HOME" = "x" ]; then
    # get the full path (without any relative bits)
    SWIFTMQ_HOME=`cd $DIRNAME/../..; pwd`
fi
export SWIFTMQ_HOME

# Setup the JVM
if [ "x$JAVA" = "x" ]; then
    if [ "x$JAVA_HOME" != "x" ]; then
	JAVA="$JAVA_HOME/bin/java"
    else
	JAVA="java"
    fi
fi

# Setup the classpath
export SWIFTMQ_CLASSPATH=
die() {
    echo "${PROGNAME}: $*"
    exit 1
}
classpath_jar() {
    if [ ! -f "$1" ]; then
        die "Missing required file: $1"
    fi
    SWIFTMQ_CLASSPATH=$SWIFTMQ_CLASSPATH:$1
}

for jar in swiftmq.jar jndi.jar jms.jar jsse.jar jnet.jar jcert.jar dom4j-full.jar jta-spec1_0_1.jar;
do classpath_jar $SWIFTMQ_HOME/jars/$jar;
done 

# If JAVA_OPTS is not set try check for Hotspot
if [ "x$JAVA_OPTS" = "x" ]; then

    # Check for SUN(tm) JVM w/ HotSpot support
    if [ "x$HAS_HOTSPOT" = "x" ]; then
	HAS_HOTSPOT=`$JAVA -version 2>&1 | $GREP -i HotSpot`
    fi

    # Enable -server if we have Hotspot, unless we can't
    if [ "x$HAS_HOTSPOT" != "x" ]; then
	# MacOS does not support -server flag
	if [ "$darwin" != "true" ]; then
	    JAVA_OPTS="-server"
	fi
    fi
fi

# For Cygwin, switch paths to Windows format before running java
if $cygwin; then
    SWIFTMQ_HOME=`cygpath --path --windows "$SWIFTMQ_HOME"`
    JAVA_HOME=`cygpath --path --windows "$JAVA_HOME"`
    SWIFTMQ_CLASSPATH=`cygpath --path --windows "$SWIFTMQ_CLASSPATH"`
fi

# Display our environment
echo "========================================================================="
echo ""
echo "  SwiftMQ Environment"
echo ""
echo "  SWIFTMQ_HOME: $SWIFTMQ_HOME"
echo ""
echo "  JAVA: $JAVA"
echo ""
echo "  JAVA_OPTS: $JAVA_OPTS"
echo ""
echo "  CLASSPATH: $SWIFTMQ_CLASSPATH"
echo ""
echo "========================================================================="
echo ""

STATUS=10
while [ $STATUS -eq 10 ]
do
# Execute the JVM
   "$JAVA" $JAVA_OPTS \
      -classpath "$SWIFTMQ_CLASSPATH" \
      com.swiftmq.Router "../../config/hjbrouter/routerconfig.xml"
   STATUS=$?
done
