from nose.tools import *
from lamson.testing import *
import os
from lamson import server, handlers, fsm, utils

relay = relay(port=8823)
client = TestConversation(relay, "zedshaw@zedshaw.com", "admin_tests")
confirm_format = "testing-confirm-[0-9]+@test.com"
noreply_format = "testing-noreply@test.com"


def test_user_initially_joins():
    client.begin()

    client.say("testing@test.com", "Unknown user", "testing-subscribe@test.com")

    msg = client.say("testing-subscribe@test.com", "Subscribe after unknown", confirm_format)

    client.say(msg['from'], "Confirmation message.", noreply_format)


def test_known_user_subscribes():
    test_user_initially_joins()  # should be part of testing now

    msg = client.say("known-subscribe@test.com", "Subscribing to known-subscribe", 
                    "known-confirm-[0-9]+@test.com")

    client.say(msg['from'], "Subscribe confirm.", "known-noreply@test.com")


def test_known_user_unsubscribes():
    test_user_initially_joins()

    msg = client.say("testing-unsubscribe@test.com", "Unsubscribe testing", confirm_format)
    
    client.say(msg['from'], "Unsubscribe confirm.", noreply_format)


def test_known_user_pauses():
    test_user_initially_joins()

    msg = client.say("testing-pause@test.com", "Pause testing", confirm_format)

    client.say(msg['from'], "Pause confirm", noreply_format)


def test_known_user_resumes_after_pausing():
    test_known_user_pauses()

    msg = client.say("testing-resume@test.com", "Resume testing", confirm_format)
    client.say(msg['from'], "Resume confirm", noreply_format)

def test_known_user_posts():
    test_user_initially_joins()
    client.say("testing@test.com", "Posting", "testing@test.com")

def test_known_user_posts_when_not_subscribed():
    test_user_initially_joins()
    client.say("notsubscribed@test.com", "No subscribed", "notsubscribed-subscribe@test.com")


