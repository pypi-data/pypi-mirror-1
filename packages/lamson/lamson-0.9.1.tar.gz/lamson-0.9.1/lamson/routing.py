"""
The meat of Lamson, doing all the work that actually takes an email and makes
sure that your code gets it.

The three most important parts for a programmer are the Router variable, the
StateStorage base class, and the @route, @route_like, and @stateless decorators.

The lamson.routing.Router variable (it's not a class, just named like one) is
how the whole system gets to the Router.  It is an instance of RoutingBase and
there's usually only one.

The lamson.routing.StateStorage is what you need to implement if you want Lamson
to store the state in a different way.  By default the lamson.routing.Router
object just uses a default MemoryStorage to do its job.  If you want to use a
custom storage, then in your config/boot.py (or config/testing.py) you would set
lamson.routing.Router.STATE_STORE to what you want to use.

Finally, when you write a state handler, it has functions that act as state
functions for dealing with each state.  To tell the Router what function should
handle what email you use a @route decorator.  To tell the Route that one
function routes the same as another use @route_like.  In the case where a state
function should run on every matching email, just use the @stateless decorator
after a @route or @route_like.

If at any time you need to debug your routing setup just use the lamson routes
command.
"""

from __future__ import with_statement
from functools import wraps
import re
import logging
import sys
import email.utils
import shelve
import threading

ROUTE_FIRST_STATE = 'START'

class StateStorage(object):
    """
    The base storage class you need to implement for a custom storage
    system.
    """
    def get(self, module, sender):
        """
        You must implement this so that it returns a single string
        of either the state for this combination of arguments, OR
        the ROUTE_FIRST_STATE setting.
        """
        raise NotImplementedError("You have to implement a StateStorage.get.")

    def set(self, module, sender, state):
        """
        Set should take the given parameters and consistently set the state for 
        that combination such that when StateStorage.get is called it gives back
        the same setting.
        """
        raise NotImplementedError("You have to implement a StateStorage.set.")

    def clear(self):
        """
        This should clear ALL states, it is only used in unit testing, so you 
        can have it raise an exception if you want to make this safer.
        """
        raise NotImplementedError("You have to implement a StateStorage.clear for unit testing to work.")


class MemoryStorage(StateStorage):
    """
    The default simplified storage for the Router to hold the states.  This
    should only be used in testing, as you'll lose all your contacts and their
    states if your server shutsdown.  It is also horribly NOT thread safe.
    """
    def __init__(self):
        self.states = {}

    def get(self, module, sender):
        key = self.key(module, sender)
        try:
            return self.states[key]
        except KeyError:
            self.set(module, sender, ROUTE_FIRST_STATE)
            return ROUTE_FIRST_STATE

    def set(self, module, sender, state):
        key = self.key(module, sender)
        self.states[key] = state

    def key(self, module, sender):
        return repr([module, sender])

    def clear(self):
        self.states.clear()


class ShelveStorage(MemoryStorage):
    """
    Uses Python's shelve to store the state of the Routers to disk rather than
    in memory like with MemoryStorage.  This will get you going on a small
    install if you need to persist your states (most likely), but if you 
    have a database, you'll need to write your own StateStorage that 
    uses your ORM or database to store.  Consider this an example.
    """
    def __init__(self, database_path):
        """Database path depends on the backing library use by Python's shelve."""
        self.database_path = database_path
        self.lock = threading.RLock()

    def get(self, module, sender):
        """
        This will lock the internal thread lock, and then retrieve from the
        shelf whatever module you request.  If the module is not found then it
        will set (atomically) to ROUTE_FIRST_STATE.
        """
        with self.lock:
            store = shelve.open(self.database_path)
            try:
                key = store[self.key(module, sender)]
            except KeyError:
                self.set(module, sender, ROUTE_FIRST_STATE)
                key = ROUTE_FIRST_STATE
            return key

    def set(self, module, sender, state):
        """
        Acquires the self.lock and then sets the requested state in the shelf.
        """
        with self.lock:
            store = shelve.open(self.database_path)
            store[self.key(module, sender)] = state
            store.close()

    def clear(self):
        """
        Primarily used in the debugging/unit testing process to make sure the
        states are clear.  In production this could be a bad thing.
        """
        with self.lock:
            store = shelve.open(self.database_path)
            store.clear()
            store.close()



