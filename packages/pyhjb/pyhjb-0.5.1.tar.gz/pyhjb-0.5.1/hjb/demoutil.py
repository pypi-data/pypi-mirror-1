"""
Utility functions and classes used by the py.hjb demo methods
"""

import sys
from os import getcwd
from os.path import walk, isfile, join as join_path

import time
import logging
import logging.handlers
import cPickle

from threading import _Timer, Lock
from itertools import cycle, chain
    
from hjb.hjbtypes import *
from hjb.hjbmessages import *
from hjb.hjbclient import HJBClient, SimpleMessagingScenario, HJBError, compose_url

__all__ = [
    "accept_jms_log",
    "write_message",
    "heartbeat_for",
    "five_simple_messages",
    "five_simple_messages_generator",
    "filesystem_message_generator",
    "ResponseFromFile",
    "RepeatingTimer",
    "Heartbeat",
    "HeartbeatMonitor",
    "JMSHandler",
    "PeriodicFlushMemoryHandler",
]
__docformat__ = "restructuredtext en"

def heartbeat_for(name, status="alive", **kw):
    """Create a heartbeat message.

    A heartbeat message is a `HJBMapMessage` contain a field *status*
    with value `status`, a field *application* with value `name` and
    any other fields and values specified by the keyword arguments.

    """
    headers = {
        "hjb_demo": hjb_bool(True),
        "hjb_send_to": "heartbeat",
    }
    return HJBMapMessage(
            application=name, 
            status=status,
            headers=headers,
            **kw)


def write_message(message, to=sys.__stdout__):
    def handle_message():
        print >> to, "*" * 60
        print >> to, message
        print >> to, "*" * 60
    return handle_message


def accept_jms_log(message):
    """
    Create a handling function used to process log messages sent by the
    `JMSHandler` if `message` is one of those.

    """
    if not message.headers.get("hjb_log", None):
        return None

    def handle_message():
        dict_ = cPickle.loads("" + hjbdecode(message.payload))
        dict_["name"] = "fromjms." + dict_["name"]
        raw_record = logging.makeLogRecord(dict_)
        logging.getLogger("fromjms").handle(raw_record)
    return handle_message
    
five_simple_messages = [

    HJBMessage("sent by PyHJB!",
               headers={"hjb_demo": hjb_bool(True),
                        "hjb_useful": "for sure"}),
        
    HJBMapMessage(value_foo=hjb_long(100),
                  value_bar=hjb_int(300),
                  value_baz=hjb_byte_array("boo!"),
                  value_bool=hjb_bool(True),
                  value_str="anything",
                  headers={"hjb_demo": hjb_bool(True)}),
        
    HJBStreamMessage(
            values=[
            hjb_long(1000),
            hjb_float(6000),
            hjb_byte(3)],
            headers={
            "hjb_demo": hjb_bool(True),
            "hjb_useful": "maybe"}),

    HJBBytesMessage(hjb_byte_array("sent (as bytes) by PyHJB!"),
                    headers={"hjb_demo": hjb_bool(True),
                             "hjb_useful": "not sure"}),
    
    # this object message, believe it or not, contains a
    # java.util.Date - it seems a little inefficient for something
    # that's only a timestamp!!
    HJBObjectMessage("(base64 rO0ABXNyAA5qYXZhLnV0aWwuRGF0ZWhqgQFLWXQZAwAAeHB3CAAAAQTrseBAeA==)",
                     headers={"hjb_demo": hjb_bool(True),
                              "hjb_useful": "unlikely"}),

]


def five_simple_messages_generator():
    for message in five_simple_messages:
        yield message


def filesystem_message_generator(paths=None,
                                 exts=None):
    """Generate messages sequentially from a set of directories in the filesystem.
    
    Recurse through each of the directories specified in `paths`, interpreting
    any file with an extension in `exts` as a text file containing a message in
    HJB's textual format.

    All the messages read from the filesystem in this way are yielded in turn.
    
    """
    if not paths:
        paths = [getcwd()]
    if not exts:
        exts = ['.msg']
        
    def next_message_in_path(message_generators, dir_path, file_names):
        """
        Get the next message from all recognized message files below directory
        `dir_path`.
        
        """
        file_names.sort()
        for f in file_names:
            if not f[-4:] in exts:
                continue
            file_path = join_path(dir_path, f)            
            if isfile(file_path):
                message_generators.append(MessageReader(ResponseFromFile(file_path)).messages())
                
    message_generators = []
    for dir_path in paths:
        walk(dir_path, next_message_in_path, message_generators)
        
    return chain(*message_generators)


