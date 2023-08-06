import random
import logging
from lamson import queue, view

CONFIRMATIONS = {}
PENDING_QUEUE = "run/pending"

def push(message):
    pending = queue.Queue(PENDING_QUEUE)
    return pending.push(message)

def get(pending_id):
    pending = queue.Queue(PENDING_QUEUE)
    return pending.get(pending_id)

def verify(message, expect_id_number):
    try:
        id_number, pending_id = CONFIRMATIONS[message['from']]
        if expect_id_number == id_number:
            return get(pending_id)
        else:
            return None
    except KeyError:
        return None

def register(target, message):
    pending_id = push(message)

    id_number = "%x" % random.randint(0,100000)
    confirm_address = "%s-confirm-%s" % (target, id_number)

    CONFIRMATIONS[message['from']] = (id_number, pending_id)

    return confirm_address


def send(relay, target, message, template, vars):
    confirm_address = register(target, message)
    vars.update(locals())
    msg = view.respond(template, vars)
    relay.deliver(msg)

def clear():
    CONFIRMATIONS = {}

