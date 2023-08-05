"""
Defines classes and functions for accessing the messaging services of
a JMS Provider via a HJB server.
"""
from httplib import HTTPConnection
from urllib import urlencode, basejoin, quote
from copy import deepcopy

from logging import getLogger as logger_for
import re

from hjbmessages import *

__all__ = [
    "session_object_types",
    "compose_url",
    "invoke_connection",
    "url_from_response",
    "invoke_hjb",
    "HJBError",
    "SessionObjects",
    "HJBClient",
    "SimpleHJBProfile",
    "main",
]

__version__ = "0.6.0"

# regex used to determine if a URI refers to an object is part
# of a connection
_connection_url_rx = re.compile("^(.*connection-\d+)")

log = logger_for("hjb.client")

session_object_types=[
    "consumers",
    "producers",
    "browsers",
    "subscribers"]

def _qq(url):
    return quote(quote(url))

def compose_url(start, *parts):
    """Compose a url from its component parts"""
    if not parts: return start
    if start[-1] != '/': start = start + '/'
    next = parts[0]
    if next[0] == '/': next = next[1:]
    return compose_url(basejoin(start, next), *parts[1:])

def invoke_connection(host,
                      url,
                      cmd="/start",
                      connection_rx =_connection_url_rx,
                      method ="GET"):
    """Invoke a command on the connection associated with `url`.

    This assumes that the url may be a child url of a connection, e.g,
    a session or one of its child objects.  It extracts the connection
    url from `url`, and invokes `cmd` on it.

    """

    match = connection_rx.match(url)
    if (not match):
        raise ValueError("URL: [" + url + "] does not specify a connection")
    return invoke_hjb(host,
                      match.groups()[0] + cmd,
                      method)

def url_from_response(response):
    """Get a url from a response."""
    
    return response.getheader('Location')

def invoke_hjb(host,
               url,
               method="POST",
               params=None,
               headers=None):
    """Send a request to a HJB server."""
    if not params:
        params = {}        
    if not headers:
        headers = {}
    headers.setdefault("Content-Type", "application/x-www-form-urlencoded")
          
    log.debug("invoked URI %s using %s with parameters %s", url, method, params)
    conn = HTTPConnection(host)
    conn.request(method,
                 _qq(url),
                 urlencode(params),
                 headers)
    response = conn.getresponse()
    response.dataread = response.read()
    conn.close()
    if response.status >= 400:
        raise HJBError(response)
    return response

class HJBError(Exception):
    """
    I am used to signal that a request to an HJB server did not
    complete successfully
    """
    
    def __init__(self, response):
        self.response = response

    def __str__(self):
        return str(self.response.status) + " " + self.response.reason


class SessionObjects(object):
    """
    I provide convenience attributes for accessing information about
    session objects after they have been created.

    """

    def __init__(self, session_object_responses):
        """
        `session_object_responses` is the map of {`session_object_type`: [list
           of responses of that type]}

        obtained during invocation of `HJBClient.make_session_objects`
           
        """
        self._responses = session_object_responses
        self._update_url_lists()

    def _update_url_lists(self):

        def add_url_list(object_type):
            if (object_type == "subscribers"):
                found_type = "durable-subscribers"
            else:
                found_type = object_type
            return object_type, map(url_from_response,
                                    responses.get(found_type, []))
        
        responses = self._responses
        self.__dict__.update(dict(add_url_list(t) for t in session_object_types))

    def __str__(self):
        return "".join(["\n" + t + ": " + str(getattr(self, t)) 
                for t in session_object_types if hasattr(self, t)]) 
        
    
