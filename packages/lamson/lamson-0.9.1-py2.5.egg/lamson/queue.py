"""
Simpler queue management than the regular mailbox.Maildir stuff.  You
do get a lot more features from the Python library, so if you need
to do some serious surgery go use that.  This works as a good
API for the 90% case of "put mail in, get mail out" queues.
"""

import mailbox
import os
from lamson import mail

class Queue(object):
    """
    Provides a simplified API for dealing with 'queues' in Lamson.
    It currently just supports maildir queues since those are the 
    most robust, but could implement others later.
    """

    def __init__(self, dir):
        self.dir = dir
        self.mbox = mailbox.Maildir(dir)

    def push(self, message):
        """
        Pushes the message onto the queue.  Remember the order is probably
        not maintained.  It returns the key that gets created.
        """
        return self.mbox.add(str(message))

    def pop(self):
        """
        Pops a message off the queue, order is not really maintained
        like a stack.

        It returns a (key, message) tuple for that item.
        """
        try:
            key, msg = self.mbox.popitem()
            return key, self.unstupify_python_message(msg)
        except KeyError:
            return None, None

    def get(self, key):
        """
        Get the specific message referenced by the key.  The message is NOT
        removed from the queue.
        """
        return self.unstupify_python_message(self.mbox.get(key))

    def remove(self, key):
        """Removes the queue, but not returned."""
        self.mbox.remove(key)
    
    def count(self):
        """Returns the number of messages in the queue."""
        return len(self.mbox)

    def unstupify_python_message(self, msg):
        """
        Converts whatever bullshit Python's maildir returns into
        something that can actually be used by a human.
        """
        data = str(msg) + "\n" + msg.fp.read()
        return mail.MailRequest(self.dir, msg['from'], msg['to'], data)

    def clear(self):
        """
        Clears out the contents of the entire queue.
        Warning: This could be horribly inefficient since it
        basically pops until the queue is empty.
        """
        # man this is probably a really bad idea
        while self.count() > 0:
            self.pop()
    
    def keys(self):
        """
        Returns the keys in the queue.
        """
        return self.mbox.keys()
