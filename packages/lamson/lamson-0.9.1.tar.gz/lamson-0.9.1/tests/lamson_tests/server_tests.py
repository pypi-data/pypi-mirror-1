# Copyright (C) 2008 Zed A. Shaw.  Licensed under the terms of the GPLv3.

from nose.tools import *
import os
from lamson import server, queue, routing
from message_tests import *
import re
from sqlalchemy import MetaData


def test_router():
    routing.Router.deliver(test_mail_request())

    # test that fallthrough works too
    msg = test_mail_request()
    msg['to'] = 'unhandled@unhandled.com'
    msg.To = msg['to']

    routing.Router.deliver(msg)

def test_receiver():
    receiver = server.SMTPReceiver(host="localhost", port=8824)
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
    relay = server.Relay("localhost", port=8899)
    print "Relay: %r" % relay

    relay.deliver(test_mail_response_plain_text())
    relay.deliver(test_mail_response_html())
    relay.deliver(test_mail_response_html_and_plain_text())
    relay.deliver(test_mail_response_attachments())

def test_relay_reply():
    relay = server.Relay("localhost", port=8899)
    print "Relay: %r" % relay

    relay.reply(test_mail_request(), 'from@test.com', 'Test subject', 'Body')


def test_queue_reciever():
    receiver = server.QueueReceiver('run/queue')
    run_queue = queue.Queue('run/queue')
    run_queue.push(test_mail_response_plain_text().as_string())
    assert run_queue.count() > 0
    receiver.start(one_shot=True)
    assert run_queue.count() == 0