class HJBClient(object):
    """
    I represent a connection to a HJB Server
    """

    def __init__(self, hostname, root):
        """Initialize the hostname and root url.

        Raises an error if a HttpConnection cannot successfully connect to
        `hostname`.
        
        """
        self.hostname = hostname
        HTTPConnection(hostname)
        self.root = root

    def start_connection_for(self, url):
        """Start the connection associated with the JMS object at `url`."""
        invoke_connection(self.hostname, url, cmd="/start")
        
    def stop_connection_for(self, url):
        """Stop the connection associated with the JMS object at `url`."""
        invoke_connection(self.hostname, url, cmd="/stop")
        
    def send_message(self,
                     message,
                     send_url,
                     message_type='Text',
                     config = {}):
        """Send a message to the producer at send_url."""
        if hasattr(message, "message_type"):
            message_type = message.message_type
        log.debug("sending message type %s", message_type)
        params = deepcopy(message.headers)
        params["message-to-send"] = message.payload
        params[message_class_header] = message_java_classes[message_type]
        params[message_version_header] = message_version
        response = invoke_hjb(self.hostname,
                              send_url,
                              params=params,
                              headers=config.get("headers", {}))
        

    def get_messages(self, receive_url, config={}):
        """Obtain an iterator over the messages retrieved from the consumer at receive_url."""
        response = invoke_hjb(self.hostname,
                              receive_url,
                              params=config.get("receive", {}),
                              headers=config.get("headers", {}))
        return MessageReader(response).messages()
        
    def delete(self, url):
        """Delete the JMS resource at `url`."""
        return invoke_hjb(self.hostname, url, method="DELETE")

    def add_new_session_objects(self, session_url, config):
        """Add the session objects specified by `config` to the session at session_url."""
        def create(object_type, object_args, created):
            if object_type == "subscribers":
                object_type = "durable-subscribers"
            log.debug("... creating session objects %s %s", object_type, object_args)
            log.debug("... session objects created so far: %s", created)
            return created.setdefault(object_type, []).append(
                invoke_hjb(self.hostname,
                           compose_url(session_url, "create-" + object_type[:-1]),
                           params=object_args,
                           headers=config.get("headers", {})))
        created = {}
        [[create(t, c, created) for c in config.get(t, [])] for t in session_object_types]
        return SessionObjects(created)

    def create_session(self, provider, factory_name, config, connection_url=None):
        """Make a new JMS session on the HJB Server.

        It uses `self.create_session_only` to create a new session on the HJB Server,
        then creates session objects, all using the same config

        """
        session_url = self.create_session_only(provider,
                                               factory_name,
                                               config,
                                               connection_url)[0]
        log.debug("... creating session at URI %s", session_url)
        return session_url, self.add_new_session_objects(session_url, config)

    def create_session_only(self,
                            provider,
                            factory_name,
                            config,
                            connection_url=None):
        """Make a new JMS session on the HJB Server.

        The session is created on the JMS connection with URL `self.connection_url`;
        if that is None, a new JMS connection is created

        """
        if not connection_url:
            connection_url = self.make_connection(provider, factory_name, config)[0]
        response = invoke_hjb(self.hostname,
                              compose_url(connection_url, "create"),
                              params=config.get("session", {}),
                              headers=config.get("headers", {}))
        return response.getheader("Location"), response

    def register_destination(self, provider, destination, config):
        """Register a JMS destination on the HJB server"""
        self._create_admin_object(provider,
                                  compose_url("destination", destination),
                                  config)

    def register_factory(self, provider, factory_name, config):
        """Register a JMS connection factory on the HJB server"""
        self._create_admin_object(provider,
                                  factory_name,
                                  config)

    def make_connection(self, provider, factory_name, config):
        """ Creates a new JMS connection on the HJB server."""
        self.register_factory(provider,
                              factory_name,
                              config)
        create_url = compose_url(self.root,
                                 provider,
                                 factory_name,
                                 "create")
        log.debug("... attempting to create conection with %s", create_url)
        response = invoke_hjb(self.hostname,
                              create_url,
                              params=config.get("connection", {}),
                              headers=config.get("headers", {}))
        log.debug("Created connection %s", response.getheader("Location"))
        return response.getheader("Location"), response

    def _create_admin_object(self,
                             provider,
                             object_name,
                             config):
        invoke_hjb(self.hostname,
                   compose_url(self.root, provider, "register"),
                   params=config.get("provider", {}),
                   headers=config.get("headers", {}))
        return invoke_hjb(self.hostname,
                          compose_url(self.root,
                                      provider,
                                      object_name,
                                      "register"),
                          method="GET",
                          headers=config.get("headers", {}))

