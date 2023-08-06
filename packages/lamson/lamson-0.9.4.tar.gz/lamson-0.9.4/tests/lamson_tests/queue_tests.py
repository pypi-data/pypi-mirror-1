from lamson import queue, server, mail
from nose.tools import *


def test_push():
    q = queue.Queue("run/queue")
    q.clear()

    # the queue doesn't really care if its a request or response, as long
    # as the object answers to str(msg)
    msg = mail.MailResponse(To="test@test.com", From="test@test.com",
                              Subject="Test", Body="Test")
    key = q.push(msg)
    assert key, "Didn't get a key for test_get push."

    return q


def test_pop():
    q = test_push()
    key, msg = q.pop()

    assert key, "Didn't get a key for test_get push."
    assert msg, "Didn't get a message for key %r" % key

    assert msg['to'] == "test@test.com"
    assert msg['from'] == "test@test.com"
    assert msg['subject'] == "Test"
    assert msg.body() == "Test"

    assert q.count() == 0, "Queue should be empty."
    assert not q.pop()[0]


def test_get():
    q = test_push()
    msg = mail.MailResponse(To="test@test.com", From="test@test.com",
                              Subject="Test", Body="Test")
    key = q.push(msg.as_string()) 
    assert key, "Didn't get a key for test_get push."

    msg = q.get(key)
    assert msg, "Didn't get a message for key %r" % key

def test_remove():
    q = test_push()
    msg = mail.MailResponse(To="test@test.com", From="test@test.com",
                              Subject="Test", Body="Test")
    key = q.push(msg.as_string())
    assert key, "Didn't get a key for test_get push."
    assert q.count() == 2, "Wrong count %d should be 2" % q.count()

    q.remove(key)
    assert q.count() == 1, "Wrong count %d should be 1" % q.count()

