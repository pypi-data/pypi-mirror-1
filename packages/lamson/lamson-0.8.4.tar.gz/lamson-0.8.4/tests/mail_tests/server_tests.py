# Copyright (C) 2008 Zed A. Shaw.  Licensed under the terms of the GPLv3.

from nose.tools import *
import os
from lamson import server, handlers
import re
from sqlalchemy import MetaData

sample_message = """From: zedshaw@zedshaw.com
To: zedshaw@zedshaw.com

Test
"""

def test_mail_request():
    msg = server.MailRequest("zedshaw.com", "zedshaw@zedshaw.com",
                             ["zedshaw@zedshaw.com"], sample_message)

    assert_equal(str(msg), msg.Data, "Message isn't valid.")

    assert_equal(msg.all_recipients(), [('', 'zedshaw@zedshaw.com'), 
                                        ('', 'zedshaw@zedshaw.com')])

    # test the accessor parts of the base class that we proxy to
    assert_equal(msg.matches(re.compile("^(.*)@^(.*)")), None)
    assert_equal(msg.msg['From'], "zedshaw@zedshaw.com")
    assert("From" in msg)
    del msg["From"]
    assert("From" not in msg)
    msg["From"] = "nobody@nowhere.com"
    assert("From" in msg)
    assert_equal(msg["From"], "nobody@nowhere.com")

    return msg


def test_log_handler():
    logger = handlers.LogHandler()
    logger.process(None, test_mail_request(), ["zedshaw@zedshaw.com"])
    return logger

def test_router():
    routes = [
        ("^(.*)@(.*)$", test_log_handler())
    ]
    router = server.Router(routes, None, test_database(),
                        directories=['./tests/mail_tests'],
                        module_directory='/tmp/lamson_templates')
    router.deliver(test_mail_request())
    return router

def test_receiver():
    router = test_router()
    receiver = server.SMTPReceiver({"host" : "localhost", "port" : 8824}, router)
    msg = test_mail_request()
    receiver.process_message(msg.Peer, msg.From, msg.To, msg.Data)

def test_database():
    metadata = MetaData()
    url = 'sqlite:///tests/test.db'
    db = server.Database(metadata, url)
    db.configure()
    db.create()

    session = db.session()
    assert session, "SQLA session wasn't created."

    return db


def test_relay_deliver():
    relay = server.Relay("localhost", port=8825)

    relay.deliver(test_mail_response_plain_text())
    relay.deliver(test_mail_response_html())
    relay.deliver(test_mail_response_html_and_plain_text())
    relay.deliver(test_mail_response_attachments())


def test_mail_response_plain_text():
    sample = server.MailResponse(To="receiver@zedshaw.com", 
                                 Subject="Test message",
                                 From="sender@zedshaw.com",
                                 Body="Test from test_mail_response_plain_text.")
    return sample

def test_mail_response_html():
    sample = server.MailResponse(To="receiver@zedshaw.com", 
                                 Subject="Test message",
                                 From="sender@zedshaw.com",
                                 Html="<html><body><p>From test_mail_response_html</p></body></html>")
    return sample

def test_mail_response_html_and_plain_text():
    sample = server.MailResponse(To="receiver@zedshaw.com", 
                                 Subject="Test message",
                                 From="sender@zedshaw.com",
                                 Html="<html><body><p>Hi there.</p></body></html>",
                                 Body="Test from test_mail_response_html_and_plain_text.")
    return sample

def test_mail_response_attachments():
    sample = server.MailResponse(To="receiver@zedshaw.com", 
                                 Subject="Test message",
                                 From="sender@zedshaw.com",
                                 Body="Test from test_mail_response_attachments.")
    sample.attach("./README")
    return sample


def test_mail_response_mailing_list_headers():
    list_addr = "test.users@test.com"

    msg = server.MailResponse(From='zedshaw@zedshaw.com', To=list_addr, 
            Subject='subject', Body="Mailing list reply.")

    msg["Sender"] = list_addr
    msg["Reply-To"] = list_addr
    msg["List-Id"] = list_addr
    msg["Return-Path"] = list_addr
    msg["In-Reply-To"] = 'Message-Id-1231123'
    msg["References"] = 'Message-Id-838845854'
    msg["Precedence"] = 'list'

    data = msg.as_string()

    req = server.MailRequest('localhost', 'zedshaw@zedshaw.com', list_addr, data)

    headers = ['Sender', 'Reply-To', 'List-Id', 'Return-Path', 
               'In-Reply-To', 'References', 'Precedence']
    for header in headers:
        assert msg[header] == req[header]

