
================
qc.statusmessage
================


Introduction
============

Sometimes in web application development the need arises to show a status message
or similar notices to a user. This can of course be easily done in some success page
but sometimes this page is rendered by a different request because of a redirect.
In these cases you can use some query parameters or similar methods but that's not
always easy to use or might even have security problems.

``qc.statusmessage`` tries to solve this problem by giving you a ``MessageList`` object
which is put into the WSGI environment on ingress and processed on egress to store a list of
messages inside a cookie.

For information on how to use it check out the 
`online documentation <http://quantumcore.org/docs/qc.statusmessage>`_ or
check out the `source code repository <http://hg.quantumcore.org/qc.statusmessage>`_.

