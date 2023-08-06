from nose.tools import *
from lamson.testing import *
import os
from lamson import server

relay = relay(port=8823)
client = RouterConversation("zedshaw@zedshaw.com", "requests_tests")
confirm_format = "testing-confirm-[0-9]+@"
noreply_format = "testing-noreply@"


def test_forwards_relay_host():
    """
    Makes sure that your config/settings.py is configured to forward mail from
    test.com (or your direct host) to your relay.
    """
    client.begin()
    client.say("tester@test.com", "Test that forward works.", "tester@test.com")


def test_drops_open_relay_messages():
    """
    But, make sure that mail NOT for test.com gets dropped silently.
    """
    client.begin()
    client.say("tester@donotrelay.com", "Relay should not happen")
    assert queue().count() == 0, "Should not deliver that message."
