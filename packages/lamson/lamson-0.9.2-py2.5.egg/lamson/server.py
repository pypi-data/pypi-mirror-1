"""
The majority of the server related things Lamson needs to run, like receivers, 
relays, databases, and queue processors.
"""

import smtplib
import smtpd
import asyncore
import threading
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import mapper, sessionmaker, relation
from lamson import queue, mail, routing
import time
import traceback


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
    """
    Used to talk to your "relay server" or smart host, this is probably the most 
    important class in the handlers next to the lamson.routing.Router.
    It supports a few simple operations for sending mail, replying, and can
    log the protocol it uses to stderr if you set debug=1 on __init__.
    """
    def __init__(self, host='127.0.0.1', port=25, debug=0):
        """
        The hostname and port we're connecting to, and the debug level (default to 0).
        It does the hard work of delivering messages to the relay host.
        """
        self.hostname = host
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
        relay_host.sendmail(From or message['From'], To or message['To'], str(message))
        relay_host.quit()

    def __repr__(self):
        """Used in logging and debugging to indicate where this relay goes."""
        return "<Relay to (%s:%d)>" % (self.hostname, self.port)

    def reply(self, original, From, Subject, Body):
        """Calls self.send but with the from and to of the original message reversed."""
        self.send(original['from'], From=From, Subject=Subject, Body=Body)

    def send(self, To, From, Subject, Body):
        """
        Does what it says, sends an email.  If you need something more complex
        then look at lamson.mail.MailResponse.
        """
        msg = mail.MailResponse(To=To, From=From, Subject=Subject, Body=Body)
        self.deliver(msg)


class SMTPReceiver(smtpd.SMTPServer):
    """Receives emails and hands it to the Router for further processing."""

    def __init__(self, host='127.0.0.1', port=8825):
        """
        Initializes to bind on the given port and host/ipaddress.  Typically
        in deployment you'd give 0.0.0.0 for "all internet devices" but consult
        your operating system.

        This uses smtpd.SMTPServer in the __init__, which means that you have to 
        call this far after you use python-daemonize or else daemonize will
        close the socket.
        """
        self.host = host
        self.port = port
        smtpd.SMTPServer.__init__(self, (self.host, self.port), None)

    def start(self):
        """
        Kicks everything into gear and starts listening on the port.  This
        fires off threads and waits until they are done.
        """
        logging.info("SMTPReceiver started on %s:%d." % (self.host, self.port))
        self.poller = threading.Thread(target=asyncore.loop,
                kwargs={'timeout':0.1, 'use_poll':True})
        self.poller.start()

    def process_message(self, Peer, From, To, Data):
        """
        Called by smtpd.SMTPServer when there's a message received.
        """

        try:
            logging.debug("Message received from Peer: %r, From: %r, to To %r." %
                          (Peer, From, To))
            routing.Router.deliver(mail.MailRequest(Peer, From, To, Data))
        except:
            logging.exception("Exception while processing message from Peer: %r, From: %r, to To %r." %
                          (Peer, From, To))


    def close(self):
        """Doesn't do anything except log who called this, since nobody should.  Ever."""
        logging.error(traceback.format_exc())


class QueueReceiver(object):
    """
    Rather than listen on a socket this will watch a queue directory and
    process messages it recieves from that.  It works in almost the exact
    same way otherwise.
    """

    def __init__(self, queue_dir, sleep=10):
        """
        The router should be fully configured and ready to work, the
        queue_dir can be a fully qualified path or relative.
        """
        self.queue = queue.Queue(queue_dir)
        self.queue_dir = queue_dir
        self.sleep = sleep

    def start(self, one_shot=False):
        """
        Start simply loops indefinitely sleeping and pulling messages
        off for processing when they are available.

        If you give one_shot=True it will run once rather than do a big
        while loop with a sleep.
        """

        logging.info("Queue receiver started on queue dir %s" %
                     (self.queue_dir))
        logging.debug("Sleeping for %d seconds..." % self.sleep)

        while True:
            q = queue.Queue(self.queue_dir)
            key, msg = q.pop()
            while key:
                logging.debug("Pulled message with key: %r off", key)
                self.process_message(msg)
                key, msg = q.pop()

            if one_shot: 
                return
            else:
                time.sleep(self.sleep)

    def process_message(self, msg):
        """
        Exactly the same as SMTPReceiver.process_message but just designed for the queue's
        quirks.
        """
        Data=str(msg)
        Peer = self.queue_dir # this is probably harmless but I should check it
        From = msg['from']
        To = [msg['to']]

        try:
            logging.debug("Message received from Peer: %r, From: %r, to To %r." % (Peer, From, To))
            routing.Router.deliver(mail.MailRequest(Peer, From, To, Data))
        except:
            logging.exception("Exception while processing message from Peer: %r, From: %r, to To %r." %
                          (Peer, From, To))

