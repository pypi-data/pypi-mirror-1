from lamson import server
from lamson.routing import Router
from lamson.testing import *
from nose.tools import *
import os

relay = relay(port=8899)

def setup():
    Router.clear_routes()
    Router.clear_states()
    Router.load(['lamson_tests.simple_fsm_mod'])


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

def test_RouterConversation():
    client = RouterConversation('tester@test.com', 'Test router conversations.')
    client.begin()
    client.say('testlist@test.com', 'This is a test')

def test_spelling():
    # specific to a mac setup, because macs are lame
    if 'PYENCHANT_LIBRARY_PATH' not in os.environ:
        os.environ['PYENCHANT_LIBRARY_PATH'] = '/opt/local/lib/libenchant.dylib'

    template = "tests/lamson_tests/template.txt"
    contents = open(template).read()
    assert spelling(template, contents) 
