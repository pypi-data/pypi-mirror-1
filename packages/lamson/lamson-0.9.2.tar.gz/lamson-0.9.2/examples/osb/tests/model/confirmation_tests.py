from nose.tools import *
from lamson.testing import *
from lamson.mail import MailRequest, MailResponse
import os
import time
import shutil
from app.model import confirmation

user = "test_user@test.com"
blog = "test_blog"
blog_address = "%s@osb.test.com" % blog

def craft_fake_message(to_address):
    sample = MailResponse(From=user, To=to_address, 
                           Subject="Test subject", Body="Fake body")
    return MailRequest("fakepeer", sample['From'], sample['To'], str(sample))

def test_push_get():
    message = craft_fake_message(blog_address)

    pending_id = confirmation.push(message)

    assert pending_id, "No message queue ID returned."

    msg = confirmation.get(pending_id)
    assert msg['Subject'] == message['Subject']


def test_register_verify():
    message = craft_fake_message(blog_address)
    pending_id = confirmation.push(message)
    confirm_address = confirmation.register(message, blog, "osb.test.com", pending_id)

    assert confirm_address, "Didn't get a confirmation address."
    confirm = craft_fake_message(confirm_address)

    confirm_address = confirm_address.split('@')[0]
    expect_blog, junk, expect_id = confirm_address.split('-')

    assert confirmation.verify(message, expect_blog, expect_id)



