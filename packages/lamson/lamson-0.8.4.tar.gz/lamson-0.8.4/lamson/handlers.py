from __future__ import with_statement
from lamson import server, fsm, queue
import os
import logging

class LogHandler(server.MessageHandler):
    """Just logs whatever it gets using the logging API at level INFO."""

    def process(self, session, message, args):
        logging.info("--------------- %r\n%r\n%s\nItems: %s\n" %
                     (args, message, message, message.msg.items()))

class ForwardHandler(server.MessageHandler):
    """
    Takes the message and routes it to the relay.  Use this to make
    certain messages ignored or as a catch-all for messages not handled
    by the any others.
    """

    def process(self, session, message, args):
        logging.debug("Forwarding message from %r to relay %r." % (message.From, self.relay))
        self.relay.deliver(message)

class QueueHandler(server.MessageHandler):
    """
    Used to route messages that come in to a particular queue.  It is used 
    in the test suite so you can have messages sent somewhere and then inspect
    them later.  You can also use it to defer messages that come in so 
    you can do offline processing.
    """

    def __init__(self, queue_dir):
        self.queue = queue.Queue(queue_dir)
        self.name = queue_dir

    def process(self, session, message, args):
        logging.debug("Storing message from %r to queue %r" % (message.From, self.name))
        self.queue.push(str(message))


class Conversation(server.MessageHandler):
    """Used to handle a conversation for an FSM, and is the main meat of the
    Lamson server's operations."""

    def __init__(self, fsm_name, unique=False, reload=False):
        """
        Give the fully qualified FSM module name, and if you want the states of the 
        FSM to be unique for each sender+recipient then set unique=True.

        Use unique for situations where the FSM is per each target email, but if your FSM
        has to use email addresses to perform subsequent operations (like confirm emails),
        then don't use unique.
        """
        self.fsm_name = fsm_name
        self.relay = None
        self.lookup = None
        self.unique = unique
        self.reload = reload

    def process(self, session, message, args):
        """
        Takes the message and runs it through the FSM.  If the FSM
        isn't finished then it stores it in the db.  If it finished
        then it deletes the FSM's state from the db.
        """
        full_args = [session, message] + list(args)
        view = lambda x: self.lookup.get_template(x)

        globals = {'relay': self.relay, 'view': view, 'lookup': self.lookup}
        state = fsm.FSMModule(self.fsm_name, message['to'], message['from'], globals)

        if self.reload: state.reload()

        state.load_state(session, self.unique)
        state.event(session, message, *args)
        state.store_state(session)

