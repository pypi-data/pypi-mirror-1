=============================
Testing HJB with WebSphere MQ
=============================

WebSphere MQ supports Java in two ways:

- WebSphere MQ base Java, a java wrapper of the native Websphere MQ API

- WebSphere MQ JMS, a JMS implementation that communicates with Websphere MQ
  servers
    
Obviously, HJB (the HTTP **JMS** Bridge) uses WebSphere MQ JMS! This document
discusses how to set up a WebSphere MQ installation to run the pyhjb demos.

Accessing WebSphere MQ JMS resources
------------------------------------

HJB assumes that it can access any JMS Provider's JMS resources via JNDI.  This
is certainly true for WebSphere MQ.  

However, there are a number of steps required before Websphere MQ Connection
Factories and Destinations can be accessed via JNDI.

Full details of WebSphere MQ adminstration are available in `Websphere MQ Using
Java`_.  A brief summary of the steps necessary to create the JMS administered
objects used by the `PyHJB`_ sample scripts are given in following section.

Setting up WebSphere MQ to run the HJB samples
----------------------------------------------

Prerequisites
+++++++++++++

These instructions assume that:

- WebSphere MQ version 6.0 has been downloaded and installed successfully.  You
  can get it `a trial version from here`_.

- A servlet container for hosting the HJB servlet is installed.
  
- The HJB servlet has been installed on the servlet container using a
  WebArchive file containing the Websphere JMS client librariies.   This can be
  done by following the `instructions`_ here.  An example hjb_deploy_properties
  file for use in generating the WebArchive file is included in the samples
  directory.

Create the Administered Objects
+++++++++++++++++++++++++++++++

In WebSphere MQ, creation of the administered objects used in the HJB samples
takes several steps.  

Firstly, the native MQ administrable objects are created.  There are several
types of these objects; the ones used in the HJB samples are

- Queue Managers
 
- Queues

- Message Brokers used by by `WebSphere MQ Publish Subscribe`_.

- System Queues used by `WebSphere MQ Publish Subscribe`_

Detailed instructions for creating these administrable object types are
available in the WebSphere MQ documentation. The objects can be created using
either WebSphere MQ Explorer, the installed WebSphere MQ admin commands or the
command line tool, WebSphere MQ Script Commands (MQSC_).

After the native MQ administrable objects have been created, they are bound
into JNDI as JMS administrable objects.  This is done using the JMSAdmin tool
that is supplied with WebSphere MQ.  Its usage is fully described in
`WebSphereMQ using Java`_

Both MQSC and JMSAdmin are scriptable command line tools. The pyhjb samples has a
data area containing scripts that bind all the JMS administered objects used in
the tests into JNDI.

The following sections describe how to use the combination of MQ administration
commands, MQSC scripts and JMSAdmin scripts to generate the WebSphere MQ
environment that the HJB demo can be run against. 

Create the Queue Manager
========================

The queue manager is created using the command 

  crtmqm, 
  
then started using the command 

  strmqm
  
The name of the Queue Manager used in the HJB samples is QM.HJB.SAMPLE, so
the commands to create and start the queue manager are:

  prompt> crtmqm -q -u Q.SYSTEM.DEAD.LETTER QM.HJB.SAMPLE
  prompt> strmqm QM.HJB.SAMPLE

In addition to creating the queue manager, it is necessary to create 

- a server connection channel, which allows clients to send messages to the
  queue managers queues and topics over the network, and 

- a listener, which listens for connections from clients on other machines.

This allows the HJB web container to be hosted on a different machine from the
WebSphere MQ installation and connect as a client over TCP/IP. In addition to
creating these two items, it may also be necessary to start the broker used by
WebSphere MQ Publish/Subscribe.

The HJB samples data area contains a file 

  update_hjb_qm.mqsc 

that contains the MQSC commands to add the server connection channel and listener
and start the system broker.  Run the script as follows:

  prompt> cd path/to/data/area
  prompt> runmqsc QM.HJB.SAMPLE < update_hjb_qm.mqsc

Set up Publish/Subscribe
========================

WebSphere MQ supports Publish/Subscribe using the aptly named WebSphere MQ
Publish Subscribe Broker.  There is one broker for each Queue Manager, and it
needs to have several system queues available on its Queue Manager for Publish
Subscribe to work correctly.  