class RoutingBase(object):
    """
    The self is a globally accessible class that is actually more like a
    glorified module.  It is used mostly internally by the lamson.routing 
    decorators (route, route_like, stateless) to control the routing 
    mechanism.

    It keeps track of the registered routes, their attached functions, the
    order that these routes should be evaluated, any default routing captures,
    and uses the MemoryStorage by default to keep track of the states.

    You can change the storage to another implementation by simple setting:

        self.STATE_STORE = OtherStorage()

    In a config/settings.py file.

    RoutingBase does locking on every write to its internal data (which usually
    only happens during booting and reloading while debugging), and when each
    handler's state function is called.  ALL threads will go through this lock,
    but only as each state is run, so you won't have a situation where the chain
    of state functions will block all the others.  This means that while your
    handler runs nothing will be running, but you have not guarantees about 
    the order of each state function.

    However, this can kill the performance of some kinds of state functions,
    so if you find the need to not have locking, then use the @nolocking 
    decorator and the Router will NOT lock when that function is called.  That
    means while your @nolocking state function is running at least one other
    thread (more if the next ones happen to be @nolocking) could also be
    running.

    It's your job to keep things straight if you do that.
    """

    def __init__(self):
        self.REGISTERED = {}
        self.ORDER = []
        self.DEFAULT_CAPTURES = {}
        self.STATE_STORE=MemoryStorage()
        self.HANDLERS=set()
        self.RELOAD=False
        self.lock = threading.RLock()
        self.call_lock = threading.RLock()

    def register_route(self, format, fn):
        """
        Registers this function fn into the routes mapping based on the
        format given.  Format should be a regex string ready to be handed to
        re.compile.
        """
        with self.lock:
            if format in self.REGISTERED:
                self.REGISTERED[format][1].append(fn)
            else:
                self.ORDER.append(format)
                self.REGISTERED[format] = (re.compile(format), [fn])

    def match(self, address):
        """
        This is a generator that goes through all the routes and
        yields each match it finds.  It only matches on the 
        address portion of "First Last" <address> formatted
        addresses.
        """
        name, real_address = email.utils.parseaddr(address)
        for format in self.ORDER:
            regex, functions = self.REGISTERED[format]
            match = regex.match(real_address)
            if match:
                yield functions, match.groupdict()

    def defaults(self, **captures):
        """
        Updates the defaults for routing captures with the given settings.

        You use this in your handlers or your config/settings.py to set
        common regular expressions you'll have in your @route decorators.
        This saves you typing, but also makes it easy to reconfigure later.

        For example, many times you'll have a single host="..." regex
        for all your application's routes.  Put this in your settings.py
        file using route_defaults={'host': '...'} and you're done.
        """
        with self.lock:
            self.DEFAULT_CAPTURES.update(captures)
    
    def in_state(self, fn, message):
        """
        Determines if this function's is in the state for the to/from in the
        message.  Doesn't apply to @stateless state handlers.
        """
        name, address = email.utils.parseaddr(message['from'])
        state = self.STATE_STORE.get(fn.__module__, address)
        return state and state == fn.__name__

    def in_error(self, fn, message):
        """
        Determines if the this function is in the 'ERROR' state, 
        which is a special state that self puts handlers in that throw
        an exception.
        """
        name, address = email.utils.parseaddr(message['from'])
        state = self.STATE_STORE.get(fn.__module__, address)
        return state and state == 'ERROR'


    def set_state(self, fn, message, state):
        """
        Sets the state of the given fn according to the message to the requested
        state.  This is also how you can force another FSM to a required state.
        """
        name, address = email.utils.parseaddr(message['from'])
        self.STATE_STORE.set(fn.__module__, address, state)


    def deliver(self, message, *args, **kw):
        """
        The meat of the whole Lamson operation, this method takes all the
        arguments given, and then goes through the routing listing to figure out
        which state handlers should get the gear.  The routing operates on a
        simple set of rules:

            1) Match on all functions that match the given To in their
            registered format pattern.
            2) Call all @stateless state handlers functions.
            3) Call the first method that's in the right state for the From/To.

        It will log which handlers are being run, and you can use the 'lamson route'
        command to inspect and debug routing problems.
        """
        if self.RELOAD: self.reload()

        for functions, kw in self.match(message['to']):
            to_call = []
            in_state_found = False

            for fn in functions:
                if lamson_setting(fn, 'stateless'):
                    to_call.append(fn)
                elif not in_state_found and self.in_state(fn, message):
                    to_call.append(fn)
                    in_state_found = True

            for fn in to_call:
                if lamson_setting(fn, 'nolocking'):
                    self.call_safely(fn, message, args, kw)
                else:
                    with self.call_lock:
                        self.call_safely(fn, message, args, kw)


    def call_safely(self, fn, message, args, kw):
        """
        Used by self to call a function and log exceptions rather than
        explode and crash.
        """
        try:
            fn(message, *args, **kw)
            logging.debug("Message to %s was handled by %s.%s",
                          message['to'], fn.__module__, fn.__name__)
        except:
            logging.exception("!!! ERROR handling %s.%s", fn.__module__, fn.__name__)
            self.set_state(fn, message, 'ERROR')

    def clear_states(self):
        """Clears out the states for unit testing."""
        with self.lock:
            self.STATE_STORE.clear()

    def clear_routes(self):
        """Clears out the routes for unit testing and reloading."""
        with self.lock:
            self.REGISTERED.clear()
            del self.ORDER[:]

    
    def load(self, handlers):
        """
        Loads the listed handlers making them available for processing.
        This is safe to call multiple times and to duplicate handlers
        listed.
        """
        with self.lock:
            self.HANDLERS.update(handlers)
            for module in self.HANDLERS:
                __import__(module, globals(), locals())

    def reload(self):
        """
        Performs a reload of all the handlers and clears out all routes,
        but doesn't touch the internal state.
        """
        with self.lock:
            self.clear_routes()
            for module in sys.modules.keys():
                if module in self.HANDLERS:
                    reload(sys.modules[module])


