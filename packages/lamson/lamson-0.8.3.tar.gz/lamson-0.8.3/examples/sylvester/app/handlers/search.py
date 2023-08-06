import logging
from lamson import fsm, server, queue
from sqlalchemy import and_
from config import settings


def START(): return DELIVERING


def DELIVERING(session, message, list, host):
    return DELIVERING

def END(session, message, *args):
    return END

def ERROR(ext, state):
    return state

