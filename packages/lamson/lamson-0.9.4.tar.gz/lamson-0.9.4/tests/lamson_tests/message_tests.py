# Copyright (C) 2008 Zed A. Shaw.  Licensed under the terms of the GPLv3.

from nose.tools import *
import re
import os
from lamson import mail
import email

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


    # test the accessor parts of the base class that we proxy to
    assert_equal(msg.matches(re.compile("^(.*)@^(.*)")), None)
    assert_equal(msg.msg['From'], "zedshaw@zedshaw.com")

    assert("From" in msg)
    del msg["From"]
    assert("From" not in msg)

    msg["From"] = "nobody@nowhere.com"
    assert("From" in msg)
    assert_equal(msg["From"], "nobody@nowhere.com")

    # validate that upper and lower case work for headers
    assert("FroM" in msg)
    assert("from" in msg)
    assert("From" in msg)
    assert_equal(msg['From'], msg['fRom'])
    assert_equal(msg['From'], msg['from'])
    assert_equal(msg['from'], msg['fRom'])

    # make sure repr runs
    print repr(msg)

    return msg

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
    data = str(sample)

    msg = mail.MailRequest("localhost", None, None, data)

    msg_parts = msg.all_parts()
    sample_parts = sample.all_parts()

    readme = open("./README").read()

    # BUG: Python's MIME text attachment decoding drops trailing newline chars

    assert msg_parts[0].body == sample_parts[0].body
    # python drops chars at the end, so can't compare equally
    assert readme.startswith(msg_parts[1].body)
    assert msg.body() == sample_parts[0].body

    # test that we get at least one message for messages without attachments
    sample = test_mail_response_plain_text()
    msg = mail.MailRequest("localhost", None, None, str(sample))
    msg_parts = msg.all_parts()
    assert len(msg_parts) == 0, "Length is %d should be 0." % len(msg_parts)
    assert msg.body()


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

def test_mail_response_ignore_case_headers():
    msg = test_mail_response_plain_text()
    # validate that upper and lower case work for headers
    assert("FroM" in msg)
    assert("from" in msg)
    assert("From" in msg)
    assert_equal(msg['From'], msg['fRom'])
    assert_equal(msg['From'], msg['from'])
    assert_equal(msg['from'], msg['fRom'])
