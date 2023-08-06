import logging
from lamson import fsm, server, queue
from sqlalchemy import and_
from config import settings


def START(): return DELIVERING


def DELIVERING(session, message, list, host):
    """
    This is only used if we run a QueueReceiver and set DEBUG to False.
    It's intended for production deployment really.
    """
    deliver_to_relay(session, relay, message, list, host) 

def END(session, message, *args):
    return END

def ERROR(ext, state):
    return state



def deliver_to_members(session, relay, message, list, host):
    """
    Called externally to deliver.  It figures out from the
    settings.DELIVER_DIRECTLY whether it's supposed to send
    straight to the relay or enqueue for later.
    """
    if settings.DELIVER_DIRECTLY:
        logging.debug("DELIVERY is delivering directly to the relay")
        deliver_to_relay(session, relay, message, list, host)
    else:
        logging.debug("DELIVERY is going to enqueue rather than deliver.")
        enqueue_for_delivery(message)


def enqueue_for_delivery(message):
    q = queue.Queue(settings.queue_dir)
    q.push(str(message))


def deliver_to_relay(session, relay, message, list, host):
    """
    Uses the relay host to push out the messages to all the 
    subscribers.
    """
    query = session.query(fsm.FSMState)

    # query the debate fsm states for people who are on this list and
    # who are in the POSTING state so we can deliver to them
    members = query.filter(and_(fsm.FSMState.fsm == "app.handlers.debate", 
                                fsm.FSMState.recipient == list + "@" + host,
                                fsm.FSMState.state == "POSTING")).all()

    for member in members:
        logging.debug("Sending to member %s" % member.sender)
        msg = construct_header_insanity(message, member)
        relay.deliver(msg, To=member.sender, From=list + "@" + host)


def construct_header_insanity(message, member):
    body = message.msg.get_payload()
    list_addr = list + '@' + host

    msg = server.MailResponse(From=message['from'], To=list_addr, 
                           Subject=message['subject'], Body=body)

    msg["Sender"] = list_addr
    msg["Reply-To"] = list_addr
    msg["List-Id"] = list_addr
    msg["Return-Path"] = list_addr
    msg["In-Reply-To"] = message['Message-Id']
    msg["References"] = message['Message-Id']
    msg["Precedence"] = 'list'

    return msg

