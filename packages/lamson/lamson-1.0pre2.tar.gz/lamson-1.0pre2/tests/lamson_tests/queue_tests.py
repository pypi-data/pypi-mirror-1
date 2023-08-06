from lamson import queue, server, mail
from nose.tools import *

USE_SAFE=False

def test_push():
    q = queue.Queue("run/queue", safe=USE_SAFE)
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
    key = q.push(str(msg))
    assert key, "Didn't get a key for test_get push."

    msg = q.get(key)
    assert msg, "Didn't get a message for key %r" % key

def test_remove():
    q = test_push()
    msg = mail.MailResponse(To="test@test.com", From="test@test.com",
                              Subject="Test", Body="Test")
    key = q.push(str(msg))
    assert key, "Didn't get a key for test_get push."
    assert q.count() == 2, "Wrong count %d should be 2" % q.count()

    q.remove(key)
    assert q.count() == 1, "Wrong count %d should be 1" % q.count()



def test_safe_maildir():
    global USE_SAFE
    USE_SAFE=True
    test_push()
    test_pop()
    test_get()
    test_remove()


def test_oversize_protections():
    # first just make an oversize limited queue
    overq = queue.Queue("run/queue", pop_limit=10)
    overq.clear()

    for i in range(5):
        overq.push("HELLO" * 100)

    assert_equal(overq.count(), 5)

    key, msg = overq.pop()

    assert not key and not msg, "Should get no messages."
    assert_equal(overq.count(), 0)

    # now make sure that oversize mail is moved to the overq
    overq = queue.Queue("run/queue", pop_limit=10, oversize_dir="run/big_queue")
    moveq = queue.Queue("run/big_queue")

    for i in range(5):
        overq.push("HELLO" * 100)

    key, msg = overq.pop()

    assert not key and not msg, "Should get no messages."
    assert_equal(overq.count(), 0)
    assert_equal(moveq.count(), 5)

    moveq.clear()
    overq.clear()
