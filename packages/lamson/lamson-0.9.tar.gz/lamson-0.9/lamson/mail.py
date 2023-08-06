"""
Python's email support is very complete, but very inconsistent.  The whole
purpose of lamson.mail is to just smooth this out as much as possible and make
incoming and outgoing mail easier to work with.

It is designed in sort of a "request/response" way, even though SMTP isn't a
request/response type of protocol.  The way the state handlers operate though
this makes sense, and fits most applications.

When your state function is called, you get a MailRequest object to work with
but you probably shouldn't modify it except to set headers for other state
functions (like stateless ones).  You also get MailRequest object from
lamson.queue operations, to keep things consistent.

When you want to craft an email response you use the MailResponse class to make
it.  This lets you set attachments, HTML bodies, and all the usual email
crafting things.
"""

import email
from email.utils import getaddresses, formataddr
from email import encoders
from email.message import Message
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import mimetypes
from os import path

class MailRequest(object):
    """
    Basic container for all the things that an internal mail message needs to be
    processed.  We could just use the Python email.Message alone, but then we'd
    lose the original elements.  Instead we use both the email.Message and the
    original elements for better analysis.
    """
    def __init__(self, Peer, From, To, Data):
        """
        Peer is the hostname of the server that gave you the mail, it might be 
        the name of a queue, so I wouldn't use it for much, definitely not for
        authentication.  From, To, and Data are exactly what they say they are,
        with Data being the full text of the message (not just the body).
        """
        self.Data = Data
        self.msg = email.message_from_string(Data)
        self.Peer = Peer
        self.From = From or self.msg['from']
        self.To = To or self.msg['to']
        
        if 'from' not in self.msg: self.msg['from'] = self.From
        if 'to' not in self.msg: self.msg['to'] = self.To

        self.everyone = self.all_recipients()

    def all_recipients(self):
        """Taken from http://docs.python.org/lib/module-email.utils.html"""
        frs = self.msg.get_all('from', [])
        tos = self.msg.get_all('to', [])
        ccs = self.msg.get_all('cc', [])
        resent_tos = self.msg.get_all('resent-to', [])
        resent_ccs = self.msg.get_all('resent-cc', [])
        return getaddresses(frs + tos + ccs + resent_tos + resent_ccs)

    def matches(self, expr):
        """Attempts to match the regex on any possible recipient in
        the email's list."""
        matches = expr.match(self.To[0])
        if matches:
            return matches.groups()
        else:
            return None

    def body(self):
        """
        Returns the body of the mail.  If the body is too
        complex then this probably won't work, so use the self.msg
        attribute directly.
        """
        return self.msg.get_payload()

    def __contains__(self, key):
        return key in self.msg

    def __getitem__(self, name):
        return self.msg[name]

    def __setitem__(self, name, val):
        self.msg[name] = val

    def __delitem__(self, name):
        del self.msg[name]

    def __str__(self):
        """Uses normal Python string convert to get the message as a string."""
        return self.msg.as_string()

    def __repr__(self):
        return "From: %s, length: %d" % ((self.Peer, self.From, self.To),
                                         len(self.Data))


class MailResponse(object):
    """
    Portions of MailResponse code taken from Ryan Ginstrom's mailer.py module, MIT licensed.

    Represents an email message.
    
    Set the Subject, and Body attributes as plain-text strings.
    Optionally, set the Html attribute to send an HTML email, or use the
    attach() method to attach files.
    
    Even when sending an HTML email, you have to set the Body attribute as
    the alternative text version.
    
    Send using the Mailer class.
    """

    def __init__(self, To=None, From=None, Subject=None, Body=None, Html=None):
        self.attachments = []
        self.Body = Body
        self.Html = Html
        self.headers = {'To': To, 'From': From, 'Subject': Subject}

    def as_string(self):
        """Get the email as a string to send in the mailer"""

        if not self.attachments:
            return self._plaintext()
        else:
            return self._multipart()

    def as_message(self):
        """
        Converts the internal representation into something that the
        rest of Python can understand using email.message_from_string.
        """
        return email.message_from_string(self.as_string())
    
    def _plaintext(self):
        """Plain text email with no attachments"""

        if not self.Html:
            msg = MIMEText(self.Body)
        else:
            msg  = self._with_html()

        self._set_info(msg)
        return msg.as_string()
            
    def _with_html(self):
        """There's an html part"""

        outer = MIMEMultipart('alternative')
        
        part1 = MIMEText(self.Body, 'plain')
        part2 = MIMEText(self.Html, 'html')

        outer.attach(part1)
        outer.attach(part2)
        
        return outer

    def __contains__(self, key):
        return key in self.headers

    def __getitem__(self, name):
        return self.headers[name]

    def __setitem__(self, name, val):
        self.headers[name] = val

    def __delitem__(self, name):
        del self.headers[name]

    def _set_info(self, msg):
        """
        Sets the information for the message that gets created internally.
        Important thing to note is that the self.headers map takes precedence
        over any other headers you set.
        """
        for key in self.headers:
            msg[key] = self.headers[key]

    def _multipart(self):
        """The email has attachments"""

        msg = MIMEMultipart()
        
        msg.attach(MIMEText(self.Body, 'plain'))

        self._set_info(msg)
        msg.preamble = self.headers['Subject']

        for filename in self.attachments:
            self._add_attachment(msg, filename)
        return msg.as_string()

    def _add_attachment(self, outer, filename):
        ctype, encoding = mimetypes.guess_type(filename)
        if ctype is None or encoding is not None:
            # No guess could be made, or the file is encoded (compressed), so
            # use a generic bag-of-bits type.
            ctype = 'application/octet-stream'
        maintype, subtype = ctype.split('/', 1)
        fp = open(filename, 'rb')
        if maintype == 'text':
            # Note: we should handle calculating the charset
            msg = MIMEText(fp.read(), _subtype=subtype)
        elif maintype == 'image':
            msg = MIMEImage(fp.read(), _subtype=subtype)
        elif maintype == 'audio':
            msg = MIMEAudio(fp.read(), _subtype=subtype)
        else:
            msg = MIMEBase(maintype, subtype)
            msg.set_payload(fp.read())
            # Encode the payload using Base64
            encoders.encode_base64(msg)
        fp.close()
        # Set the filename parameter
        msg.add_header('Content-Disposition', 'attachment', filename=path.basename(filename))
        outer.attach(msg)

    def attach(self, filename):
        """
        Attach a file to the email. Specify the name of the file;
        Message will figure out the MIME type and load the file.
        """
        
        self.attachments.append(filename)

    def update(self, message):
        """Given an object that answers .items() it will replace the internal
        headers with that."""
        self.headers.update(dict(message.items()))

    def __str__(self):
        return self.as_string()

