"""
Uses the SpamBayes system to perform filtering and classification
of email.  It's designed so that you attach a single decorator
to the state functions you need to be "spam free", and then use the
lamson.spam.Filter code to do training.

SpamBayes comes with extensive command line tools for processing
maildir and mbox for spam.  A good way to train SpamBayes is to 
take mail that you know is spam and stuff it into a maildir, then
periodically use the SpamBayes tools to train from that.
"""

from functools import wraps
from lamson import queue
from spambayes import hammie, Options, storage
import os

class Filter(object):
    """
    This code implements simple filtering and is taken from the
    SpamBayes documentation.
    """
    def __init__(self, storage_file, config):
        options = Options.options
        options["Storage", "persistent_storage_file"] = storage_file
        options.merge_files(['/etc/hammierc', os.path.expanduser(config)])
        self.dbname, self.usedb = storage.database_type([])
        self.mode = self.h = None

    def open(self, mode):
        if self.h is None or self.mode != mode:
            if self.h is not None:
                if self.mode != 'r':
                    self.h.store()
                self.h.close()
            self.mode = mode
            self.h = hammie.open(self.dbname, self.usedb, self.mode)

    def close(self):
        if self.h is not None:
            if self.mode != 'r':
                self.h.store()
            self.h.close()
        self.h = None

    __del__ = close

    def newdb(self):
        self.open('n')
        self.close()

    def filter(self, msg):
        if Options.options["Hammie", "train_on_filter"]:
            self.open('c')
        else:
            self.open('r')
        return self.h.filter(msg)

    def filter_train(self, msg):
        self.open('c')
        return self.h.filter(msg, train=True)

    def train_ham(self, msg):
        self.open('c')
        self.h.train_ham(msg, Options.options["Headers", "include_trained"])
        self.h.store()

    def train_spam(self, msg):
        self.open('c')
        self.h.train_spam(msg, Options.options["Headers", "include_trained"])
        self.h.store()

    def untrain_ham(self, msg):
        self.open('c')
        self.h.untrain_ham(msg)
        self.h.store()

    def untrain_spam(self, msg):
        self.open('c')
        self.h.untrain_spam(msg)
        self.h.store()




class spam_filter(object):
    """
    This is a decorator you attach to states that should be protected from spam.
    You use it by doing:

        @spam_filter(ham_db, rcfile, spam_dump_queue, next_state=SPAMMING)

    Where ham_db is the path to your hamdb configuration, rcfile is the 
    SpamBayes config, and spam_dump_queue is where this filter should
    dump spam it detects.

    The next_state argument is optional, defaulting to None, but if you use
    it then Lamson will transition that user into that state.  Use it to mark
    that address as a spammer and to ignore their emails or do something
    fancy with them.
    """

    def __init__(self, storage, config, spam_queue, next_state=None):
        self.storage = storage
        self.config = config
        self.spam_queue = spam_queue
        self.next_state = next_state

    def __call__(self, fn):
        @wraps(fn)
        def category_wrapper(message, *args, **kw):
            if self.spam(message.to_message()):
                self.enqueue_as_spam(message.to_message())
                return self.next_state
            else:
                return fn(message, *args, **kw)
        return category_wrapper

    def __get__(self, obj, of_type=None):
        raise RuntimeError("Not supported on methods yet, only module functions.")

    def spam(self, message):
        """Determines if the message is spam or not."""
        spfilter = Filter(self.storage, self.config)
        spfilter.filter(message)
        if 'X-Spambayes-Classification' in message:
            return message['X-Spambayes-Classification'].startswith('spam')
        else:
            return 'ham'

    def enqueue_as_spam(self, message):
        """Drops the message into the configured spam queue."""
        outq = queue.Queue(self.spam_queue)
        outq.push(str(message))

