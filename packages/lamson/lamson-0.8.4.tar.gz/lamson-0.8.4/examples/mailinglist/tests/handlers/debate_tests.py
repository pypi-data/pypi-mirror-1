
from nose.tools import *
from lamson.testing import *
import os
from lamson import server, handlers, fsm, queue

relay = relay(port=8823)
client = TestConversation(relay, "zedshaw@zedshaw.com", "debate_tests")
confirm_format = "testing-confirm-[0-9]+@test.com"
noreply_format = "testing-noreply@test.com"

def test_user_initially_joins():
    client.begin()

    client.say("testing@test.com", "Unknown user", "testing-subscribe@test.com")

    msg = client.say("testing-subscribe@test.com", "Subscribe after unknown", confirm_format)

    client.say(msg['from'], "Confirmation message.", noreply_format)


def test_known_user_posts():
    test_user_initially_joins()
    client.say("testing@test.com", "Known user posting", "testing@test.com")


def test_known_user_pauses_then_posts():
    test_user_initially_joins()

    msg = client.say("testing-pause@test.com", "Pause testing", confirm_format)

    client.say(msg['from'], "Pause confirm", noreply_format)

    client.say("testing@test.com", "Paused user posting", "testing-resume@test.com")

