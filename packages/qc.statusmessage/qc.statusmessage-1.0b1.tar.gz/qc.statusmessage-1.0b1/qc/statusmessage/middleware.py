import time
from paste.request import get_cookies

from message import MessageList, decode


class StatusMessageMiddleware(object):
    """WSGI middleware for handling status messages in cookies

       Imagine you want to show some message like "blog has been added" 
       to the user after he hit "submit" on the addform. You most likely 
       want to do a redirect on a successful addition so that the user 
       cannot accidently hit "reload" and submit the data again.

       In order to do that this middleware offers you a possibility of
       storing one or more messages in a cookie. Therefor it provides
       a ``MessageList`` object in the WSGI environment under the key
       ``qc.statusmessage``. Check out the 
       ``qc.statusmessage.message.MessageList`` API for more information
       on how to use it but basically it's a simple list object and all
       methods usually available to lists apply.

       The contents of the ``MessageList`` object are serialized to a 
       cookie on egress and deserialized again on ingress. You can name
       the cookie in the constructor of this middleware.

    """

    def __init__(self, application, cookie_name="status"):
        """initialize the middleware with the application and a name
        of the cookie.
        """

        self.application = application
        self.cookie_name = cookie_name

    def __call__(self, environ, start_response):
        """On ingress lookup the cookie which is named as the
        ``self.cookie_name`` variable and deserialize the data
        into a ``MessageList`` object. This object is then put into
        the WSGI environment under ``qc.statusmessage``.

        On egress it will be done the other way round: The ``MessageList``
        object in the WSGI environment will be serialized to a cookie with
        it's name stored in ``self.cookie_name``.

        """

        cookies = get_cookies(environ)
        cookie = cookies.get(self.cookie_name, None)
        cookie_value = getattr(cookie,'value',None)
        if cookie_value is not None:
            msglist = decode(cookie_value)
        else:
            # create a new object from scratch
            msglist = MessageList()

        # place the message list in the environment
        environ['qc.statusmessage'] = msglist

        # create a replacement start_response function
        def replacement_start_response(status, headers, *args, **kwargs):
            """add the cookie to it on egress

            We still have the ``MessageList`` object available
            
            """
            cookie_value = msglist.encode()
            if cookie_value is not None:
                set_cookie='%s=%s; Path=/;' %(self.cookie_name, cookie_value)
            else:
                # delete the cookie
                set_cookie='%s=; Path=/; max-age=0; expires=%s' %(self.cookie_name, time.time()-60)
            headers.append(('Set-Cookie', set_cookie))
            return start_response(status, headers, *args, **kwargs)

        # now call the application with our custom start response wrapper
        return self.application(environ, replacement_start_response)

def make_statusmessage_middleware(app, global_conf, **local_conf):
    cookie_name = local_conf.get('cookie_name', None)
    return StatusMessageMiddleware(app, cookie_name)

