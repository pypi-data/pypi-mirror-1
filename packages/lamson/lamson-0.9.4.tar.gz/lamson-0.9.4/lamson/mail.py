"""
The lamson.mail module contains nothing more than wrappers around the big work
done in lamson.encoding.  These are the actual APIs that you'll interact with
when doing email, and they mostly replicate the lamson.encoding.MailBase 
functionality.

The main design criteria is that MailRequest is mostly for reading email 
that you've received, so it doesn't have functions for attaching files and such.
MailResponse is used when you are going to write an email, so it has the
APIs for doing attachments and such.
"""


import mimetypes
from lamson import encoding


class MailRequest(object):
    """
    This is what's handed to your handlers for you to process.  The information
    you get out of this is *ALWAYS* in Python unicode and should be usable 
    by any API.  Modifying this object will cause other handlers that deal
    with it to get your modifications, but in general you don't want to do
    more than maybe tag a few headers.
    """
    def __init__(self, Peer, From, To, Data):
        """
        Peer is the remote peer making the connection (sometimes the queue
        name).  From and To are what you think they are.  Data is the raw
        full email as received by the server.
        """

        self.msg = encoding.from_string(Data)
        self.Peer = Peer
        self.From = From or self.msg['from']
        self.To = To or self.msg['to']
        
        if 'from' not in self.msg: 
            self.msg['from'] = self.From
        if 'to' not in self.msg:
            self.msg['to'] = self.To

    def all_parts(self):
        """Returns all multipart mime parts.  This could be an empty list."""
        return self.msg.parts


    def matches(self, expr):
        """Used to see if this message matches the given regex.  It's
        used by the router to get the message to the right handlers."""
        matches = expr.match(self.To[0])

        if matches:
            return matches.groups()
        else:
            return None

    def body(self):
        """
        Always returns a body if there is one.  If the message
        is multipart then it returns the first part's body, if
        it's not then it just returns the body.  If returns
        None then this message has nothing for a body.
        """
        if self.msg.parts:
            return self.msg.parts[0].body
        else:
            return self.msg.body

    def __contains__(self, key):
        return self.msg.__contains__(key)

    def __getitem__(self, name):
        return self.msg.__getitem__(name)

    def __setitem__(self, name, val):
        self.msg.__setitem__(name, val)

    def __delitem__(self, name):
        del self.msg[name]

    def __str__(self):
        """
        Converts this to a string usable for storage into a queue or 
        transmission.
        """
        return encoding.to_string(self.msg)

    def __repr__(self):
        return "From: %r" % [self.Peer, self.From, self.To]

    def to_message(self):
        """
        Converts this to a Python email message you can use to
        interact with the python mail APIs.
        """
        return encoding.to_message(self.msg)


class MailResponse(object):
    """
    You are given MailResponse objects from the lamson.view methods, and
    whenever you want to generate an email to send to someone.  It has
    the same basic functionality as MailRequest, but it is designed to
    be written to, rather than read from (although you can do both).

    You can easily set a Body or Html during creation or after by
    passing it as __init__ parameters, or by setting those attributes.

    You can initially set the From, To, and Subject, but they are headers so
    use the dict notation to change them:  msg['From'] = 'joe@test.com'.

    The message is not fully crafted until right when you convert it with
    MailResponse.to_message.  This lets you change it and work with it, then
    send it out when it's ready.
    """
    def __init__(self, To=None, From=None, Subject=None, Body=None, Html=None):
        self.Body = Body
        self.Html = Html
        self.msg = encoding.MailBase([('To', To), ('From', From), ('Subject', Subject)])
        self.multipart = self.Body and self.Html
        self.attachments = []

    def as_string(self):
        """Legacy function that will go away."""
        return str(self)

    def as_message(self):
        """Legacy function that will go away."""
        return self.to_message()
    
    def __contains__(self, key):
        return self.msg.__contains__(key)

    def __getitem__(self, key):
        return self.msg.__getitem__(key)

    def __setitem__(self, key, val):
        return self.msg.__setitem__(key, val)

    def __delitem__(self, name):
        del self.msg[name]

    def attach(self, filename, content_type=None):
        """
        Takes the given file, figures out the mime type and
        required encoding, and then sets it up to be attached
        when you call to_message.
        """
        self.multipart = True

        if not content_type:
            content_type, encoding = mimetypes.guess_type(filename)

        self.attachments.append((filename, content_type))

    def update(self, message):
        """
        Used to easily set a bunch of heading from another dict
        like object.
        """
        for k in message.keys():
            self.msg[k] = message[k]

    def __str__(self):
        """
        Converts to a string.
        """
        return str(self.to_message())

    def _encode_attachment(self, filename, content_type):
        data = open(filename).read()
        self.msg.attach_file(filename, data, content_type, 'attachment')

    def to_message(self):
        """
        Figures out all the required steps to finally craft the
        message you need and return it.  The resulting message
        is also available as a self.msg attribute.

        What is returned is a Python email API message you can
        use with those APIs.  The self.msg attribute is the raw
        lamson.encoding.MailBase.
        """
        if self.Body and self.Html:
            self.multipart = True

        if self.multipart:
            self.msg.body = None
            if self.Body:
                self.msg.attach_text(self.Body, 'text/plain')

            if self.Html:
                self.msg.attach_text(self.Html, 'text/html')

            for args in self.attachments:
                self._encode_attachment(*args)

        elif self.Body:
            self.msg.body = self.Body
            self.msg.content_encoding['Content-Type'] = ('text/plain', {})

        elif self.Html:
            self.msg.body = self.Html
            self.msg.content_encoding['Content-Type'] = ('text/html', {})

        return encoding.to_message(self.msg)

    def all_parts(self):
        """
        Returns all the encoded parts.  Only useful for debugging
        or inspecting after callin to_message().
        """
        return self.msg.parts
