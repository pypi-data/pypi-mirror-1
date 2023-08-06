import logging
from sqlalchemy import MetaData, Table, Column, String, Integer, DateTime, and_
from sqlalchemy.orm import mapper
import datetime

LOADED_FSM_MODULES = {}


class FSMState(object):
    """Just stores the state about an FSM in the database."""

    def __init__(self, fsm=None, recipient=None, sender=None):
        self.fsm = fsm
        self.recipient = recipient
        self.sender = sender


def default_table(metadata, table_name="fsm_states"):
    table = Table(table_name, metadata, 
            Column('id', Integer, primary_key=True),
            Column('recipient', String(50), nullable=False),
            Column('sender', String(50), nullable=False),
            Column('state', String(50), nullable=False, default="START"),
            Column('fsm', String(50), nullable=False),
            Column("last_modified", DateTime,
                   default=datetime.datetime.now,onupdate=datetime.datetime.now,nullable=False)
    )
    mapper(FSMState, table)

def set_fsm_state(session, fsm, unique, To, From, state):
    """
    A quick little function for setting the state of another FSM.  Will
    probably replace with something more legit later.
    """
    state = FSMModule(fsm, To, From, {})
    state.load_state(session, unique)
    state.stored.state = "POSTING"
    state.store_state(session)

def fsm_event(session, fsm, unique, message, globals, *args):
    """
    Allows you to transition an FSM in one shot for convenience.
    """
    state = FSMModule(fsm, message['to'], message['from'], globals)
    state.load_state(session, unique)
    state.event(session, message, *args)
    state.store_state(session)


class FSMModule(object):

    def __init__(self, name, recipient, sender, globals, reload=False):
        """Given the name of an FSM module it will load the module and install the globals given."""
        self.fsm = self.import_fsm(name, globals)
        self.name = name
        self.recipient = recipient
        self.stored = None
        self.sender = sender
        self.globals = globals


    def load_state(self, session, unique_to=False):
        query = session.query(FSMState)

        if unique_to:
            self.stored = query.filter(and_(FSMState.fsm == self.name, FSMState.sender == self.sender, FSMState.recipient == self.recipient)).first()
        else:
            self.stored = query.filter(and_(FSMState.fsm == self.name, FSMState.sender == self.sender)).first()

        if not self.stored:
            self.stored = FSMState(fsm=self.name, 
                                   recipient=self.recipient, sender=self.sender)

        assert self.stored.fsm == self.name, "Got wrong FSM state returned: expected %s, got %s" % (self.name, self.stored.fsm)

        self.init_stored_state()

    def init_stored_state(self):
        if not self.stored.state: 
            self.state = self.fsm.START()
            self.stored.state = self.state.__name__
        else:
            try:
                self.state = self.fsm.__dict__[self.stored.state]
            except KeyError:
                logging.error("Handler %s does not have state '%s', it does have: %s" %
                              (self.fsm, self.stored.state, self.fsm.__dict__.keys()))
                self.state = None


    def store_state(self, session):
        """
        Using the fsm (an FSMModule) store_state 
        will update the fsm_state and store it in the database for
        later operations.
        """
        assert self.stored, "You haven't called load_state yet."

        session.add(self.stored)
        session.commit()

    def apply_globals(self, mod, vars):
        for k in vars:
            mod.__dict__[k] = vars[k]

    def import_fsm(self, name, vars):
        """
        Uses __import__ to load the request module and then forces the
        module's __dict__ to have the given vars so that it really has
        the globals set unlike the boldface lie that is the __import__ documentation.
        """
        if name in LOADED_FSM_MODULES:
            return LOADED_FSM_MODULES[name]

        mod = __import__(name, globals(), locals())

        # stupid hack to work around __import__ not really importing
        components = name.split('.')
        for comp in components[1:]:
            mod = getattr(mod, comp)

        if vars: self.apply_globals(mod, vars)

        return mod

    def reload(self):
        """Reloads the module for the FSM so that code changes appear."""
        logging.debug("Reloading FSM %s." % self.name)
        self.fsm = reload(self.fsm)
        self.apply_globals(self.fsm, self.globals)


    def is_finished(self):
        return self.state.__name__ == "END"

    def reset(self):
        logging.debug("### %s RESET.")
        self.state = None
        self.stored.state = None
        self.init_stored_state()


    def event(self, *args):
        """Runs the FSM and keeps track of the state for the next run."""
        assert self.state, "FSM %s is dead, reset it."

        logging.debug(">>> EVENT(%s '%s'): ARGS: %s"  % (self.state.__name__, self.state.__doc__, args))
        try:
            nextstate = self.state(*args)
        except RuntimeError, exc:
            logging.debug("!!! ERROR: ")
            nextstate = self.fsm.ERROR(exc, self.state)

        if nextstate == None:
            action = "AGAIN"
        elif nextstate != self.state:
            self.state = nextstate
            self.stored.state = self.state.__name__
            action = "TRANS"
        else:
            action = "STATE"

        if self.state:
            logging.debug("^^^ %s: %s" % (action, self.state.__name__))
        else:
            logging.debug("### %s END." % (self.name))

