import logging
from lamson import fsm, server, queue
from config import settings
from sqlalchemy import and_
from app.handlers import delivery


def START():
    return NEW_USER


def NEW_USER(session, message, list, host):
    body = view("you_need_to_subscribe.msg").render(list=list, host=host)
    relay.reply(message, list + "-subscribe@" + host, "You are unknown to me sir!", body)

    return NEW_USER


def POSTING(session, message, list, host):
    # Leave it to the delivery handler for later 
    delivery.deliver_to_members(session, relay, message, list, host)


def PAUSED(session, message, *args):
    body = view("you_are_paused.msg").render(list=list, host=host)

    relay.reply(message, list + "-resume@" + host, "You are paused, and you are not doing it right.", body)

    return PAUSED


def END(session, message, *args):
    # just rebounce to NEW_USER to bring them back
    return NEW_USER(session, message, *args)

def UNSUBSCRIBED(session, message, *args):
    # just punt to the new user, but will want to do this nicer
    return NEW_USER(session, message, *args)

def ERROR(ext, state):
    return state

