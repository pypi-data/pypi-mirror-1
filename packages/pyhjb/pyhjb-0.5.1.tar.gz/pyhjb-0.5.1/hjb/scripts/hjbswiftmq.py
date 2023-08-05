#!/usr/bin/env python
"""
Demo showing pyhjb accessing a SwiftMQ JMS provider via a HJB
server.

"""
from copy import deepcopy

from hjb.hjbclient import HJBClient, SimpleMessagingScenario
from hjb.democli import DemoCommand

__docformat__ = "restructuredtext en"

queue_aliases = {
    "Map": "hjb_sample_MAP@hjbrouter",
    "Text": "hjb_sample_TEXT@hjbrouter",
    "Object": "hjb_sample_OBJECT@hjbrouter",
    "Stream": "hjb_sample_STREAM@hjbrouter",
    "Bytes": "hjb_sample_BYTES@hjbrouter",
}

topic_aliases = {
    "qotd": "hjb_sample_QOTD",
    "logmessage": "hjb_sample_LOGMESSAGE",
    "heartbeat": "hjb_sample_HEARTBEAT",
}

destination_aliases = deepcopy(queue_aliases)
destination_aliases.update(deepcopy(topic_aliases))

def create_scenario():
    provider_config = {
        # This provider config matches the SWIFTMQ messaging environment
        # created using the files in the samples/data/swiftmq directory
         
        # These are the parameters that are used to configure the java
        # Hashtable that initialises a provider's JNDI initial context
        "provider" : {
            "java.naming.factory.initial": 
                "com.swiftmq.jndi.InitialContextFactoryImpl",
            "java.naming.provider.url": 
                "smqp://localhost:4091/timeout=10000",
        }
    }
    provider = "swiftmq"
    root = "/hjb-swiftmq/hjb"
    factory = "/ConnectionFactory"
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
