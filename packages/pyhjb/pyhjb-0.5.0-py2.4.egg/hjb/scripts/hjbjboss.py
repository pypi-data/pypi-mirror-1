#!/usr/bin/env python
"""
Demo showing pyhjb accessing a 'JBoss Messaging' JMS provider via a HJB
server.

N.B. JBoss Messaging is not the same as JBoss MQ.  The example should
work just the same, but has not been tested as of 2006/05/16.

"""

from copy import deepcopy

from hjb.hjbclient import HJBClient, SimpleMessagingScenario
from hjb.democli import DemoCommand

queue_aliases = {
    "Map": "/queue/hjb.sample.MAP",
    "Text": "/queue/hjb.sample.TEXT",
    "Object": "/queue/hjb.sample.OBJECT",
    "Stream": "/queue/hjb.sample.STREAM",
    "Bytes": "/queue/hjb.sample.BYTES",
}

topic_aliases = {
    "qotd": "/topic/hjb.sample.QOTD",
    "logmessage": "/topic/hjb.sample.LOGMESSAGE",
    "heartbeat": "/topic/hjb.sample.HEARTBEAT",
}

destination_aliases = deepcopy(queue_aliases)
destination_aliases.update(deepcopy(topic_aliases))

def create_scenario():
    provider_config = {
        # This provider config matches the JBOSS messaging environment
        # created using the files in the samples/data/jboss directory
        # 
        # These are the parameters that are used to configure the java
        # Hashtable that initialises a provider's JNDI initial context
        "provider" : {
            "java.naming.factory.initial": 
                "org.jnp.interfaces.NamingContextFactory",
            "java.naming.provider.url": 
                "jnp://localhost:1099",
            "java.naming.factory.url.pkgs":
                "org.jboss.naming:org.jnp.interfaces",
        }
    }
    provider = "jboss"
    root = "/hjb-jboss/hjb"
    factory = "/ConnectionFactory"
    host = "localhost:8015"
    return SimpleMessagingScenario(
            HJBClient(host, root),
            provider,
            factory,
            destination_aliases.values(),
            provider_config)

def turn_on_client_debug():
    import logging
    h = logging.StreamHandler()
    h.setLevel(logging.DEBUG)
    f = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    h.setFormatter(f)
    logging.getLogger("hjb.client").setLevel(logging.DEBUG)
    logging.getLogger("hjb.client").addHandler(h)

def main():
    #turn_on_client_debug() 
    command = DemoCommand(
            create_scenario(),
            destination_aliases)
    command.execute()
 
if __name__ == '__main__':
    main()
