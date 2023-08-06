import unittest
from qc.statusmessage.message import Message, MessageList, decode


class TestMessage(unittest.TestCase):

    def test_create_message(self):
        """test creating a message"""
        msg = Message(u"Dies ist ein Test")
        self.assertEqual(msg.msg, u"Dies ist ein Test")

    def test_create_message_with_attributes(self):
        msg = Message(u"Dies ist ein Test", a=3, b="test", c=u"test2", d=3.2)
        self.assertEqual(msg.msg, u"Dies ist ein Test")
        self.assertEqual(msg.a, 3)
        self.assertEqual(msg.b, "test")
        self.assertEqual(msg.c, u"test2")
        self.assertEqual(msg.d, 3.2)

    def test_encode(self):
        """test encoding a message"""
        msg = Message(u"Dies ist ein Test")

        res = msg.encode()
        self.assertEqual(res,{'msg': u'Dies ist ein Test'})

    def test_decode(self):
        """test decoding a message"""
        d={'msg': u'foobar'}
        msg = Message()
        msg.decode(d)

        self.assertEqual(msg.msg, u"foobar")

    def test_list_encode(self):
        """test basic list encoding functionality"""
        msg1 = Message(u"Message 1")
        msg2 = Message(u"Message 2", c=3)
        msglist = MessageList()
        msglist.append(msg1)
        msglist.append(msg2)

        res = msglist.encode()

        self.assertEqual(res,u"W3sibXNnIjogIk1lc3NhZ2UgMSJ9LCB7Im1zZyI6ICJNZXNzYWdlIDIiLCAiYyI6IDN9XQ==")


    def test_list_decode(self):
        """test list decoding"""
        from binascii import b2a_base64
        from simplejson import dumps
        data = b2a_base64(dumps([{'msg': u'Message 1'},
                {'msg': u'Message 2', 'c':3, 'test': u'new stuff'}]))
        msglist = decode(data)
        self.assertEqual(len(msglist),2)
        msg1, msg2 = msglist

        self.assertEqual(msg1.msg, u"Message 1")
        self.assertEqual(msg2.msg, u"Message 2")
        self.assertEqual(msg2.c, 3)
        self.assertEqual(msg2.test, u"new stuff")


class TestMiddleware(unittest.TestCase):

    def _makeOne(self, *arg, **kw):
        from qc.statusmessage.middleware import StatusMessageMiddleware
        return StatusMessageMiddleware(*arg, **kw)

    def test_write_message(self):
        app = DummyApplication(msg='Message 1')
        start_response = DummyStartResponse()
        smm = self._makeOne(app,'cookie')

        env = {}
        result = smm(env, start_response)

        cookie_header = start_response.headers[0][1]
        self.assertEqual(cookie_header, u'cookie=W3sibXNnIjogIk1lc3NhZ2UgMSJ9XQ==; Path=/;')

    def test_read_message(self):
        """test if a set message can be read again"""

        # make the next request with this cookie
        cvalue = '''cookie="W3sibXNnIjogIk1lc3NhZ2UgMSJ9XQ=="'''

        app = DummyApplication()
        start_response = DummyStartResponse()
        smm = self._makeOne(app,'cookie')

        env = {'HTTP_COOKIE': cvalue}
        result = smm(env, start_response)
        self.failUnless('qc.statusmessage' in env.keys())

        msglist = env['qc.statusmessage']
        self.assertEqual(len(msglist),1)
        self.assertEqual(msglist.pop().msg,u'Message 1')

    def test_add_message(self):
        """test if a message can be added"""

        # make the next request with this cookie
        cvalue = '''cookie="W3sibXNnIjogIk1lc3NhZ2UgMSJ9XQ=="'''

        app = DummyApplication(msg=u"another one")
        start_response = DummyStartResponse()
        smm = self._makeOne(app,'cookie')

        env = {'HTTP_COOKIE': cvalue}
        result = smm(env, start_response)
        self.failUnless('qc.statusmessage' in env.keys())

        msglist = env['qc.statusmessage']
        self.assertEqual(len(msglist),2)
        self.assertEqual(msglist.pop().msg,u'another one')
        self.assertEqual(msglist.pop().msg,u'Message 1')
        self.assertEqual(len(msglist),0)

    def test_if_cookie_is_deleted_on_empty_list(self):
        # first round: put a message into a cookie and we tell the application
        # to consume it (e.g. pop() it)
        cvalue = '''cookie="W3sibXNnIjogIk1lc3NhZ2UgMSJ9XQ=="'''
        app = DummyApplication(consume=True)
        start_response = DummyStartResponse()
        smm = self._makeOne(app,'cookie')

        env = {'HTTP_COOKIE': cvalue}

        # here the application is called which is told to delete the message
        result = smm(env, start_response)

        # here we get the new cookie value
        cvalue = start_response.headers[0][1]
        self.failUnless(cvalue.startswith('cookie=; Path=/; max-age=0; expires'))


class DummyApplication(object):

    # TODO: find out why headers is not [] when using it this way
    #def __init__(self, msg=None, headers = [], status='200 OK'):
    def __init__(self, msg=None, status='200 OK', headers=None, consume=False):
        self.msg = msg
        self.status = status
        if headers is None:
            headers = []
        self.headers = headers
        self.consume = consume

    def __call__(self, environ, start_response):
        ml = environ['qc.statusmessage']
        if self.msg is not None:
            ml.append(Message(self.msg))
        if self.consume:
            ml.pop()
        self.environ = environ
        self.start_response = start_response(self.status, self.headers)
        return ['hello world']

class DummyStartResponse(object):
    def __call__(self, status, headers, exc_info=None):
        self.status = status
        self.headers = headers
        self.exc_info = exc_info

