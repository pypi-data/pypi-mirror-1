from nose.tools import *
import os
from lamson import fsm, server
from mail_tests.utils import session

def test_event():
    simple = fsm.FSMModule("mail_tests.simple_fsm_mod", "test@test.com", "test@test.com", {"var1": 1, "var2": 2})
    simple.load_state(session)

    assert simple.state == simple.fsm.TEST

    simple.event(10)
    assert simple.state == simple.fsm.NEXT

    simple.event(20)
    assert simple.state == simple.fsm.END

    simple.event(30)
    assert simple.is_finished()


def test_error():
    simple = fsm.FSMModule("mail_tests.simple_fsm_mod", "test@test.com", "test@test.com", {"var1": 1, "var2": 2})
    simple.load_state(session)
    assert simple.state == simple.fsm.TEST
    simple.event("error")
    assert simple.is_finished()


def test_reset():
    simple = fsm.FSMModule("mail_tests.simple_fsm_mod", "test@test.com", "test@test.com", {"var1": 1, "var2": 2})
    simple.load_state(session)
    assert simple.state == simple.fsm.TEST

    simple.event("reset")
    assert simple.is_finished()

    simple.reset()
    assert not simple.is_finished()

    simple.event("again")
    simple.event(10)
    simple.event(20)
    assert simple.is_finished()



