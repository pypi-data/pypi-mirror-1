from nose.tools import *
from lamson.testing import *
from lamson.mail import MailRequest, MailResponse
from app.model import confirmation
from mock import patch

user = "test_user@test.com"
blog = "test_blog"
blog_address = "%s@oneshotblog.com" % blog


def craft_fake_message(to_address):
    sample = MailResponse(From=user, To=to_address, 
                           Subject="Test subject", Body="Fake body")
    return MailRequest("fakepeer", sample['From'], sample['To'], str(sample))

def test_push_get():
    confirmation.clear()
    message = craft_fake_message(blog_address)

    pending_id = confirmation.push(message)

    assert pending_id, "No message queue ID returned."

    msg = confirmation.get(pending_id)
    assert msg['Subject'] == message['Subject']


def test_register_verify():
    confirmation.clear()
    message = craft_fake_message(blog_address)
    confirm_address = confirmation.register("post", message)

    assert confirm_address, "Didn't get a confirmation address."
    confirm = craft_fake_message(confirm_address)

    target, junk, expect_id = confirm_address.split('-')

    assert confirmation.verify(message, expect_id)

def test_verify_with_bogus_id():
    confirmation.clear()
    message = craft_fake_message(blog_address)
    confirm_address = confirmation.register("post", message)
    assert confirm_address
    assert not confirmation.verify(message, "totallybogusid")

def test_verify_with_unknown_address():
    confirmation.clear()
    message = craft_fake_message(blog_address)
    assert not confirmation.verify(message, "totallybogusid")

@patch('lamson.server.Relay')
def test_send(RelayMock):
    confirmation.clear()
    rm = RelayMock()
    
    msg = craft_fake_message(blog_address)
    confirmation.send(relay(), "post", msg, "mail/confirm.msg", locals())
    assert rm.deliver.called, "Confirmation not delivered."