WebSphere MQ comes with a script that creates these system queues for a given
Queue Manager.  This is described in "Installation and Configuration" section
of `WebSphere MQ Using Java`_.  The necessary steps are repeated here for the
Queue Managers created in `Create the Queue Managers`_. 

Run the script supplied with MQ to create the queues needed for
Publish/Subscribe as follows:

  prompt> cd path/to/wsmq/installation/Java/bin/
  prompt> runmqsc QM.HJB.SAMPLE < MQJMS_PSQ.mqsc

Create the Test Queues and Topics
=================================

The queues are created using the runmqsc in batch mode.  The HJB samples 
data area contains a file 

  create_hjb_queues.mqsc 

that contains the MQSC commands to create the sample queues. Run the
script as follows:

  prompt> cd path/to/data/area
  prompt> runmqsc QM.HJB.SAMPLE < create_hjb_queues.mqsc
  
The topics used by WebSphere MQ Publish/Subscribe do not need to be created by
the runmqsc tool.  Registering them in JNDI using JMSAdmin is sufficient. 

Create the JMS Bindings for the Administered Objects
====================================================

The HJB sample data area contains a file

  add_hjb_bindings.scp

that contains the JMSAdmin commands to add the JNDI bindings for the HJB Test
Connection Factorys, Queues and Topics. It binds

- 3 Connection Factorys, all using QM_HJB_SAMPLE, with Transport property
  set to Client so that the JMS Connection Factorys can be accessed by clients
  on other machines.  They are:

  - HJB/SAMPLE/TopicConnectionFactory

  - HJB/SAMPLE/QueueConnectionFactory

  - HJB/SAMPLE/ConnectionFactory

- All the queues created in `Create the Test Queues and Topics`_ are bound to
  JNDI as follows (JNDI name => actual Topic Name):
  
  - HJB/SAMPLE/TEXT => Q.HJB.SAMPLE.TEXT
    
  - HJB/SAMPLE/MAP => Q.HJB.SAMPLE.MAP
    
  - HJB/SAMPLE/STREAM => Q.HJB.SAMPLE.STREAM
    
  - HJB/SAMPLE/OBJECT => Q.HJB.SAMPLE.OBJECT
    
  - HJB/SAMPLE/BYTES => Q.HJB.SAMPLE.BYTES

- In addition, the following topics are registered (JNDI name => actual Topic
  Name) 

  - HJB/SAMPLE/QUOTD => Hjb/Test/QuoteOfTheDay

  - HJB/SAMPLE/LOGMESSAGE => Hjb/Test/LogMessage

  - HJB/SAMPLE/HEARTBEAT => Hjb/Test/Heartbeat
  
N.B., the data area contains a configuration file 

  HJB_JMSAdmin.cfg

that contains overrides for the JMSAdmin configuration file. It defaults to
storing the MQ administrable objects using Sun's simple filesystem JNDI context.  
Edit this file and change the directory used as the root of the JNDI hierarchy
to a location to one on the system where HJB is installed.  

Otherwise, consult Chapter 5 of `WebSphere MQ using Java`_ for details of how
to modify the JMSAdmin.cfg to use other JNDI contexts.

When using HJB_JMSAdmin.cfg, add the JMS bindings as follows:

  prompt> cd path/to/wsmq/installation/Java/bin
  prompt> ./JMSAdmin -cfg /path/to/data/area/HJB_JMSAdmin.cfg < /path/to/data/area/add_hjb_bindings.scp

After this last step, all the administrable objects by the pyhjb  demos should
be available from JNDI.

.. _MQSC: http://publibfp.boulder.ibm.com/epubs/pdf/csqzaj10.pdf

.. _WebSphere MQ Using Java: http://publibfp.boulder.ibm.com/epubs/pdf/csqzaw14.pdf

.. _PyHJB: http://hjb.python-hosting.com

.. _a trial version from here: http://www-128.ibm.com/developerworks/websphere/downloads

.. _WebSphere MQ Publish Subscribe: ftp://ftp.software.ibm.com/software/integration/support/supportpacs/individual/ma0dintr.pdf

.. _WebSphere MQ User Guide: http://publibfp.boulder.ibm.com/epubs/pdf/amqnar10.pdf
.. _WebSphere MQ Publish Subscriber Tutorial: ftp://ftp.software.ibm.com/software/integration/support/supportpacs/individual/ma0dtut.pdf
