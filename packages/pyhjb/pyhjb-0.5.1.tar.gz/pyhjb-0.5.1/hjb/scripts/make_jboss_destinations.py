#!/usr/bin/env python
"""
Simple script for automatically creating a xxx-service.xml file that adds the
HJB demo queues to a JBoss Messaging server.

Should be invoked as follows:

  make_jboss_destinations.py [jboss-service-filename]

  e.g. python make_jboss_destinations.py C:\\jboss4xx\\server\\messaging\\deploy\\hjb-demo-service.xml
  
jboss-service-filename is optional, if its not supplied, generated service file
is dumped to stdout

"""

from os.path import isfile
import sys
from xml.dom.minidom import parseString

from hjbjboss import topic_aliases, queue_aliases 

__docformat__ = "restructuredtext en"

service_xml_template = """<?xml version="1.0" encoding="UTF-8"?>
<server>
  <loader-repository>jboss.messaging:loader=ScopedLoaderRepository
    <loader-repository-config>java2ParentDelegation=false</loader-repository-config>
  </loader-repository>
  %s
</server>
"""

queue_mbean_template = """
  <mbean code="org.jboss.jms.server.destination.Queue"
         name="jboss.messaging.destination:service=Queue,name=%s"
         xmbean-dd="xmdesc/Queue-xmbean.xml">
    <depends optional-attribute-name="ServerPeer">jboss.messaging:service=ServerPeer</depends>
      <attribute name="SecurityConfig">
        <security>
          <role name="guest" read="true" write="true"/>
          <role name="publisher" read="true" write="true" create="false"/>
          <role name="noacc" read="false" write="false" create="false"/>
        </security>
      </attribute>
  </mbean>
"""

topic_mbean_template = """
  <mbean code="org.jboss.jms.server.destination.Topic"
         name="jboss.messaging.destination:service=Topic,name=%s"
         xmbean-dd="xmdesc/Topic-xmbean.xml">
     <depends optional-attribute-name="ServerPeer">jboss.messaging:service=ServerPeer</depends>
     <attribute name="SecurityConfig">
        <security>
           <role name="guest" read="true" write="true" create="true"/>
           <role name="publisher" read="true" write="true" create="false"/>
           <role name="durpublisher" read="true" write="true" create="true"/>
        </security>
     </attribute>
  </mbean>
"""

def write_service_xml_text(queues=None, topics=None, fd=None):
    """Create a jboss service_xml file and write it to file-like object `fd`
       
    Creates a jboss service.xml file that contains topic and queue
    configuration for a JBoss messaging server.  
    
    `queues` should be a list containing queue names.  Each queue will
    be configured using `queue_mbean_template` as a template.

    `topics` should be a list cointaining topic names.  Each topic
    will be configured using `topic_mbean_template` as a template.

    `fd` is a file-like object to which the configuration XML  will be written.

    """
    if not queues:
        queues = ["testQueue"]
    if not topics:
        topics = ["testTopic"]
    if not fd:
        fd = sys.stdout
    queue_text = "".join([queue_mbean_template % s.replace("/queue/", "") for s in queues])
    topic_text = "".join([topic_mbean_template % s.replace("/topic/", "") for s in topics])
    all_text = service_xml_template % (queue_text + topic_text)
    parseString(all_text)
    fd.write(all_text)


def open_file_if_specified():
    """Attempts to open sys.argv[1] as file and return the opened file.

    Returns `None` if file operation fails or if sys.argv[1] is not present.  

    """
    if len(sys.argv) > 1:
        try:
            return file(sys.argv[1], 'w')
        except:
            print "[** Error ***] could not open file ", sys.argv[1] 
            return None
    return None

def main():
    fd = open_file_if_specified()
    write_service_xml_text(
            queues=queue_aliases.values(), 
            topics=topic_aliases.values(),
            fd=fd)
    if fd: 
        fd.close()

if __name__ == "__main__":
    main()
