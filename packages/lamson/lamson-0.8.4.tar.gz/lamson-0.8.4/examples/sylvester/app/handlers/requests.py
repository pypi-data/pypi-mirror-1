import logging
from lamson import fsm, server, queue
from config import settings


def START():
    return NEW_USER


def NEW_USER(session, message, list, host):
    return NEW_USER

def END(session, message, *args):
    # just rebounce to NEW_USER to bring them back
    return NEW_USER(session, message, *args)

def ERROR(ext, state):
    return state