def RepeatingTimer(*args, **kwargs):
    """Create a `_RepeatingTimer` instance"""
    return _RepeatingTimer(*args, **kwargs)


class _RepeatingTimer(_Timer):
    """I extend threading._Timer to continuosly repeat the timed task"""
    
    def __init__(self, interval, function, args=[], kwargs={}):
        _Timer.__init__(self, interval, function, args, kwargs)

    def run(self):
        while not self.finished.isSet():
            self._run()
            self.finished.wait(self.interval)

    def _run(self):
        self.function(*self.args, **self.kwargs)


class ResponseFromFile(object):
    """I simulate a response object's dataread field using text from a file"""
    
    def __init__(self, file_path):

        assert isfile(file_path), "File " + file_path + " is not a file!"
        self.file_path = file_path

    def _get_dataread(self):

        if not hasattr(self, "_dataread"):
            self._dataread = file(self.file_path).read()
        return self._dataread


class Heartbeat(object):
    """I send a heartbeat message to a JMS destination at regular intervals"""

    def __init__(self, name, client, producer_url, period=10):
        self.name = name
        self.client = client
        self.producer_url = producer_url
        self.period = period
    
    def start(self):
        """
        Start sending heartbeat messages
        """
        def send_heartbeat():
            self.client.send_message(
                    heartbeat_for(self.name, "alive"), 
                    self.producer_url)
            
        t = RepeatingTimer(self.period, send_heartbeat)
        t.setDaemon(True)
        self.client.send_message(
                heartbeat_for(self.name, "starting"), 
                self.producer_url)
        self._timer = t
        t.start()

    def stop(self):
        """Stop sending the heartbeat messages."""
        if hasattr(self, "_timer"):
            self.client.send_message(
                    heartbeat_for(self.name, "stopping"), 
                    self.producer_url)
            self._timer.cancel()
            del self._timer
        
class HeartbeatMonitor(object):
    """I maintain status information about various clients who've sent heartbeats."""

    log = logging.getLogger("hjb.demo.heartbeat") 
    
    def __init__(self, period=10, time_to_lapsed=120):
        self.period = period
        self.time_to_lapsed = time_to_lapsed
        self.recorded_statuses = {}
        self.unknown_count = 0
        self._lock = Lock()

    def start(self):
        """Start printing out the status table at regular intervals."""
        self._timer = RepeatingTimer(self.period, self.print_status_table)
        self._timer.start()

    def stop(self):
        """Stop printing out the status table at regular intervals."""
        if hasattr(self, "_timer"):
            self._timer.cancel()
            del self._timer

    def join(self):
        """Join the monitor's timer thread"""
        if hasattr(self, "_timer"):
            self._timer.join(self.period)


    def update_status_table(self, app, status, timestamp): 
        """
        Update the status table.

        """
        self._lock.acquire()
        try:
            as = self.recorded_statuses
            if as.get(app, None):
                old = as[app]
                if (old[1] != status):
                    self.log.info("%s is now %s (was) %s", app, status, old[1]) 
            as[app] = (app, status, timestamp)
        finally:
            self._lock.release()

    def print_status_table(self):
        """
        Prints the status table to standard output

        """
        def print_status_row(app, status, timestamp):
            if not timestamp:
                time_text = "unknown"
            else:
                time_text = time.strftime("%Y%m%d:%H:%M:%S", time.gmtime(timestamp/1000))
            print "%s\t%s\t%s" % (time_text, app, status)
        try: 
            self.check_for_lapsing()
            # clears the screen on ANSI terminals, http://en.wikipedia.org/wiki/ANSI_color
            print "\x1B[2J\x1B[1;1f" 
            print "*" * 22
            print "HJB Heartbeat Monitor"
            print "*" * 22
            print
            if not self.recorded_statuses:
                print "No applications registered"
            else:
                [print_status_row(a, s, t) for a, s, t in self.recorded_statuses.values()]
        except:
            self.stop()
            raise

    def check_for_lapsing(self):
        """
        Checks the status table for applications whose heartbeats are
        later than expected.

        """
        def update_lapsed(app, status, timestamp):
            if not timestamp or status.startswith("stopped") or status.startswith("lapsed"):
                return app, status, timestamp
            delta = current_time - timestamp/1000
            if delta < self.time_to_lapsed:
                return app, status, timestamp
            time_text = time.strftime("%Y%m%d:%H:%M:%S", time.gmtime(timestamp/1000))
            if status == "stopping":
                status = "stopped at %s" % (time_text,)
            else:
                status = "lapsed: (was [%s] at [%s])" % (status, time_text)
            return app, status, timestamp 
        current_time = time.time()
        self._lock.acquire()
        try:
            self.recorded_statuses = dict((
                    (a, update_lapsed(a, s, t)) 

                    for a, s, t 
                    in self.recorded_statuses.values()))
        finally:
            self._lock.release()
            
    def create_handler_generator(self, message):
        """
        Create a handler generator suitable for use with
        `hjb.demo.ReceiveLotsOfMessages.run` that updates the status table.
        
        """
        if "heartbeat" != message.headers.get("hjb_send_to", None):
            self.log.warning("message was not a heartbeat message --> headers %s", str(message.headers))
            return None

        def handle_message():
            """Get the name, status and timestamp from the message and
            update the status table using `self.update_status_table`.
            
            """
            headers = message.headers
            heartbeat_info = message.payload_as_dict()
            
            app = heartbeat_info.get("application", None)
            if not app:
                self.unknown_count += 1
                app = "unknown_" + str(self.unknown_count)
            status = heartbeat_info.get("status", "unknown")
            timestamp = headers.get("hjb.core.jms.timestamp", None)
            if timestamp:
                timestamp = hjbdecode(timestamp)
            self.update_status_table(app, status, timestamp)
        return handle_message
    
