# Copyright (C) 2008 Zed A. Shaw.  Licensed under the terms of the GPLv3.

from nose.tools import *
import os
from lamson import server, handlers, fsm
from mail_tests.utils import session
import re
import datetime
from sqlalchemy import MetaData, Table, Column, String, Integer, DateTime, Boolean
from sqlalchemy.orm import mapper

sample_message = """From: testcase@zedshaw.com
To: zedshaw@zedshaw.com

Test
"""

def test_conversation_storage():
    convo = handlers.Conversation("mail_tests.stored_fsm")
     
    msg = server.MailRequest("zedshaw.com", "zedshaw@zedshaw.com",
                             ["zedshaw@zedshaw.com"], sample_message)

    states = session.query(fsm.FSMState).all()
    for s in states: session.delete(s)
    session.flush()

    convo.process(session, msg, [("zedshaw","zedshaw.com")])
    states = session.query(fsm.FSMState).all()
    assert len(states) > 0, "There should be some states, now there's %d." % len(states)


    convo.process(session, msg, [("zedshaw","zedshaw.com")])
    convo.process(session, msg, [("zedshaw","zedshaw.com")])

