import smtplib
import smtpd
import asyncore
import threading
import email
import re
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import mapper, sessionmaker, relation
from email.utils import getaddresses, formataddr
from mako.template import Template
from mako.lookup import TemplateLookup
from mako import exceptions
from email import encoders
from email.message import Message
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import mimetypes
from os import path
from lamson import queue
import time


# Portions of MailResponse code taken from Ryan Ginstrom's mailer.py module, MIT licensed.
class MailResponse(object):
    """
    Represents an email message.
    
    Set the To, From, Subject, and Body attributes as plain-text strings.
    Optionally, set the Html attribute to send an HTML email, or use the
    attach() method to attach files.
    
    Even when sending an HTML email, you have to set the Body attribute as
    the alternative text version.
    
    Send using the Mailer class.
    """

    def __init__(self, To=None, From=None, Subject=None, Body=None, Html=None):
        self.attachments = []
        self._to = None
        self.To = To
        self.From = From
        self.Subject = Subject
        self.Body = Body
        self.Html = Html
        self.headers = {}

    def _get_to(self):
        addrs = self._to.replace(";", ",").split(",")
        return ", ".join([x.strip()
                          for x in addrs])
    def _set_to(self, to):
        self._to = to
    
    To = property(_get_to, _set_to,
                  doc="""The recipient(s) of the email.
                  Separate multiple To with commas or semicolons""")

    def as_string(self):
        """Get the email as a string to send in the mailer"""

        if not self.attachments:
            return self._plaintext()
        else:
            return self._multipart()
    
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
        msg['Subject'] = self.Subject
        msg['From'] = self.From
        msg['To'] = self.To

        for key in self.headers:
            msg[key] = self.headers[key]

    def _multipart(self):
        """The email has attachments"""

        msg = MIMEMultipart()
        
        msg.attach(MIMEText(self.Body, 'plain'))

        self._set_info(msg)
        msg.preamble = self.Subject

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

    def __str__(self):
        return self.as_string()




class MailRequest(object):
    """Basic container for all the things that an internal
    mail message needs to be processed.  We could just use the Python
    email.Message alone, but then we'd lose the original elements.  Instead we
    use both the email.Message and the original elements for better analysis.
    """
    def __init__(self, Peer, From, To, Data):
        self.Data = Data
        self.msg = email.message_from_string(Data)
        self.Peer = Peer
        self.From = From or self.msg['from']
        self.To = To or self.msg['to']
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






class Database(object):
    """Manages the database configuration for a Router to give
    the handlers access to the models.  It really doesn't do much
    other than setup sqlalchemy and get things going."""

    def __init__(self, metadata, url, log_level=logging.DEBUG):
        self.metadata = metadata
        self.url = url
        self.log_level = log_level
        logging.getLogger('sqlalchemy.engine').setLevel(self.log_level)

    def create(self):
        """Called just to create a database that hasn't been setup
        yet.  You are responsible for making all the tables and
        then calling this after metadata is configured."""
        logging.warning("Database created for URL %s." % self.url)
        self.metadata.create_all(self.engine)

    def configure(self):
        """Takes the url and metadata and fires it up so that you can
        call self.session() to work with the database."""
        logging.info("Database configured to use %s URL." % self.url)
        self.engine = create_engine(self.url)
        self.sessionmaker = sessionmaker(bind = self.engine)

    def session(self):
        """Uses the session maker to create a session you can use
        in a handler."""
        return self.sessionmaker()



class Relay(object):
    def __init__(self, hostname, port=25, debug=0):
        """
        The hostname and port we're connecting to, and the debug level (default to 0).
        Relay is available to every handler, and FSM handlers get it as a global.
        It does the hard work of delivering messages to the relay host.
        """
        self.hostname = hostname
        self.port = port
        self.debug = debug

    def deliver(self, message, To=None, From=None):
        """
        Takes a fully formed email message and delivers it to the
        configured relay server.

        You can pass in an alternate To and From, which will be used in the
        SMTP send lines rather than what's in the message.
        """
        relay_host = smtplib.SMTP(self.hostname, self.port)
        relay_host.set_debuglevel(self.debug)
        relay_host.sendmail(From or message.From, To or message.To, str(message))
        relay_host.quit()

    def __repr__(self):
        """ Used in logging and debugging to indicate where this relay goes."""
        return "<Relay to (%s:%d)>" % (self.hostname, self.port)

    def reply(self, original, From, Subject, Body):
        self.send(original['from'], From=From, Subject=Subject, Body=Body)

    def send(self, To, From, Subject, Body):
        msg = MailResponse(To=To, From=From, Subject=Subject, Body=Body)
        self.deliver(msg)




