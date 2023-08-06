import random
import logging
from lamson import queue, view
from webapp.librelist.models import Confirmation
from config import settings

def push(message):
    pending = queue.Queue(settings.PENDING_QUEUE)
    return pending.push(message)

def get(pending_id):
    pending = queue.Queue(settings.PENDING_QUEUE)
    return pending.get(pending_id)

def verify(target, message, expect_id_number):
    confirmations = Confirmation.objects.filter(from_address=message['from'], 
                                               expected_secret=expect_id_number,
                                                list_name=target)
    if confirmations:
        conf = confirmations[0]
        if conf.expected_secret == expect_id_number:
            return get(conf.pending_message_id)
        else:
            return None
    else:
        return None

def register(target, message):

    confirmations = Confirmation.objects.filter(from_address=message['from'], 
                                                list_name=target)

    if confirmations:
        id_number = confirmations[0].expected_secret
    else:
        pending_id = push(message)

        id_number = "%x" % random.randint(0,100000)

        conf = Confirmation(from_address=message['from'],
                            expected_secret = id_number,
                            pending_message_id = pending_id,
                            list_name=target)
        conf.save()

    return "%s-confirm-%s" % (target, id_number)


def send(relay, target, message, template, vars):
    confirm_address = register(target, message)
    vars.update(locals())
    msg = view.respond(vars, template, To=message['from'],
                       From="%(confirm_address)s@%(host)s",
                       Subject="Confirmation required")

    msg['Reply-To'] = "%(confirm_address)s@%(host)s" % vars

    relay.deliver(msg)


def clear():
    """Only used by tests."""
    Confirmation.objects.all().delete()