class PeriodicFlushMemoryHandler(logging.handlers.MemoryHandler):
    """
    I buffer logging records in memory, periodically flushing them to
    a target handler that is recreated on each flush.

    This is similar to the way MemoryHandler works in the python
    standard library, but has the advantage that it allows handlers to
    be setup in one thread and continue to be used by other threads
    after the initialising thread has stopped running.

    """

    def __init__(self, capacity, flush_level=logging.ERROR, target_generator=None):
        logging.handlers.MemoryHandler.__init__(self, capacity, flush_level)
        self.target_generator = target_generator

    def flush(self):
        if self.target_generator:
            self.target = self.target_generator()
            logging.handlers.MemoryHandler.flush(self)
            self.target.close()
            del self.target

class JMSHandler(logging.Handler):
    """
    I write log records, in pickle format, to a JMS destination via a HJB
    server. 
    
    This Handler is directly based on the SocketHandler in the python standard
    library, i.e,  
    
      - the pickle which is sent is that of the LogRecord's attribute
        dictionary (__dict__), so that the receiver does not need to have the
        logging module installed in order to process the logging event.

      - To unpickle the record at the receiving end into a LogRecord, use the
        `logging.makeLogRecord` function. 

    """
    
    def __init__(self, scenario):
        """
        Initialize the handler with a `SimpleMessagingScenario`.
        
        Assumes the first session in `scenario` has a single configured
        producer.  The producer will be used to send logging messages to a JMS
        message destination via a HJB server.

        """

        assert len(scenario.sessions[0].producers) > 0, "scenario's first session has no producers"
        logging.Handler.__init__(self)
        self.scenario = scenario
        self.client = scenario.client
        self.send_url = compose_url(scenario.sessions[0].producers[0], "send")  

    def make_pickle(self, record):
        """
        Pickle the record in binary format.

        Copied from the *SocketHandler.makePickle* method in the python
        standard library, modified to exclude the length prefix, as this is not
        required when communication over JMS.
        
        """
        ei = record.exc_info
        if ei:
            dummy = self.format(record) # just to get traceback text into record.exc_text
            record.exc_info = None  # to avoid Unpickleable error
        s = cPickle.dumps(record.__dict__, 1)
        if ei:
            record.exc_info = ei  # for next handler
        return s

    def make_message(self, record):
        """
        Create a Bytes Message from `record`.

        Creates a HJB Bytes Message by pickling the record, then using the
        pickle output as the body of the message.

        """
        p = self.make_pickle(record)
        return HJBBytesMessage(
                hjb_byte_array(p),
                headers={"hjb_log": hjb_bool(True),
                         "hjb_demo": hjb_bool(True),
                         "hjb_useful": "darn right"})
        
    def send(self, message):
        """
        Send a record using the configured producer.

        """
        self.client.send_message(message, self.send_url)

    def handle_error(self, record):
        """
        Handle an error during logging.

        """
        logging.Handler.handleError(self, record)

    def emit(self, record):
        """
        Emit a record.

        Creates a message from record and sends it to the configured JMS
        destination.

        """
        try:
            m = self.make_message(record)
            self.send(m)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handle_error(record)
