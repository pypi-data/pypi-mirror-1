"""
Contains classes used to process messages sent and received from a HJB Server
"""
from cStringIO import StringIO
from hjbtypes import hjbdecode

__all__ = [
    "message_types",
    "message_java_classes",
    "message_version",
    "message_version_header",
    "message_class_header",
    "HJBMessage",
    "HJBMapMessage",
    "HJBStreamMessage",
    "HJBObjectMessage",
    "HJBBytesMessage",
    "MessageReader",
]

def dict_as_text(dict):
    def as_text(header, value):
        return "%s=%s\n" % (header, value)
    out = StringIO()
    out.writelines([as_text(h,v) for h,v in dict.items()])
    return out.getvalue()

def text_as_dict(text):
    as_key_value_text = [
            l.strip().split("=", 1) 
            for l in StringIO(text).readlines() if l.strip()]
    return dict([(k, hjbdecode(v)) for k, v in as_key_value_text])   

class MessageReader(object):
    """I provide accesse to HJB Messages in a HTTP Response object"""

    def __init__(self, response):
        self._response = response
        self._raw = response.dataread
        self._fd = StringIO(self._raw)

    def reset(self):
        """Reset the MessageReader to the start of the response."""
        self._fd.seek(0)
        
    def messages(self):
        while 1:
            yield self.next_message()

    def next_message(self):
        """Read the next message from the response."""
        headers = {}
        fd = self._fd
        next = fd.readline()
        if not next : raise StopIteration
        while next:
            if not next.strip():
                next = fd.readline()
                continue
            if '%' == next.strip():
                break
            next = next.strip()
            header, value = next.split("=", 1)
            headers[header] = value.strip()
            next = fd.readline()
        payload = []
        next = fd.readline()
        
        while next:
            if '%%' == next.strip():
                break
            payload.append(next)
            next = fd.readline()
            
        if not message_class_header in headers:
            return HJBMessage(''.join(payload), headers)
        else:
            return java_hjb_link[headers[message_class_header]](
                payload=''.join(payload),
                headers=headers)

    
class HJBMessage(object):
    """I represent an encoded JMS message"""

    message_type = "Text"
    
    def __init__(self, payload, headers=None):
        """Assign the message headers and payload. 

        Assumes the header values and any relevant parts of the
        payload are **already** encoded.  The header values are stored
        in their string form.

        """
        if not headers:
            headers = {}
        self.headers = dict([(k, str(v)) for k, v in headers.items()])
        self.payload = payload

    def __str__(self):
        out = StringIO()
        if self.headers:
            out.write(dict_as_text(self.headers))
        out.write("%\n")
        out.write(self.payload)
        return out.getvalue()

class HJBMapMessage(HJBMessage):
    """I represent an encoded JMS Map message"""

    message_type = "Map"

    def __init__(self, payload=None, headers=None, **kw):
        """Assign the message headers and Map message payload.

        Assumes the headers and keyword argument values are
        **already** encoded.  the keyword arguments will form the
        payload of the MapMessage
        
        """
        if payload:
            HJBMessage.__init__(self, payload, headers)
        else:            
            HJBMessage.__init__(self, dict_as_text(kw), headers)

    def payload_as_dict(self):
        """
        Returns the payload message as a dictionary.
        """
        return text_as_dict(self.payload)


class HJBStreamMessage(HJBMessage):
    """I represent an encoded JMS Stream message"""

    message_type = "Stream"

    def __init__(self, values=None, payload=None, headers=None):
        """Assing the message headers and Stream message payload.

        Assumes the headers and optional arguementrs are **already**
        encoded.  The optional arguments in the given order will form
        the payload of the StreamMessage message

        """
        if payload or not values:
            HJBMessage.__init__(self, payload, headers)
        else:        
            stream_args_as_map = dict(enumerate(values))
            HJBMessage.__init__(self, dict_as_text(stream_args_as_map), headers)


    def payload_as_list(self):
        """
        Returns the payload message as a list
        """
        return [v for k, v in text_as_dict(self.payload)]


class HJBObjectMessage(HJBMessage):
    """I represent an encoded JMS Object message"""

    message_type = "Object"

    def __init__(self, payload, headers=None):
        """Assign the message headers and payload. 

        Assumes the headers and any relevant parts of the payload
        are **already** encoded.

        """
        HJBMessage.__init__(self, str(payload), headers)
        

class HJBBytesMessage(HJBMessage):
    """I represent an encoded JMS Bytes message"""

    message_type = "Bytes"

    def __init__(self, payload, headers=None):
        """Assign the message headers and payload. 

        Assumes the headers and any relevant parts of the payload
        are **already** encoded.

        """
        HJBMessage.__init__(self, str(payload), headers)


message_hjb_classes = [
    HJBMessage,
    HJBMapMessage,
    HJBObjectMessage,
    HJBStreamMessage,
    HJBBytesMessage,
]
message_types = dict([(cls.message_type, cls) for cls in message_hjb_classes])
message_java_classes = dict([(x, "javax.jms.%sMessage" % x) for x in message_types.keys()])
java_hjb_link = dict([("javax.jms.%sMessage" % x, message_types[x]) for x in  message_types.keys()])

message_class_header = "hjb_jms_message_interface"
message_version_header = "hjb_message_version"
message_version = "1.0"
