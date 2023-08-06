import random
import logging
from lamson import queue

CONFIRMATIONS = {}
PENDING_QUEUE = "run/pending"

def push(message):
    pending = queue.Queue(PENDING_QUEUE)
    return pending.push(message)

def get(pending_id):
    pending = queue.Queue(PENDING_QUEUE)
    return pending.get(pending_id)

def verify(message, expect_post_name, expect_id_number):
    try:
        post_name, id_number, pending_id = CONFIRMATIONS[message['from']]
        if expect_post_name == post_name and expect_id_number == id_number:
            return pending_id
        else:
            return None
    except KeyError:
        return None

def register(message, post_name, host, pending_id):
    id_number = "%x" % random.randint(0,100000)
    confirm_address = "%s-confirm-%s@osb.%s" % (post_name, id_number, host)

    CONFIRMATIONS[message['from']] = (post_name, id_number, pending_id)

    return confirm_address
