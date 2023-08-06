from nose.tools import *
from lamson.routing import *


def setup():
    Router.clear_states()
    Router.clear_routes()

def teardown():
    setup()

def test_MemoryStorage():
    store = MemoryStorage()
    store.set(test_MemoryStorage.__module__, "tester@test.com", "TESTED")

    assert store.get(test_MemoryStorage.__module__, "tester@test.com") == "TESTED"

    assert store.get(test_MemoryStorage.__module__, "tester2@test.com") == "START"

    store.clear()

    assert store.get(test_MemoryStorage.__module__, "tester@test.com") == "START"

def test_ShelveStorage():
    store = ShelveStorage("tests/statesdb")

    store.set(test_ShelveStorage.__module__, "tester@test.com", "TESTED")
    assert store.get(test_MemoryStorage.__module__, "tester@test.com") == "TESTED"

    assert store.get(test_MemoryStorage.__module__, "tester2@test.com") == "START"

    store.clear()
    assert store.get(test_MemoryStorage.__module__, "tester@test.com") == "START"


def test_RoutingBase():
    assert len(Router.ORDER) == 0
    assert len(Router.REGISTERED) == 0

    Router.load(['lamson_tests.simple_fsm_mod'])
    import simple_fsm_mod

    assert len(Router.ORDER) > 0
    assert len(Router.REGISTERED) > 0

    message = {'to': 'users-subscribe@test.com', 'from': 'zedshaw@zedshaw.com'}
    Router.deliver(message)
    assert Router.in_state(simple_fsm_mod.CONFIRM, message)

    confirm = {'to': 'users-confirm-1@test.com', 'from': 'zedshaw@zedshaw.com'}
    Router.deliver(confirm)
    assert Router.in_state(simple_fsm_mod.POSTING, message)

    Router.deliver(message)
    assert Router.in_state(simple_fsm_mod.NEXT, message)

    Router.deliver(message)
    assert Router.in_state(simple_fsm_mod.START, message)

    Router.clear_states()
    explosion = {'to': 'start-explode@test.com', 'from': 'hacker@hacker.com'}
    Router.deliver(explosion)

    assert Router.in_error(simple_fsm_mod.END, explosion)

    Router.reload()
    assert 'lamson_tests.simple_fsm_mod' in Router.HANDLERS
    assert len(Router.ORDER)
    assert len(Router.REGISTERED)


