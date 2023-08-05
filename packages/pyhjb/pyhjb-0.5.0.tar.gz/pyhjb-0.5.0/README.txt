############################################################
#                      PyHJB                               #
#----------------------------------------------------------#
# Copyright (C) 2006 Tim Emiola                            #
# Author: Tim Emiola <tbetbe@users.berlios.de>             #
# URL: <http:/hjb.python-hosting.com>                      #
# License: LGPL, see the licensing section below           #
############################################################

Introduction
------------

  PyHJB is a python client library for accessing JMS 1.1 (Java Message Service)
  messaging providers via HJB, the HTTP JMS bridge.

  HJB <http://hjb.berlios.de> provides access to JMS resources via HTTP.  It
  acts as an HTTP gateway server for any JMS messaging provider, and provides a
  RESTful equivalent for most of the non-optional portions of the JMS API. 

  This includes:

    * sending/receipt of messages from Enterprise Messaging Systems that support JMS

    * registration of JMS administrable objects (queues, topics, connection
      factories)

    * setup and configuration of JMS runtime objects, e.g., message consumers, 
      message producers, queue browser, durable subscribers etc

Prerequisites
-------------

  PyHJB is a pure python package which has no on dependencies anything apart
  from the python standard library. 

  However, it communicates over a network with a HJB gateway server, which is
  Java Servlet container running a HJB servlet.  See
  <http://hjb.berlios.de/download.html> for the latest version of HJB, and
  <http://hjb.berlios.de/installation.html> for the instructions on installing
  it.
  
Installing    
----------

  To install, download the source distribution from
  <http://cheeseshop.python.org/TBD/real_link>, then use the distutils 
  setup.py script

  prompt> cd pyhjb-m.n 
  prompt> python setup.py install

  More detailed installation instructions can be found on 
  http://hjb.python-hosting.com/wiki/GettingStarted

Documentation
-------------

  There is documentation available online at
  http://hjb.python-hosting.com/wiki/UsefulDocuments If you have questions that
  are not answered please email the hjb user mailing list
  <hjb-users@lists.berlios.de>.

Contributing
------------

  If you are interested in contributing to pyhjb, please email the 
  hjb developer mailing list <hjb-developers@lists.berlios.de>. 

Licensing
---------

  PyHJB is free software; you can redistribute it and/or
  modify it under the terms of the GNU Lesser General Public
  License as published by the Free Software Foundation; either
  version 2.1 of the License, or (at your option) any later version.

  This library is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
  Lesser General Public License for more details.

  You should have received a copy of the GNU Lesser General Public
  License along with this library; if not, write to the Free Software
  Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