class Router(object):
    """
    More or less the main engine.  It takes a message and works it through
    the routing specifications.
    """

    def __init__(self, handlers, relay, db, directories, module_directory):
        """Will take a routing spec and build up the internal rules."""
        assert directories, "You must give the search directories for templates."
        assert module_directory, "You have to say where to put mako modules."
        self.lookup = TemplateLookup(directories=directories,
                                     module_directory=module_directory)

        self.handlers = [(re.compile(m), h) for m,h in handlers]
        self.relay = relay
        self.db = db

        # give each handler access to the relay and template lookup
        for match, handler in handlers:
            handler.relay = self.relay
            handler.lookup = self.lookup

    def deliver(self, message):
        """Goes through all the handlers matching them to the message, 
        and if a match is found, process is called.  The matching stops
        if any handler returns false."""
        for match, handler in self.handlers:
            a_hit = message.matches(match)
            if a_hit:
                logging.debug("Routed message %r to handler %r." % (a_hit, handler))
                session = self.db.session() if self.db else None
                handler.process(session, message, a_hit)
                return # all done, get out of here

        # fall through to here if nothing matched
        logging.warn("Message from %r to %r wasn't handled. Try ^(.+)@(.+)$ as a test." % 
                      (message.From, message.To))


class MessageHandler(object):
    """This is called by the Router to process a message.  The Router will set
    the self.relay variable so you can work with it to send replies."""

    def process(self, message, args, db):
        """This acts as a filter.  You implement this method, it takes the
        message, processes it.  The db argument is a SQLAlchemy session
        created just for this request so you can access the db."""


class SMTPReceiver(smtpd.SMTPServer):
    """Receives emails and hands it to the Router for further processing."""

    def __init__(self, receiver, router):
        self.host = receiver["host"]
        self.port = receiver["port"]
        self.router = router
        smtpd.SMTPServer.__init__(self, (self.host, self.port), None)

    def start(self):
        logging.info("SMTPReceiver started on %s:%d." % (self.host, self.port))
        self.poller = threading.Thread(target=asyncore.loop,
                kwargs={'timeout':0.1, 'use_poll':True})
        self.poller.start()

    def process_message(self, Peer, From, To, Data):
        try:
            logging.debug("Message received from Peer: %r, From: %r, to To %r." %
                          (Peer, From, To))
            self.router.deliver(MailRequest(Peer, From, To, Data))
        except:
            logging.exception("Exception while processing message from Peer: %r, From: %r, to To %r." %
                          (Peer, From, To))


    def close(self):
        logging.info("SMTPReceiver on %s:%d stopping." % (self.host, self.port))
        smtpd.SMTPServer.close(self)
        self.poller.join()


class QueueReceiver(object):
    """
    Rather than listen on a socket this will watch a queue directory and
    process messages it recieves from that.  It works in almost the exact
    same way otherwise.
    """

    def __init__(self, queue_dir, router, sleep=60):
        """
        The router should be fully configured and ready to work, the
        queue_dir can be a fully qualified path or relative.
        """
        self.router = router
        self.queue = queue.Queue(queue_dir)
        self.queue_dir = queue_dir
        self.sleep = sleep

    def start(self):
        """
        Start simply loops indefinitely sleeping and pulling messages
        off for processing when they are available.
        """

        logging.info("Queue receiver started on queue dir %s" %
                     (self.queue_dir))
        logging.debug("Sleeping for %d seconds..." % self.sleep)

        while True:
            time.sleep(self.sleep)

            q = queue.Queue(self.queue_dir)
            key, msg = q.pop()
            while key:
                logging.debug("Pulled message with key: %r off", key)
                self.process_message(msg)
                key, msg = q.pop()

    def process_message(self, msg):
        Data=str(msg)
        Peer = self.queue_dir # this is probably harmless but I should check it
        From = msg['from']
        To = [msg['to']]

        try:
            logging.debug("Message received from Peer: %r, From: %r, to To %r." % (Peer, From, To))
            self.router.deliver(MailRequest(Peer, From, To, Data))
        except:
            logging.exception("Exception while processing message from Peer: %r, From: %r, to To %r." %
                          (Peer, From, To))

