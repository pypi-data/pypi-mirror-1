from lamson import server
from nose.tools import *
from lamson.testing import *

relay = relay(port=8825)

def test_clear_queue():
    queue().push("Test")
    assert queue().count() > 0

    clear_queue()
    assert queue().count() == 0


def test_relay():
    clear_queue()
    relay.send('test@test.com', 'zedshaw@zedshaw.com', 'Test message', 'Test body')
    assert queue().keys()

def test_delivered():
    clear_queue()
    relay.send("zedshaw@zedshaw.com", "tester@tester.com", Subject="Test subject.", Body="Test body.")
    assert delivered("zedshaw@zedshaw.com"), "Test message not delivered."
    assert delivered("zedshaw@zedshaw.com"), "Test message not delivered."
    assert not delivered("badman@test.com")

