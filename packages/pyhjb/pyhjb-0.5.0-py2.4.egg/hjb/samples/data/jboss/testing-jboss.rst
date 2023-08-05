================================
Testing HJB with JBoss Messaging
================================

`JBoss Messaging`_ is an open source JMS implementation.  It is the next
generation JMS1.1 messaging implementation from `JBoss
<http://www.jboss.org>`_, replacing the older `JBossMQ`_.

This document discusses how to set up a JBoss Messaging installation to run the
samples provided with HJB.

Accessing JBoss Messaging JMS resources
---------------------------------------

HJB assumes that it can access any JMS Provider's JMS resources via JNDI.  This
is true for JBoss Messaging.

However, a number of configuration tasks need to be completed before JBoss
Messaging Connection Factories and Destinations can be accessed via JNDI; they
are described in the following section.

Setting up JBoss Messaging to run the HJB samples
-------------------------------------------------

Prerequisites
+++++++++++++

These instructions assume that:

- `JBoss AS`_ version 4.0.4 has been downloaded and `installed
  <http://wiki.jboss.org/wiki/Wiki.jsp?page=JBossInstallation>`_ successfully.

- JBoss Messaging has been installed.
  
  - `JBoss AS`_ version 4.0.4 does *not* include JBoss Messaging, so `download
    JBoss Messaging`_ and install it.  Follow the `installation instructions`_,
    making sure to remove JBoss MQ, and run the example tests to ensure that
    installation was successful.  Also update the login-config.xml file in the
    messaging server deployment area, by adding the 'guest' user as an
    unauthenticated identity. 
  
- A servlet container for hosting the HJB servlet is installed.

  - If using a separate`Tomcat` _ instance on windows, ensure that the tomcat
    path has no spaces in it.  During HJB testing, the tomcat installation path
    had to be renamed was necessary to fix odd behaviour from the JBoss client
    libraries. 
  
- The HJB servlet has been installed on the servlet container using a
  WebArchive file containing the JBoss Messaging JMS client libraries.  This
  can be done by following the `instructions`_ here.  An example
  hjb_deploy_properties file for use in generating the JBoss Messaging
  WebArchive file is included in the samples directory.

  - The JBoss Messaging client libraries are all contained in a single jar file
    that is part of the JBoss messaging download called

    jboss-messaging-client-scoped.jar

Create the Administered Objects
+++++++++++++++++++++++++++++++

JBoss Messaging configures its JNDI environment using XML files that are added
to the deployed messaging server installation.  PyHJB comes with a script, 

  make_jboss_destinations.py 

that creates a single file containing all the destinations used by the demo.
It should be run at least once.

You can directly refer to the 

  hjbjboss.py 

demo script supplied with pyhjb for the names of the queues, topics and
connection factories that are used in the demo.

.. _PyHJB: http://hjb.python-hosting.com

.. _Tomcat: http://tomcat.apache.org

.. _installation instructions: http://labs.jboss.com/file-access/default/members/jbossmessaging/freezone/docs/guide-1.0.1.CR2/html/index.html

.. _JBoss AS: http://sourceforge.net/project/showfiles.php?group_id=22866&package_id=16942&release_id=416591 

.. _JBoss Messaging: http://labs.jboss.com/portal/index.html?ctrl:id=page.default.info&project=jbossmessaging

.. _download JBoss Messaging: http://labs.jboss.com/file-access/default/members/jbossmessaging/downloads/jboss-messaging-1.0.1.CR2.zip

.. _JBoss MQ: http://wiki.jboss.org/wiki/Wiki.jsp?page=JBossMQ

.. _instructions: http://hjb.berlios.de/installation.html
