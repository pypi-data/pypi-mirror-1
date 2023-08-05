""" 
Contains clases that demonstrate various simple message use cases using a JMS
Messaging provider, HJB and  py.hjb.  
"""

from copy import deepcopy
from itertools import cycle, chain
import logging
from random import choice
import sys

from hjb.hjbtypes import *
from hjb.hjbmessages import *
from hjb.hjbclient import HJBClient, SimpleMessagingScenario, HJBError, compose_url
from hjb.demoutil import *

log = logging.getLogger("hjb.demo")

def create_memory_logging_handler(**kw):
    return UsefulMemoryHandler(5, target_generator=create_file_logging_handler) 

def create_file_logging_handler(logfile="C:\\Temp\\hjb_debug.log", level=logging.DEBUG):
    h = logging.FileHandler(logfile)
    h.setLevel(level)
    f = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    h.setFormatter(f)
    return h

def create_jms_logging_handler(demo, level=logging.INFO):
    dsc = demo.scenario
    logging_scenario = SimpleMessagingScenario(
            HJBClient(
                dsc.client.hostname,
                dsc.client.root),
            dsc.provider,
            dsc.factory,
            [demo.aliases["logmessage"]],
            deepcopy(dsc.config))
    jms_logging_config = {
        "producers": [
            {"destination-url" : logging_scenario.full_url_of(demo.aliases["logmessage"])}
        ]
    }
    logging_scenario.update_session(jms_logging_config, index=0)
    h = JMSHandler(logging_scenario)
    h.setLevel(level)
    f = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    h.setFormatter(f)
    return h

class Demo(object):
    """I provide my subclasses with useful methods for demonstrating HJB's
    capabilities.
    """

    def __init__(self, scenario, aliases):
        self.aliases = aliases
        self.scenario = scenario
        self.use_jms_log = False

    def get_producer_aliases(self):
        """Obtain the list of destination aliases that have actually been
        used as in producers.

        If its present, this will be the value of `self.configured_producers`
        field, which should have been assigned by `self._create_session_config`.

        Otherwise it will be the value of `self.aliases.keys()`

        """
        result = getattr(self, 'configured_producers', None)
        if result:
            return result 
        else:
            result = self.aliases.keys()
            result.sort()
            return result

    def configure_session(self):
        """Create the session used by this in this demo class."""
        self.scenario.update_session(self._create_session_config(), index=0)

    def configure_logging(self, level=logging.DEBUG, jms_level=logging.INFO):
        log.setLevel(level)
        log.addHandler(create_memory_logging_handler(level=level))
        if (self.use_jms_log):
            log.addHandler(create_jms_logging_handler(self, level=jms_level))

    def find_sending_url_for(self, message):
        """Select the send URL to which `message` should be sent.

        Assumes that `self.scenario` has a first session with configured
        producers. 
        
        Uses `self.aliases` to route message to different producers depending
        on type of the message or the value of the `hjb_send_to` header in the
        message when that is present and the destinations available in
        `self.scenario`.

        """
        sc = self.scenario
        destinations = self.get_producer_aliases()
        message_type = getattr(message, "message_type", None)
        hjb_send_to = message.headers.get("hjb_send_to", None)

        producers = sc.sessions[0].producers
        for test in [hjb_send_to, message_type]:
            for i, destination in enumerate(destinations):
                if len(producers) == i:
                    break
                if destination == test:
                    return compose_url(producers[i], "send")
        return compose_url(producers[0], "send")

    def create_heartbeat(self, name):
        """Create a `demoutil.Heartbeat`.
       
        Create a `demoutil.Heartbeat` instance that fires heartbeat messages 
        for this demo instance.
        
        Assumes that `self.scenario` has as a first session with a configured
        heartbeat producer. 
        
        """ 
        self._assert_first_session_exists()
        sc = self.scenario
        assert len(sc.sessions[0].producers) > 0, "scenario's first session has no producer"
        dummy_message = heartbeat_for(str(self), "dummy")
        sc = self.scenario
        return Heartbeat(
                str(self), 
                sc.client, 
                self.find_sending_url_for(dummy_message))

    def _assert_first_session_exists(self):
        sc = self.scenario
        assert sc, "no scenario supplied"
        assert len(sc.sessions) > 0, "scenario has no sessions"
 
