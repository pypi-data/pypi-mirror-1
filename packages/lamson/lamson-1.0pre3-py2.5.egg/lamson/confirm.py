import uuid
from lamson import queue, view

class ConfirmationStorage(object):
    def __init__(self, db={}):
        self.confirmations = db

    def clear(self):
        self.confirmations.clear()

    def key(self, target, from_address):
        return target + ':' + from_address

    def get(self, target, from_address):
        return self.confirmations.get(self.key(target, from_address), (None, None))

    def delete(self, target, from_address):
        try:
            del self.confirmations[self.key(target, from_address)]
        except KeyError:
            pass

    def store(self, target, from_address, expected_secret, pending_message_id):
        self.confirmations[self.key(target, from_address)] = (expected_secret,
                                                              pending_message_id)

class ConfirmationEngine(object):
    def __init__(self, pending_queue, storage):
        self.pending = queue.Queue(pending_queue)
        self.storage = storage

    def get_pending(self, pending_id):
        return self.pending.get(pending_id)

    def push_pending(self, message):
        return self.pending.push(message)

    def delete_pending(self, pending_id):
        self.pending.remove(pending_id)


    def cancel(self, target, from_address, expect_secret):
        secret, pending_id = self.storage.get(target, from_address)

        if secret == expect_secret:
            self.storage.delete(target, from_address)
            self.delete_pending(pending_id)

    def make_random_secret(self):
        return uuid.uuid4().hex

    def register(self, target, message):
        from_address = message['from']

        pending_id = self.push_pending(message)
        secret = self.make_random_secret()
        self.storage.store(target, from_address, secret, pending_id)

        return "%s-confirm-%s" % (target, secret)

    def verify(self, target, from_address, expect_secret):
        assert expect_secret, "Must give an expected ID number."

        secret, pending_id = self.storage.get(target, from_address)

        if secret == expect_secret:
            self.storage.delete(target, from_address)
            return self.get_pending(pending_id)
        else:
            return None

    def send(self, relay, target, message, template, vars):
        confirm_address = self.register(target, message)
        vars.update(locals())
        msg = view.respond(vars, template, To=message['from'],
                           From="%(confirm_address)s@%(host)s",
                           Subject="Confirmation required")

        msg['Reply-To'] = "%(confirm_address)s@%(host)s" % vars

        relay.deliver(msg)

    def clear(self):
        self.pending.clear()
        self.storage.clear()
