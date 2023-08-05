=========================
Testing HJB with Swift MQ
=========================

`SwiftMQ`_ is a commercial JMS implementation from IIT software.  It is a
'state-of-the-art, micro-kernel based JMS enterprise messaging platform'.

This document discusses how to set up a SwiftMQ installation to run the pyhjb
demo.

Accessing Swift MQ JMS resources
--------------------------------

HJB assumes that it can access any JMS Provider's JMS resources via JNDI.  This
is true for SwiftMQ.

However, a number of configuration tasks need to be completed before SwiftMQ
can be accessed via JNDI; they are described in the following section.

Setting up SwiftMQ to run the HJB samples
-----------------------------------------

Prerequisites
+++++++++++++

These instructions assume that:

- Swift MQ version 6.0 has been downloaded and installed successfully.  You
  can get it `from here`_.

- A servlet container for hosting the HJB servlet is installed.
  
- The HJB servlet has been installed on the servlet container using a
  WebArchive file containing the SwiftMQ JMS client librariies.   This can be
  done by following the `instructions`_ here.  An example hjb_deploy_properties
  file for use in generating the WebArchive file is included in the samples
  directory.

Create the Administered Objects
+++++++++++++++++++++++++++++++

SwiftMQ is designed entirely as a federated router network, whereby the router
network represents a single router to the JMS client.

By default, each router is represented by a set of child folders beneath the
SwiftMQ installation folder.  The set of folders includes folders for
configuration, logging, trace output and message persistence.  

The pyhjb samples area contains a set of similar folders that should be copied
into an existing SwiftMQ installation. Doing this sets up a new router, that
can either be run on its own, or run as part of a federated router network.
These pyhjb folders include a configuration folder containing a file that sets
up all the queues and topics used by the pyhjb demo.

E.g. the folders can be copied as follows (on unix),

    prompt> cd $PYHJB_HOME/hjb/samples/data/swiftmq/swiftmq_home
    prompt> cp -Rv $SWIFTMQ_HOME

Once the hjb folders are installed, it should be possible to start the
hjb_router using:

    prompt> cd $SWIFTMQ_HOME/scripts/unix
    prompt> ./run_hjbrouter.sh

You can refer directly to the 
  
  hjbswiftmq.py 
  
demo script supplied with pyhjb for the names of the queues, topics and
connection factories that are used in the demo.

For additional details on using SwiftMQ as a messaging provider, please read
the documentation available in the docs area of the installed SwiftMQ
distribution.

.. _PyHJB: http://hjb.python-hosting.com

.. _SwiftMQ: http://www.swiftmq.com

.. _instructions: http://hjb.berlios.de/installation.html

.. _from here: http://www.swiftmq.com/downloads/index.html
