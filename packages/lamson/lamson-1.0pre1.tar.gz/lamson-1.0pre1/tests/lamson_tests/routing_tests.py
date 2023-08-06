from nose.tools import *
from lamson.routing import *
from lamson.mail import MailRequest


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

    message = MailRequest('fakepeer', 'zedshaw@zedshaw.com', 'users-subscribe@test.com', "")
    Router.deliver(message)
    assert Router.in_state(simple_fsm_mod.CONFIRM, message)

    confirm = MailRequest('fakepeer', 'zedshaw@zedshaw.com',  'users-confirm-1@test.com', "")
    Router.deliver(confirm)
    assert Router.in_state(simple_fsm_mod.POSTING, message)

    Router.deliver(message)
    assert Router.in_state(simple_fsm_mod.NEXT, message)

    Router.deliver(message)
    assert Router.in_state(simple_fsm_mod.END, message)

    Router.deliver(message)
    assert Router.in_state(simple_fsm_mod.START, message)

    Router.clear_states()
    explosion = MailRequest('fakepeer',  'hacker@hacker.com',   'start-explode@test.com', "")
    Router.LOG_EXCEPTIONS=True
    Router.deliver(explosion)

    assert Router.in_error(simple_fsm_mod.END, explosion)

    Router.clear_states()
    Router.LOG_EXCEPTIONS=False
    explosion = MailRequest('fakepeer',  'hacker@hacker.com',   'start-explode@test.com', "")
    assert_raises(RuntimeError, Router.deliver, explosion)

    Router.reload()
    assert 'lamson_tests.simple_fsm_mod' in Router.HANDLERS
    assert len(Router.ORDER)
    assert len(Router.REGISTERED)


@raises(NotImplementedError)
def test_StateStorage_get_raises():
    s = StateStorage()
    s.get("raises", "raises")

@raises(NotImplementedError)
def test_StateStorage_set_raises():
    s = StateStorage()
    s.set("raises", "raises", "raises")

@raises(NotImplementedError)
def test_StateStorage_clear_raises():
    s = StateStorage()
    s.clear()

@raises(TypeError)
def test_route___get___raises():
    class BadRoute(object):

        @route("test")
        def wont_work(message, **kw):
            pass

    br = BadRoute()
    br.wont_work("raises")

