from binascii import b2a_base64, a2b_base64
from UserList import UserList
import simplejson as json

# maximum length of a single message
MAX_LENGTH=600

# the various types of messages
STRING_TYPE = 1     # just a string
MSGID_TYPE = 2      # a message id which needs to be translated

ALL_TYPES = (STRING_TYPE, MSGID_TYPE)

class Message(object):
    """A Message object can store a message and any additional 
    attributes as long as they can be encoded in JSON format.
    Per default it only takes the message but you can add additional
    data via keyword arguments like this::
    
        msg = Message(u'my message', typ = 1, format='restructuredText')
        
    """

    def __init__(self, msg=u'', **kws):
        """initialize the message. ``msg`` MUST be unicode."""
        self.msg = msg
        # store additional keywords in the class
        for a,v in kws.items():
            setattr(self,a,v)

    def __repr__(self):
        return "<Message '%s'>" %self.msg

    def encode(self):
        """encoding a message basically means returning the instance dict"""
        return self.__dict__

    def decode(self, d):
        """decode a dictionary into this object"""
        self.__dict__ = d

class MessageList(UserList):
    """a list of messages

    You can store more than one message as a statusmessage. You simply store them
    inside this list like object.
    """

    def encode(self):
        """return a representation of all the messages included. 
        This is created by using this list and encoding it via JSON and base64.

        If the list is empty we return None so that the middleware can eventually
        delete the cookie.
        """
        if len(self) == 0:
            return None
        l = []
        for msg in self:
            l.append(msg.encode())

        return b2a_base64(json.dumps(l)).rstrip()

def decode(s):
    """decode a list of messages

    This returns a ``MessageList`` object which consists of individual
    ``Message`` object.

    First is decodes base64 and then the json string inside creating
    individual ``Message`` objects out of it.

    """

    # first we get a list of dictionaries
    l = json.loads(a2b_base64(s))

    # and now we convert those into Message objects
    msglist = MessageList()
    for d in l:
        m = Message()
        m.decode(d)
        msglist.append(m)
    return msglist

