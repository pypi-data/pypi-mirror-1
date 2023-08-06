from nose.tools import *
from lamson import spam
from lamson_tests.message_tests import *
from lamson.routing import Router
import os

ham_db = "tests/sddb"

def setup():
    Router.clear_states()
    Router.clear_routes()
    if os.path.exists(ham_db):
        os.unlink(ham_db)


def teardown():
    setup()


def test_Filter():
    sf = spam.Filter(ham_db, 'tests/.hammierc')
    ham_msg = test_mail_request().msg
    spam_msg = test_mail_response_plain_text().as_message()

    sf.train_ham(ham_msg)
    sf.train_spam(spam_msg)

    sf.untrain_ham(test_mail_request().msg)
    sf.untrain_spam(spam_msg)

    sf.close()

def test_spam_filter():
    import spam_filtered_mod

    sf = spam.Filter(ham_db, 'tests/.hammierc')
    msg = test_mail_request()
    sf.train_spam(msg.msg)

    Router.deliver(msg)
    assert Router.in_state(spam_filtered_mod.START, msg), "Spam got through"

    print Router.STATE_STORE.states
    print Router.REGISTERED
    sf.untrain_spam(msg.msg)
    sf.train_ham(msg.msg)

    Router.deliver(msg)
    assert Router.in_state(spam_filtered_mod.END, msg), "Ham didn't go through."

