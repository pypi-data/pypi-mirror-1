from nose.tools import *
from lamson.testing import *
from lamson.mail import MailRequest, MailResponse
from app.model import confirmation
from mock import patch

user = "test_user@test.com"
list_name = "test_list_name"
list_name_address = "%s@oneshotlist_name.com" % list_name

def setup():
    confirmation.clear()


def craft_fake_message(to_address):
    sample = MailResponse(From=user, To=to_address, 
                           Subject="Test subject", Body="Fake body")
    return MailRequest("fakepeer", sample['From'], sample['To'], str(sample))

def test_push_get():
    message = craft_fake_message(list_name_address)

    pending_id = confirmation.push(message)

    assert pending_id, "No message queue ID returned."

    msg = confirmation.get(pending_id)
    assert msg['Subject'] == message['Subject']


def test_register_verify():
    message = craft_fake_message(list_name_address)
    confirm_address = confirmation.register("post", message)

    assert confirm_address, "Didn't get a confirmation address."
    confirm = craft_fake_message(confirm_address)

    target, junk, expect_id = confirm_address.split('-')

    assert confirmation.verify(target, message, expect_id)

def test_verify_with_bogus_id():
    message = craft_fake_message(list_name_address)
    confirm_address = confirmation.register("post", message)
    assert confirm_address
    assert not confirmation.verify(list_name, message, "totallybogusid")

def test_verify_with_unknown_address():
    message = craft_fake_message(list_name_address)
    assert not confirmation.verify(list_name, message, "totallybogusid")

@patch('lamson.server.Relay')
def test_send(RelayMock):
    rm = RelayMock()
    host='librelist.com'
    
    msg = craft_fake_message(list_name_address)
    confirmation.send(relay(), "post", msg, "mail/confirmation.msg", locals())
    assert rm.deliver.called, "Confirmation not delivered."

