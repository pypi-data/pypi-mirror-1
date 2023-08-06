# Copyright (C) 2008 Zed A. Shaw.  Licensed under the terms of the GPLv3.

from nose.tools import *
import re
import os
from lamson import mail

sample_message = """From: zedshaw@zedshaw.com
To: zedshaw@zedshaw.com

Test
"""

def test_mail_request():
    # try with a half-assed message
    msg = mail.MailRequest("zedshaw.com", "zedfrom@zedshaw.com",
                           "zedto@zedshaw.com", "Fake body.")
    assert msg['to'] == "zedto@zedshaw.com", "To is %r" % msg['to']
    assert msg['from'] == "zedfrom@zedshaw.com", "From is %r" % msg['from']

    msg = mail.MailRequest("zedshaw.com", "zedshaw@zedshaw.com",
                             ["zedshaw@zedshaw.com"], sample_message)

    assert_equal(str(msg), msg.Data, "Message isn't valid.")

    # test the accessor parts of the base class that we proxy to
    assert_equal(msg.matches(re.compile("^(.*)@^(.*)")), None)
    assert_equal(msg.msg['From'], "zedshaw@zedshaw.com")
    assert("From" in msg)
    del msg["From"]
    assert("From" not in msg)
    msg["From"] = "nobody@nowhere.com"
    assert("From" in msg)
    assert_equal(msg["From"], "nobody@nowhere.com")

    print repr(msg)

    return msg

def test_character_encoded_header():
    msg = mail.MailRequest("zedshaw.com", "zedshaw@zedshaw.com",
                             ["zedshaw@zedshaw.com"], sample_message)
    msg['Subject'] = '=?iso-8859-1?q?p=F6stal?='
    assert msg['Subject'] == u'p\xf6stal', "%r" % msg['Subject']

    msg = mail.MailRequest("zedshaw.com", "zedshaw@zedshaw.com",
                             ["zedshaw@zedshaw.com"], sample_message)
    msg.encode_header('Subject', u'p\xf6stal', 'iso-8859-1')

    assert msg['Subject'] == u'p\xf6stal', "%r" % msg['Subject']

    
    sample = test_mail_response_plain_text()
    sample.encode_header('Subject', u'p\xf6stal', 'iso-8859-1')

    assert sample['Subject'] ==  '=?iso-8859-1?q?p=F6stal?=', "%r" % sample['Subject']


def test_mail_response_plain_text():
    sample = mail.MailResponse(To="receiver@zedshaw.com", 
                                 Subject="Test message",
                                 From="sender@zedshaw.com",
                                 Body="Test from test_mail_response_plain_text.")
    return sample

def test_mail_response_html():
    sample = mail.MailResponse(To="receiver@zedshaw.com", 
                                 Subject="Test message",
                                 From="sender@zedshaw.com",
                                 Html="<html><body><p>From test_mail_response_html</p></body></html>")
    return sample

def test_mail_response_html_and_plain_text():
    sample = mail.MailResponse(To="receiver@zedshaw.com", 
                                 Subject="Test message",
                                 From="sender@zedshaw.com",
                                 Html="<html><body><p>Hi there.</p></body></html>",
                                 Body="Test from test_mail_response_html_and_plain_text.")
    return sample

def test_mail_response_attachments():
    sample = mail.MailResponse(To="receiver@zedshaw.com", 
                                 Subject="Test message",
                                 From="sender@zedshaw.com",
                                 Body="Test from test_mail_response_attachments.")
    sample.attach("./README")
    return sample

def test_mail_request_attachments():
    sample = test_mail_response_attachments()
    msg = mail.MailRequest("localhost", None, None, str(sample))
    all = msg.all_parts()
    readme = open("./README").read()
    assert all[0].get_payload() == sample.Body
    assert all[1].get_payload(decode=True) == readme
    assert msg.body() == sample.Body
    assert msg.body(0) == sample.Body
    assert msg.body(1) == readme

    # test that we get at least one message for messages without attachments
    sample = test_mail_response_plain_text()
    msg = mail.MailRequest("localhost", None, None, str(sample))
    all = msg.all_parts()
    assert len(all) == 1, "Length is %d should be 1." % len(all)
    assert all[0].get_payload() == sample.Body
    assert msg.body() == sample.Body


def test_mail_response_mailing_list_headers():
    list_addr = "test.users@test.com"

    msg = mail.MailResponse(From='zedshaw@zedshaw.com', To=list_addr, 
            Subject='subject', Body="Mailing list reply.")

    print repr(msg)

    msg["Sender"] = list_addr
    msg["Reply-To"] = list_addr
    msg["List-Id"] = list_addr
    msg["Return-Path"] = list_addr
    msg["In-Reply-To"] = 'Message-Id-1231123'
    msg["References"] = 'Message-Id-838845854'
    msg["Precedence"] = 'list'

    data = msg.as_string()

    req = mail.MailRequest('localhost', 'zedshaw@zedshaw.com', list_addr, data)

    headers = ['Sender', 'Reply-To', 'List-Id', 'Return-Path', 
               'In-Reply-To', 'References', 'Precedence']
    for header in headers:
        assert msg[header] == req[header]

    # try a delete
    del msg['Precedence']

