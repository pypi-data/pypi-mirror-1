
from nose.tools import *
from lamson.testing import *
import os
from lamson import server, handlers, fsm

relay = relay(port=8823)
client = TestConversation(relay, "zedshaw@zedshaw.com", "requests_tests")
confirm_format = "testing-confirm-[0-9]+@"
noreply_format = "testing-noreply@"


def test_forwards_relay_host():
    client.begin()
    client.say("tester@test.com", "Test that forward works.", "tester@test.com")


def test_drops_open_relay_messages():
    client.begin()
    client.say("tester@donotrelay.com", "Relay should not happen")
    assert queue().count() == 0, "Should not deliver that message."
