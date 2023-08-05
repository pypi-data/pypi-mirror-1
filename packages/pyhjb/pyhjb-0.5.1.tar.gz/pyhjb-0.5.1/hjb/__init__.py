"""
PyHJB is a python client library for accessing JMS 1.1 (Java Message
Service) messaging providers via HJB, the HTTP JMS bridge.

`HJB`_ provides access to JMS resources via HTTP.  It acts as an HTTP
gateway server for any JMS messaging provider, and provides a RESTful
equivalent for most of the non-optional portions of the JMS API.

.. _HJB: http://hjb.berlios.de

PyHJB is a pure python package which, via HJB, allows python programs
to:

* send/receive messages from **any** Enterprise Messaging System that
  supports JMS.  It is distributed with a few demo scripts showing it
  being used with a selection of well-known messaging providers:
  WebSphere MQ, Swift MQ, Active MQ and JBoss Messaging.

* register JMS administrable objects via JMS, e.g, queues, topics and
  connection factories.

* configure JMS runtime objects, e.g, connections, sessions, message
  consumers, message producers, queue browsers and durable subscribers
  etc.

Importantly, python programs written using PyHJB are portable across
JMS messaging providers.  The programs use the JMS API via HTTP rather
than a vendor's custom messaging API, and thus combine two important
maintainability traits:

* the use of the JMS API

* being written in python!

"""
__docformat__ = "restructuredtext en"
__version__ = "0.5.1"
__author__ = "Tim Emiola <tbetbe@users.berlios.de>"
__url__ = "http://hjb.python-hosting.com"
__license__ = "GNU Lesser General Public License (LGPL)"

