import logging
from lamson import fsm, server
import random

def START():
    return UNKNOWN


def UNKNOWN(session, message, list, action, host):
    if action == "unsubscribe":
        logging.debug("Ignoring user who doesn't really exist.")
    elif action == "subscribe":
        confirm_address = "%s-confirm-%d@%s" % (list, random.randint(0,10000), host)
        body = view('confirmation.msg').render(
                         list=list, confirm_address=confirm_address, action="subscribe")
        relay.reply(message, confirm_address, "Confirm your subscription to %s" % list, body)

        return JOINING
    else:
        body = view('unknown.msg', address=message['to'])
        relay.reply(message, list + "-noreply@" + host, "Invalid command %s" % action, body)


def JOINING(session, message, list, action, confirm_id, host):
    if action != 'confirm':
        body = view("confirm_expected.msg").render(
                         list=list, host=host, action=action, request_type="subscribe")
        relay.reply(message, list + "-noreply@" + host, "Confirmation reply expected" % action)
    else:
        fsm.set_fsm_state(session, "app.handlers.debate", True, list + "@" + host, message['from'], "POSTING")
        body = view("subscribed.msg").render(list=list, host=host)
        relay.reply(message, list + "-noreply@" + host, 
                         "You are now subscribed to %s" % list, body)

        return KNOWN


def KNOWN(session, message, list, action, host):
    confirm_address = "%s-confirm-%d@%s" % (list, random.randint(0,10000), host)

    if action == "unsubscribe":
        body = view("confirmation.msg").render(
                         list=list, confirm_address=confirm_address, action="unsubscribe")
        subject = "Confirm your UNSUBSCRIBE from %s" % list
        next =  UNSUBSCRIBING
    elif action == "subscribe":
        body = view("confirmation.msg").render(
                         list=list, confirm_address=confirm_address, action="subscribe")
        subject="Confirm your subscription to %s" % list
        next = SUBSCRIBING
    elif action == "pause":
        body = view("confirmation.msg").render(
                         list=list, confirm_address=confirm_address, action="pause")
        subject = "Confirm your pause request for %s" % list
        next = PAUSING
    elif action == "resume":
        body = view("confirmation.msg").render(
                         list=list, confirm_address=confirm_address, action="resume")
        subject = "Confirm your resume from %s" % list
        next = RESUMING
    else:
        body = view("unknown.msg").render(address=message['to'])
        confirm_address = list + "-noreply@" + host
        subject = "Invalid command %s" % action
        next = KNOWN

    relay.reply(message, confirm_address, subject, body)
    return next


def RESUMING(session, message, list, action, confirm_id, host):
    if action != 'confirm':
        reply_invalid_confirm(message, list, host, action)
    else:
        fsm.set_fsm_state(session, "app.handlers.debate", True, 
                          list + "@" + host, message['from'], "POSTING")

        body = view("resumed.msg").render(list=list)
        relay.reply(message, list + "-noreply@" + host, "Resumed your status on %s" % list, body)

        return KNOWN


def PAUSING(session, message, list, action, confirm_id, host):
    if action != 'confirm':
        reply_invalid_confirm(message, list, host, action)
    else:
        fsm.set_fsm_state(session, "app.handlers.debate", True, 
                          list + "@" + host, message['from'], "POSTING")

        body = view("paused.msg").render(list=list, host=host)
        relay.reply(message, list + "-resume@" + host, 
                         "Paused your status on %s" % list, body)
        return KNOWN


def SUBSCRIBING(session, message, list, action, confirm_id, host):
    # just punt for now, but will need to make this a little different later
    return JOINING(session, message, list, action, confirm_id, host)


def UNSUBSCRIBING(session, message, list, action, confirm_id, host):
    if action != 'confirm':
        reply_invalid_confirm(message, list, host, action)
    else:
        body = view("unsubscribed.msg").render(list=list)
        relay.reply(message, list + "-noreply@" + host, 
                         "You are now unsubscribed from %s" % list, body)
        return KNOWN


def END(session, message, *args):
    return KNOWN

def ERROR(exc, state):
    return state


def reply_invalid_confirm(message, list, host, action):
     body = view("confirm_expected.msg").render(
        list=list, host=host, action=action, request_type="unsubscribe")
     relay.reply(message, list + "-noreply@" + host, "Confirmation reply expected" % action, body)