class ShutdownProvider(Demo):
    """I shutdown the JMS objects on the HJB server."""

    def __init__(self, scenario, aliases):
        super(ShutdownProvider, self).__init__(scenario, aliases)

    def run(self):
        """Shutdown the provider used by `self.scenario`."""
        sc = self.scenario
        response = sc.shutdown_provider()
        print response.getheader("hjb.command.status")

    def _create_session_config(self):
        """Create the session configuration used by this demo class.
        
        Returns an empty dictionary, as no session configuration is required.
        As a side effect, the scenario destination are emptied, to prevent
        needless destination registrations.

        """
        sc = self.scenario
        sc.destinations = []
        return {}

class SendEachJmsMessageType(Demo):
    """I send one of each type of JMS message."""

    def __init__(self, scenario, aliases):
        super(SendEachJmsMessageType, self).__init__(scenario, aliases)
        self.use_jms_log = True

    def _create_session_config(self):
        """Create the session configuration used by this demo class.
        
        Specifies a set of producers, one for each message type, so that
        the messages produced go to different destinations.  This demo
        demonstrates some very simple routing based on header values.
        """
        sc = self.scenario
        destinations = self.get_producer_aliases()
        return {
            "producers": [
                { "destination-url" : sc.full_url_of(self.aliases[d]) } 
                        for d in destinations
            ], 
        }

    def run(self):
        """Sends one of each of the five JMS message types.
        
        The demo's session is configured so that each message is routed to a
        different destination.
        
        """
        self._assert_first_session_exists()
        sc = self.scenario
        try:
            sc.start()
            def send(message, url):
                try:
                    print "... sending message of type [%s] to [%s]" % (message.message_type, url)
                    sc.client.send_message(message, url)
                    print "[** SEND OK **] "
                except HJBError, e:
                    print "[** SEND FAILED **] " + str(e)
            [send(m, self.find_sending_url_for(m)) for m in five_simple_messages_generator()]                        
        finally:
            sc.delete_connection()

class PrintMessagesOnQueue(Demo):
    """I print out all the messages on a Queue."""
    
    def __init__(self, scenario, aliases, receiver_name="Text"):
        super(PrintMessagesOnQueue, self).__init__(scenario, aliases)
        self.receiver_name = receiver_name 
        self.use_jms_log = True

    def _create_session_config(self):
        """Create the session configuration used by this demo class.
        
        Specifies a browser from which the messages to be printed will be
        retrieved, and a producer to send heartbeats while the browser
        operation is occurring. 

        """
        sc = self.scenario
        return {
            "browsers": [
                {
                   "destination-url" : sc.full_url_of(self.aliases[self.receiver_name]),
                }
            ],
            "producers": [
                { "destination-url" : sc.full_url_of(self.aliases["heartbeat"]) } 
            ], 
        }
        
    def run(self):
        sc = self.scenario
        self._assert_first_session_exists()
        heartbeat = self.create_heartbeat(str(self))
        try:
            view_url = compose_url(sc.sessions[0].browsers[0], 'view')
            sc.start()
            heartbeat.start()
            count = 0
            for i, message in enumerate(sc.client.get_messages(view_url)):
                print "\nMessage ", i
                write_message(message)()
                count = count + 1
                print
            log.info("... found %d message(s)", count)
        finally:
            heartbeat.stop()
            del heartbeat
            sc.delete_connection()