class SimpleMessagingScenario(object):
    """
    I represent a typical set of interactions with a HJBServer.

    Typically, interactions with a HJBServer will use:
    
      - a fixed set of pre-determined Destinations
      
      - a single pre-determined Connection Factory
      
      - one connection, shared between multiple sessions

    I provide various methods that support the creation and use of 
    this simple scenario. 
      
    """

    def __init__(self, client, provider, factory, destinations=None, config=None):

        self.client = client
        self.provider = provider
        self.factory = factory        
        self.config = config
        self._initialised = False
        if not self.config:
            self.config = {}

        self.destinations = destinations
        if not self.destinations:
            self.destinations = []
            
    def reset_connection(self):
        """Reset this instance's connection objects on the server.

        Deletes the connection (an its children), then creates a new one.

        """
        self.delete_connection()
        self.start()
                    
    def start(self):
        """Start this instance's connection on the HJB server.

        This allows processing of message request for this instance to
        begin/resume.
           
        """
        self._initialise_hjb_if_needed()        
        self.client.start_connection_for(self._connection_url)

    def stop(self):
        """Stop this instances's connection on the HJB server

        While the connection is stopped, no messages can be sent or received.
           
        """
        self.client.stop_connection_for(self._connection_url)
        
    def delete_connection(self):
        """Delete this instance's connection from the HJB server.

        Removes the current connection and all its child objects, i.e. sessions
        and session objects from the HJB server.

        """
        self.client.delete(self._connection_url)
        del self._connection_url

    def shutdown_provider(self):
        """Shutdown the provider.

        Use with care!  This method will remove all factories and destinations
        created with the same provider name and configuration as this instance.
           
        """
        return self.client.delete(self._provider_url())

    def full_url_of(self, destination):
        """Return the url on this scenario's provider corresponding to the `destination`"""
        return compose_url(self.client.root, self.provider, "destination", destination) 
    
    def update_session(self, session_config, index=-1):
        """Update an existing JMS sesssion.

        Updates an existing JMS session by creating the session object
        specified in `session_config`. `session_config` is a map
        {`session_object_type`: {object-creation-args}}, where object-creation-args
        are the parameters to send in the creation request.

        The resulting session objects are appended to this instance's list of
        session objects.

        If the index is negative, 0 is used as the effective index, i.e., the
        first session is updated.  If there is no session corresponding to the
        effective index, a new session is created.
        
        """
        self._initialise_hjb_if_needed()        
        if index < 0:
            index = 0
        if index + 1 > len(self.session_urls):
            self.create_another_session(session_config)
        else:
            self.client.add_new_session_objects(self.session_urls[index], session_config)
            self.session_configs[index].update(session_config)
    
    def create_another_session(self, session_config):
        """Create another JMS session.

        Creates another JMS session, whose session objects are specified by
        `session_config`.  `session_config` is a map {`session_object_type`:
        {object-creation-args}}, where object-creation-args are the parameters
        to send in the creation request.

        The resulting session objects are appended to this instance's list of
        session objects.

        """
        self._initialise_hjb_if_needed()        
        current_config  = deepcopy(self.config)
        combined_config = deepcopy(session_config)
        combined_config.update(current_config)
        self.session_configs.append(combined_config)
        session_url, session_objects = self.client.create_session(
                self.provider,
                self.factory,
                combined_config,
                self._connection_url)
        self.sessions.append(session_objects)
        self.session_urls.append(session_url)
        
    def _initialise_hjb_if_needed(self):
        if self._initialised:
            return
        [self._register_destination(d) for d in self.destinations]
        self._register_factory(self.factory)
        self._make_the_connection()
        self.sessions = []
        self.session_configs = []
        self.session_urls = []
        self._initialised = True

    def _register_destination(self, destination):
        """Register this scenario's destination""" 
        self.client.register_destination(
            self.provider,
            destination,
            self.config)

    def _make_the_connection(self):
        """Create a connection using this scenario's provider, factory and configuration"""
        self._connection_url = self.client.make_connection(self.provider,
                                                           self.factory,
                                                           self.config)[0]

    def _register_factory(self, factory):
        """Register this scenario's connection factory""" 
        self.client.register_factory(
            self.provider,
            factory,
            self.config)
        
    def _admin_url(self, name):
        return compose_url(self.client.root,
                           self.provider,
                           name)
        
    def _provider_url(self):
        return compose_url(self.client.root,
                           self.provider)

    def _factory_url(self):
        return self._admin_url(self.factory)

    def _connection_url(self):
        return self._connection_url

def main():
    pass

if __name__ == '__main__':
    main()
