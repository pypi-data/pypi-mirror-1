from lamson import server, utils, fsm
from lamson.queue import Queue
import re
import logging

TEST_QUEUE="run/queue"

try:
    from config import settings
    TEST_QUEUE=settings.queue_dir
except:
    logging.warning("No config.settings loaded, using %r as target test queue." % TEST_QUEUE)



def relay(hostname="127.0.0.1", port=8824):
    """Wires up a default relay on port 8824 (the default lamson log port)."""
    return server.Relay(hostname, port, debug=0)


def queue(queue_dir=TEST_QUEUE):
    """Creates a queue for you to analyze the results of a send, uses the
    TEST_QUEUE setting in settings.py if that exists, otherwise defaults to
    run/queue."""
    return Queue(queue_dir)


def clear_queue(queue_dir=TEST_QUEUE):
    """Clears the default test queue out, as created by lamson.testing.queue."""
    queue(queue_dir=TEST_QUEUE).clear()


def database_session():
    """Makes a default database connection based on the settings.database 
    configuration.  This means you need to have a config/settings.py file
    working."""
    from config import settings
    database = utils.configure_database(settings.database)
    session = database.session()
    return session


def clear_models(*models):
    """Clears out all the models from the database, doing a complete reset.
    Experience has shown that this won't scale, so doing a transaction based
    processis probably better."""
    for model in models:
        session = database_session()
        session.query(model).delete()
        session.commit()

def delivered(pattern, to_queue=None):
    """
    Checks that a message with that patter is delivered, and then returns it.

    It does this by searching through the queue directory and finding anything that
    matches the pattern regex.
    """
    q = to_queue or queue()
    for key in q.keys():
        msg = q.get(key)
        if not msg:
            # no messages in the queue
            return False

        regp = re.compile(pattern)
        if regp.search(str(msg)):
            msg = q.get(key)
            return msg

    # didn't find anything
    return False


class TestConversation(object):
    """
    Used to easily do conversations with an email server such that you
    send a message and then expect certain responses.
    """

    def __init__(self, relay, From, Subject):
        """
        This creates a set of default values for the conversation so that you
        can easily send most basic message.  Each method lets you override the
        Subject and Body when you send.
        """
        self.relay = relay
        self.From = From
        self.Subject = Subject

    def begin(self):
        """Clears out the queue and models so that you have a fresh start."""
        clear_queue()
        clear_models(fsm.FSMState)

    def say(self, To, Body, expect=None, Subject=None):
        """Say something to To and expect a reply with a certain address."""
        self.relay.send(To, self.From, Subject or self.Subject, Body)
        msg = None

        if expect:
            msg = delivered(expect)
            if not msg:
                print "MESSAGE IN QUEUE:"
                q = queue()
                for key in q.keys():
                    print "-----"
                    print q.get(key)

            assert msg, "Expected %r when sending to %r with '%s:%s' message." % (expect, 
                                          To, self.Subject or Subject, Body)
        return msg