class ReceiveLotsOfMessages(Demo):
    """I receive several messages from a consumer."""


    def __init__(self, scenario, aliases, receiver_name="Text"):
        super(ReceiveLotsOfMessages, self).__init__(scenario, aliases)
        self.receiver_name = receiver_name 
        self.use_jms_log = False

    def _create_session_config(self):
        """Create the session configuration used by this demo class.
        
        Specifies a consumer from which to receive messages. 
        """
        sc = self.scenario
        return {
            "consumers": [
                {
                   "destination-url" : sc.full_url_of(self.aliases[self.receiver_name]),
                }
            ]
        }

    def run(self,
            max_tries=10,
            time_out=3000,
            receiver_url=None,
            handler_generators=None):
        """Receive several messages from the provider.

        Assumes `self.scenario` has a first session with a configured consumer. 
        
        If `max_tries` is set to a positive value, several messages will be
        requested using the consumer, until either `max_tries` messages have
        been received or `max_tries` requests have been returned with no
        response.

        If `max_tries` is set to a negative value, messages will be retrieved
        continuously.

        On receiving a message, it is processed by the handler_generators.
        Each handler_generator should be a function that takes a message as an
        argument and returns either None or a function f().  
        
          - If None is returned, it means that the handler_generator could not
            handle the function.

          - If a function is returned, then the message is handled by invoking
            it.

        Each handler_generator in the list attempts generating the handling
        function until one of them does.  A warning is logged if a message is
        not handled.
        
        """
        self._assert_first_session_exists()
        sc = self.scenario

        if not handler_generators:
            handler_generators = [write_message]

        if not receiver_url:
            receiver_url = compose_url(sc.sessions[0].consumers[0], "receive") 

        sc.start()
        count = missed = 0
        try:
            while max_tries < 0 or (missed < max_tries and count < max_tries):
                try:
                    messages = sc.client.get_messages(
                        receiver_url,
                        config={"receive": { "timeout": str(hjb_long(time_out))}})
                    count = count + 1 
                    for message in messages:
                        for hg in handler_generators:
                            handling_function = hg(message)
                            if handling_function:
                                handling_function()
                                break
                        else:
                            log.warn("No handler found for message: \n%s", message)
                except HJBError:
                    missed = missed + 1
                except:
                    raise
        finally:
            sc.delete_connection()

class MonitorHeartbeats(ReceiveLotsOfMessages):
    """I monitor 'heartbeat' messages emitted by other demo applications.

    I consume messages from the *heartbeat* publisher, and maintain the
    statuses of every distinct client in a simple table.

    """
    
    def __init__(self, scenario, aliases):
        super(MonitorHeartbeats, self).__init__(scenario, aliases)

    def _create_session_config(self):
        """Create the session configuration used by this demo class.
        
        Specifies a consumer for the *heartbeat* publisher. 
        """
        sc = self.scenario
        return {
            "consumers": [
                {
                   "destination-url" : sc.full_url_of(self.aliases["heartbeat"]),
                }
            ]
        }

    def run(self):
        """Listen for all 'heartbeat' messages.

        Consumes messages from the *heartbeat* publisher, maintaining the
        status of every distinct client that sends a heartbeat.

        """
        self._assert_first_session_exists()
        sc = self.scenario
        heartbeat_retrieval_url = compose_url(sc.sessions[0].consumers[0], "receive")
        monitor = HeartbeatMonitor()
        monitor.start()
        # The main thread has to stay alive as non-daemon threads
        # do not seem to respond to KeyboardInterrupt and SystemExit
        while True: 
            try:
                super(MonitorHeartbeats, self).run(
                        max_tries=-1,
                        time_out=3000,
                        handler_generators=[monitor.create_handler_generator],
                        receiver_url=heartbeat_retrieval_url)
            except:
                monitor.stop()
                del monitor 
                raise

