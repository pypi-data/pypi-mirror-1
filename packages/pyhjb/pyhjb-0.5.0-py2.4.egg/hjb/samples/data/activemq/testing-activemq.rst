==========================
Testing HJB with Active MQ
==========================

`Active MQ`_ is an open source JMS implementation from the `Apache Software
Foundation`_.

This document discusses how to set up an Active MQ installation to run the
pyhjb demo.

Accessing Active MQ JMS resources
---------------------------------

HJB assumes that it can access any JMS Provider's JMS resources via JNDI.  This
is true for ActiveMQ.

However, the ActiveMQ JMS implementation does not really use JNDI.  To comply
with the JMS specification, it provides a nominal JNDI environment.  The only
way to place things in this nominal JNDI context is to put the names in the
hashtable used to initialise the ActiveMQ JNDI environment.

Setting up Active MQ to run the HJB samples
-------------------------------------------

Prerequisites
+++++++++++++

These instructions assume that:

- Active MQ version 4.0 has been downloaded and installed successfully.  You
  can get it `from here`_.

- A servlet container for hosting the HJB servlet is installed.
  
- The HJB servlet has been installed on the servlet container using a
  WebArchive file containing the ActiveMQ JMS client librariies.   This can be
  done by following the `instructions`_ here.  An example hjb_deploy_properties
  file for use in generating the WebArchive file is included in the samples
  directory.

Create the Administered Objects
+++++++++++++++++++++++++++++++

As mentioned above, ActiveMQ uses a nominal JNDI environment.  To be able to
obtain queues, destinations and connection factories from JNDI, you specify
them in the hashtable actually used to configure ActiveMQ JNDI.  

The `PyHJB`_ activemq demo script does this by adding them as extra items to
the *provider* dictionary within the overall scenario configuration.

You can refer directly to the 
  
  hjbactivemq.py 
  
demo script supplied with pyhjb for the names of the queues, topics and connection
factories that are used in the demo.

For additional details on using ActiveMQ as a messaging provider, please read
the `manual`_ on the ActiveMQ website.

.. _PyHJB: http://hjb.python-hosting.com

.. _Apache Software Foundation: http://jakarta.apache.org

.. _Active MQ: http://www.activemq.org

.. _instructions: http://hjb.berlios.de/installation.html

.. _manual: http://www.activemq.org/site/using-activemq.html

.. _from here: http://people.apache.org/~chirino/incubator-activemq-4.0/maven1/incubator-activemq/distributions/incubator-activemq-4.0.zip
