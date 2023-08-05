#!/usr/bin/env python
"""
Demo showing pyhjb accessing a WebSphere MQ messaging provider via a HJB
server.

"""

from copy import deepcopy

from hjb.hjbclient import HJBClient, SimpleMessagingScenario
from hjb.democli import DemoCommand

__docformat__ = "restructuredtext en"

queue_aliases = {
    "Map": "HJB\\SAMPLE\\MAP",
    "Text": "HJB\\SAMPLE\\TEXT",
    "Object": "HJB\\SAMPLE\\OBJECT",
    "Stream": "HJB\\SAMPLE\\STREAM",
    "Bytes": "HJB\\SAMPLE\\BYTES",
}

topic_aliases = {
    "qotd": "HJB\\SAMPLE\\QOTD",
    "logmessage": "HJB\\SAMPLE\\LOGMESSAGE",
    "heartbeat": "HJB\\SAMPLE\\HEARTBEAT",
}

destination_aliases = deepcopy(queue_aliases)
destination_aliases.update(deepcopy(topic_aliases))

def create_scenario():
    provider_config = {
        # provider_config matches the WebSphere MQ environment
        # created using the files in the samples/data/wsmq directory
        
        # The parameters are used to configure the java Hashtable that
        # initialises a provider's JNDI initial context WSMQ supports a generic
        # JNDI implementation as its store for MQ items, as long as the
        # implementation can persist java objects
         
        # This example uses the sun filesystem JNDI context.  The jar file
        # containing this context is supplied with WebSphere MQ.
        
        # Obviously, if the demo JNDI implementation changes, e.g., to use a
        # real LDAP server, these values in this dictionary will need to
        # change, as will the format of the destination URLs used in this
        # sample file 
        "provider" : {
            "java.naming.factory.initial": 
                "com.sun.jndi.fscontext.RefFSContextFactory",
            "java.naming.provider.url": 
                "file:/C:/tim_root/var/wsmq/jndi",
        }
    }
    provider = "wsmq"
    root = "/hjb-wsmq/hjb"
    factory = "HJB\\SAMPLE\\ConnectionFactory"
    host = "localhost:8015"
    return SimpleMessagingScenario(
            HJBClient(host, root),
            provider,
            factory,
            destination_aliases.values(),
            provider_config)

def main():
    command = DemoCommand(
            create_scenario(),
            destination_aliases)
    command.execute()
 
if __name__ == '__main__':
    main()
