#!/usr/bin/env python
"""
Demo showing pyhjb accessing an Active  MQ messaging provider via a HJB
server.

"""

from copy import deepcopy

from hjb.hjbclient import HJBClient, SimpleMessagingScenario
from hjb.democli import DemoCommand

__docformat__ = "restructuredtext en"

queue_aliases = {
    "test": "text",
    "Map": "HJB.SAMPLE.MAP",
    "Text": "HJB.SAMPLE.TEXT",
    "Object": "HJB.SAMPLE.OBJECT",
    "Stream": "HJB.SAMPLE.STREAM",
    "Bytes": "HJB.SAMPLE.BYTES",
}

topic_aliases = {
    "qotd": "HJB/SAMPLE/QOTD",
    "logmessage": "HJB\\SAMPLE\\LOGMESSAGE",
    "heartbeat": "HJB.SAMPLE.HEARTBEAT",
}

destination_aliases = deepcopy(queue_aliases)
destination_aliases.update(deepcopy(topic_aliases))

def create_scenario():
    provider_config = {
        # This configuration matches the default ActiveMQ environment
        # as of ActiveMQ version 4.0
        # 
        # In ActiveMQ, JNDI is optional - to use it, the JNDI names have to be
        # set up when the Initial Context is created.  That's why the
        # destination names are prefixed by 'topic.' or 'queue.' in the
        # provider configuration.

        "provider" : {
            # these are the parameters that is used to configure the java
            # Hashtable that initialises a provider's JNDI initial context
            #        
            # The first two are expected from all JNDI providers
            "java.naming.factory.initial": "org.apache.activemq.jndi.ActiveMQInitialContextFactory",
            "java.naming.provider.url": "tcp://localhost:61616",
            #
            # These others are specific to ActiveMQ because it initialise JNDI
            # using the JNDI configuration environment
            "connectionFactoryNames": "connectionFactory,queueConnectionFactory,topicConnectionFactory",
        }
    }
    config_queue_aliases = dict((("queue." + v, v) for k,v in queue_aliases.iteritems()))
    provider_config["provider"].update(config_queue_aliases)
    config_topic_aliases = dict((("topic." + v, v) for k,v in topic_aliases.iteritems()))
    provider_config["provider"].update(config_topic_aliases)

    provider = "activemq"
    root = "/hjb-activemq/hjb"
    factory = "connectionFactory"
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