class ReceiveJmsLogs(ReceiveLotsOfMessages):
    """I listen for log messages sent over JMS and log them locally."""

    def __init__(self, scenario, aliases):
        super(ReceiveJmsLogs, self).__init__(scenario, aliases)

    def configure_session(self):
        """Create the session used by this in this demo class.
        
        Extends `Demo.configure_session` to update the connection config so
        that the client Id is set if it is not already assigned.

        """
        connection_config = self.scenario.config.setdefault("connection", {})
        connection_config["clientId"] = "hjbclient"
        super(ReceiveJmsLogs, self).configure_session()

    def _create_session_config(self):
        """Create the session configuration used by this demo class.
        
        Specifies a durable subscriber for a *logmessage* publisher. 
        """
        sc = self.scenario
        return {
            "subscribers": [
                {
                   "destination-url" : sc.full_url_of(self.aliases["logmessage"]),
                   "subscriber-name" : "hjbclient",
                }
            ]
        }
        
    def run(self):
        """Listen for all logging message sent over JMS.
        
        Assumes that `self.scenario` has as a first session with a configured
        durable subscriber.

        Subscribes to the *logmessage* publisher, adds all logged messages to a
        single logfile.

        """
        self._assert_first_session_exists()
        sc = self.scenario
        h = logging.StreamHandler()
        h.setFormatter(logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s'))
        logging.getLogger("fromjms").addHandler(h)
        log_retrieval_url = compose_url(sc.sessions[0].subscribers[0], "receive")
        super(ReceiveJmsLogs, self).run(
                max_tries=-1,
                time_out=3000,
                handler_generators=[accept_jms_log],
                receiver_url=log_retrieval_url)

class ReceiveOneMessage(ReceiveLotsOfMessages):
    """I receive a single message from a consumer."""

    def __init__(self, scenario, aliases, receiver_name="Text"):
        super(ReceiveOneMessage, self).__init__(scenario, aliases)
        self.receiver_name = receiver_name 

    def _create_session_config(self):
        """Create the session configuration used by this demo class."""
        sc = self.scenario
        return {
            "consumers": [
                {
                   "destination-url" : sc.full_url_of(self.aliases[self.receiver_name]),
                }
            ]
        }

    def run(self, **kw):
        super(ReceiveOneMessage, self).run(max_tries=1, **kw)


class SendAndWaitForConversationResponse(ReceiveLotsOfMessages):
    """I send a message and wait for a response to it.
    
    This method is designed to be run at the same time as another process
    running the demo `EchoInConversation`.
        
    The producer selects a message at random from the messages generated by
    `self.message_generator`, adding a header with a specific value that is
    known to the receiving demo process (the value of `conversation_id`).
        
    The consumer waits for a message identified by a specific value that is
    known by both the sending and receiving demos (the conversation_id).
    This is done by using a JMS message selector expression to 
    configure the consumer.  The consumer times out if no message is
    received after waiting for the timeout period.

    The producer sends the message, then the consumer waits for a response with
    same conversation_id, timing out after `time_out` seconds if none is
    received.

    """

    def __init__(self, scenario, aliases,
            receiver_name="Text", 
            sender_name="Map", 
            conversation_id="hjb_demo",
            message_generator=five_simple_messages_generator()):
        super(SendAndWaitForConversationResponse, self).__init__(scenario, aliases)
        self.message_generator = message_generator
        self.receiver_name = receiver_name
        self.sender_name = sender_name
        self.conversation_id = conversation_id

    def _create_session_config(self):
        """Create the session configuration used by this demo class.
        
        Specifies

        Two producers:
          - one is used to send the response,
          - the other sends heartbeat messages

        One consumer
          - used to receive the triggering request.  The consumer is configured
            to use a selector, so other applications may be send messages on
            the consumer destination at the same time without affecting this
            demo.  If they attempt to receive messages at the same time, if
            they don't have use their own selectors (or even if they do), they
            might get the message meant for this demo.

        """
        sc = self.scenario
        al = self.aliases
        self.configured_producers = {
            self.sender_name : al[self.sender_name],
            "heartbeat" : al["heartbeat"]
        }
        destinations = self.get_producer_aliases()
        return {
            "producers": [
                { "destination-url" : sc.full_url_of(self.aliases[d]) } 
                        for d in destinations
            ], 
            "consumers": [
                { 
                    "destination-url"  : sc.full_url_of(al[self.receiver_name]),
                    "message-selector" : "hjb_conversation_id = '%s'" % self.conversation_id,
                } 
            ], 
        }

    def send_a_message(self):
        """Send a randomly chosen message to the receiving destination."""

        random_message = choice(list(self.message_generator))         
        request = deepcopy(random_message)
        request.headers =  {
            "hjb_demo": hjb_bool(True),
            "hjb_send_to": self.sender_name,
            "hjb_conversation_id": self.conversation_id
        }
        sc = self.scenario
        sc.client.send_message(
                request,
                self.find_sending_url_for(request))
        print "... [**    SENT     **] message with conversation_id: %s to %s" % (self.conversation_id, self.sender_name) 
        log.info("... sent message with headers %s", str(request.headers))


    def run(self, time_out=30000, **kw):
        """Send the message, then construct and send the response.
        
        Time's out after `time_out` milliseconds.
        
        """
        heartbeat = self.create_heartbeat(str(self))
        try:
            heartbeat.start()
            self.send_a_message()
            print "... [**   WAITING   **] for a response" 
            sys.stdout.flush()
            super(SendAndWaitForConversationResponse, self).run(
                    max_tries=1, 
                    time_out=time_out,
                    **kw)
        finally:
            print
            try:
                heartbeat.stop()
                del heartbeat
            except:
                pass 

class EchoInConversation(SendAndWaitForConversationResponse):
    """I wait to receive a message and then send a response to it.
         
    This demo is designed to be run at the same time as another process
    running the `SendMessageThenWaitForResponse` demo.
   
    The consumer waits for a message identified by a specific value that is
    known by both the sending and receiving demos (the conversation_id).
    This is done by using a JMS message selector expression to 
    configure the consumer.  The consumer times out if no message is
    received after waiting for the timeout period.

    On receiving the message, it is sent back to the sender using the
    configured producer with the body unchanged.

    """

    def __init__(self, scenario, aliases,
            receiver_name="Map", sender_name="Text", conversation_id="hjb_demo"):
        super(EchoInConversation, self).__init__(
                scenario, 
                aliases, 
                receiver_name=receiver_name, 
                sender_name=sender_name, 
                conversation_id=conversation_id)

    def run(self, time_out=30000):
        """Wait for the message, then construct and send the response.
        
        Time's out after `time_out`.
        
        """
        print "... [**   WAITING   **] message with conversation_id %s from %s" % (self.conversation_id, self.receiver_name), 
        sys.stdout.flush()
        heartbeat = self.create_heartbeat(str(self))
        try:
            heartbeat.start()
            ReceiveLotsOfMessages.run(
                    self,
                    max_tries=1, 
                    time_out=time_out, 
                    handler_generators=[self.create_handler_generator])
        finally:
            print
            try:
                heartbeat.stop()
                del heartbeat
            except:
                pass 

    def create_handler_generator(self, message): 
        """Create a handler_generator function suitable for by `ReceiveLotsOfMessages.run()`."""
        cid = self.conversation_id
        if cid != message.headers.get("hjb_conversation_id", None):
            print "\r... [**   ERROR   **] bad headers: " +  str(message.headers)
            log.warning(
                    "message did not have the expected conversation_id [%s]; headers were: %s", 
                    cid, 
                    str(message.headers))
            return None

        def handle_message():
            """Create a new message with the same body, and sends to the return destination.
            
            The response message has empty headers, apart from :
            - the conversation_id
            - some hjb demo specific headers

            """
            log.info("... received message with headers %s", str(message.headers))
            print "\r... [**   RECEIVED  **]", 
            sys.stdout.flush()
            response = deepcopy(message)
            response.headers =  {
                "hjb_demo": hjb_bool(True),
                "hjb_send_to": self.sender_name,
                "hjb_conversation_id": self.conversation_id
            }
            sc = self.scenario
            sc.client.send_message(
                    response,
                    self.find_sending_url_for(response))
            log.info("... sent response with headers %s", str(response.headers))
            print "\r... [**  RESPONDED  **] "
            sys.stdout.flush()
        return handle_message
         

class SendLotsOfMessages(SendEachJmsMessageType): 
    """I periodically send messages to the configured demo destinations.""" 

    def __init__(
            self, 
            scenario, 
            aliases,
            message_generator=five_simple_messages_generator()):
        super(SendLotsOfMessages, self).__init__(scenario, aliases)
        self.message_generator = message_generator

    def run(self, period=36.0):
        """Sends a message periodically.

        The messages are sent every `period` seconds; they are produced by
        `self.message_generator`, which yields a new messages each time it is
        invoked.
        
        """
        self._assert_first_session_exists()
        sc = self.scenario
        
        def send_next_message():
            try:
                message = message_generator.next()
                global send_seqno
                send_seqno = send_seqno + 1
                message.headers["hjb_demo_seqno"] = str(hjb_long(send_seqno))
                log.info("... sending message with headers \n%s", message.headers)
                print "\r... %s has sent [%d] message(s)" % (str(self), send_seqno), 
                sys.stdout.flush()
                sc.client.send_message(message, self.find_sending_url_for(message))
            except (KeyboardInterrupt, SystemExit) :
                heartbeat.stop()
                sc.delete_connection()
                del send_seqno
                raise
      
        global send_seqno # needs to be global, its accessed from multiple threads
        send_seqno = 0
        heartbeat = self.create_heartbeat(str(self))
        message_generator = cycle(self.message_generator)
        send_timer = RepeatingTimer(period, send_next_message)
        send_timer.setDaemon(True)

        sc.start()
        heartbeat.start()
        send_timer.start()
        while True: 
            # The main thread has to stay alive as non-daemon threads
            # do not seem to respond to KeyboardInterrupt and SystemExit
            try:
                send_timer.join(heartbeat.period)
            except (KeyboardInterrupt, SystemExit) :
                heartbeat.stop()
                sc.delete_connection()
                send_timer.cancel()
                del send_timer
                raise