Router = RoutingBase()

class route(object):
    """
    The @route decorator is attached to state handlers to configure them in the
    Router so they handle messages for them.  The way this works is, rather than
    just routing working on only messages being sent to a state handler, it also uses
    the state of the sender.  It's like having routing in a web application use
    both the URL and an internal state setting to determine which method to run.

    However, if you'd rather than this state handler process all messages
    matching the @route then tag it @stateless.  This will run the handler 
    no matter what and not change the user's state.
    """

    def __init__(self, format, **captures):
        """
        Sets up the pattern used for the Router configuration.  The format
        parameter is a simple pattern of words, captures, and anything you
        want to ignore.  The captures parameter is a mapping of the words in
        the format to regex that get put into the format.  When the pattern is
        matched, the captures are handed to your state handler as keyword
        arguments.

        For example, if you have:

            @route("(list_name)-(action)@(host)",
                list_name='[a-z]+',
                action='[a-z]+', host='test\.com')
            def STATE(message, list_name=None, action=None, host=None):
                ....

        Then this will be translated so that list_name is replaced with [a-z]+,
        action with [a-z]+, and host with 'test.com' to produce a regex with the
        right format and named captures to that your state handler is called
        with the proper keyword parameters.

        You should also use the Router.defaults() to set default things like the
        host so that you aren't putting it into your code.
        """
        self.captures = Router.DEFAULT_CAPTURES.copy()
        self.captures.update(captures)
        self.format = self.parse_format(format, self.captures)

    def __call__(self, fn):
        """Returns either a decorator that does a stateless routing or
        a normal routing."""
        self.setup_accounting(fn)

        if lamson_setting(fn, 'stateless'):
            @wraps(fn)
            def routing_wrapper(message, *args, **kw):
                next_state = fn(message, *args, **kw)
        else:
            @wraps(fn)
            def routing_wrapper(message, *args, **kw):
                assert Router.in_state(fn, message), "State handler %s called but not in that state." % fn.__name__

                next_state = fn(message, *args, **kw)

                if next_state:
                    Router.set_state(fn, message, next_state.__name__)

        Router.register_route(self.format, routing_wrapper)
        return routing_wrapper

    def __get__(self, obj, type=None):
        """
        This is NOT SUPPORTED.  It is here just so that if you try to apply
        this decorator to a class's method it will barf on you.
        """
        raise NotImplementedError("Not supported on methods yet, only module functions.")

    def parse_format(self, format, captures):
        """Does the grunt work of convertion format+captures into the regex."""
        for key in captures:
            format = format.replace("(" + key + ")", "(?P<%s>%s)" % (key, captures[key]))
        return "^" + format + "$"

    def setup_accounting(self, fn):
        """Sets up an accounting map attached to the fn for routing decorators."""
        attach_lamson_settings(fn)
        fn._lamson_settings['format']= self.format
        fn._lamson_settings['captures'] = self.captures


def lamson_setting(fn, key):
    """Simple way to get the lamson setting off the function, or None."""
    return fn._lamson_settings.get(key)


def has_lamson_settings(fn):
    return "_lamson_settings" in fn.__dict__

def assert_lamson_settings(fn):
    """Used to make sure that the fn has been setup by a routing decorator."""
    assert has_lamson_settings(fn), "Function %s has not be setup with a @route first." % fn.__name__


def attach_lamson_settings(fn):
    """Use this to setup the _lamson_settings if they aren't already there."""
    if '_lamson_settings' not in fn.__dict__:
        fn._lamson_settings = {}


class route_like(route):
    """
    Many times you want your state handler to just accept mail like another
    handler.  Use this, passing in the other function.  It even works across
    modules.
    """
    def __init__(self, fn):
        assert_lamson_settings(fn)
        self.format = fn._lamson_settings['format']
        self.captures = fn._lamson_settings['captures']


def stateless(fn):
    """
    This simple decorator is attached to a handler to indicate to the
    Router.deliver() method that it does NOT maintain state or care about it.
    This is how you create a handler that processes all messages matching the
    given format+captures in a @route.

    Another way to think about a @stateless handler is that it is a passthrough
    handler that does its processing and then passes the results on to others.

    Stateless handlers are NOT guaranteed to run before the handler with state.
    """
    if has_lamson_settings(fn):
        assert not lamson_setting(fn, 'format'), "You must use @stateless AFTER @route or @route_like."
    
    attach_lamson_settings(fn)
    fn._lamson_settings['stateless'] = True

    return fn

def nolocking(fn):
    """
    Normally lamson.routing.Router has a lock around each call to all handlers
    to prevent them from stepping on eachother.  It's assumed that 95% of the
    time this is what you want, so it's the default.  You probably want
    everything to go in order and not step on other things going off from other
    threads in the system.

    However, sometimes you know better what you are doing and this is where
    @nolocking comes in.  Put this decorator on your state functions that you
    don't care about threading issues or that you have found a need to 
    manually tune, and it will run it without any locks.
    """
    attach_lamson_settings(fn)
    fn._lamson_settings['nolocking'] = True
    return fn


