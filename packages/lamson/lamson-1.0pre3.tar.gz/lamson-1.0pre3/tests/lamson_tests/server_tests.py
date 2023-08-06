# Copyright (C) 2008 Zed A. Shaw.  Licensed under the terms of the GPLv3.

from nose.tools import *
from mock import *
import os
from lamson import server, queue, routing
from message_tests import *
import re


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
    receiver.process_message(msg.Peer, msg.From, msg.To, str(msg))


def test_relay_deliver():
    relay = server.Relay("localhost", port=8899)

    relay.deliver(test_mail_response_plain_text())
    relay.deliver(test_mail_response_html())
    relay.deliver(test_mail_response_html_and_plain_text())
    relay.deliver(test_mail_response_attachments())

@patch('DNS.mxlookup')
def test_relay_deliver_mx_hosts(DNS_mxlookup):
    DNS_mxlookup.return_value = [[100, "localhost"]]
    relay = server.Relay(None, port=8899)

    msg = test_mail_response_plain_text()
    msg['to'] = 'zedshaw@localhost'
    relay.deliver(msg)
    assert DNS_mxlookup.called

@patch('DNS.mxlookup')
def test_relay_resolve_relay_host(DNS_mxlookup):
    DNS_mxlookup.return_value = []
    relay = server.Relay(None, port=8899)
    host = relay.resolve_relay_host('zedshaw@localhost')
    assert_equal(host, 'localhost')
    assert DNS_mxlookup.called

    DNS_mxlookup.reset_mock()
    DNS_mxlookup.return_value = [[100, "mail.zedshaw.com"]]
    host = relay.resolve_relay_host('zedshaw@zedshaw.com')
    assert_equal(host, 'mail.zedshaw.com')
    assert DNS_mxlookup.called

def test_relay_reply():
    relay = server.Relay("localhost", port=8899)
    print "Relay: %r" % relay

    relay.reply(test_mail_request(), 'from@test.com', 'Test subject', 'Body')

def raises_exception(*x, **kw):
    raise RuntimeError("Raised on purpose.")


@patch('lamson.routing.Router', new=Mock())
def test_queue_receiver():
    receiver = server.QueueReceiver('run/queue')
    run_queue = queue.Queue('run/queue')
    run_queue.push(str(test_mail_response_plain_text()))
    assert run_queue.count() > 0
    receiver.start(one_shot=True)
    assert run_queue.count() == 0

    routing.Router.deliver.side_effect = raises_exception
    receiver.process_message(mail.MailRequest('localhost', 'test@test.com',
                                              'test@test.com', 'Fake body.'))



@patch('threading.Thread', new=Mock())
@patch('lamson.routing.Router', new=Mock())
def test_SMTPReceiver():
    receiver = server.SMTPReceiver(port=9999)
    receiver.start()
    receiver.process_message('localhost', 'test@test.com', 'test@test.com',
                             'Fake body.')

    routing.Router.deliver.side_effect = raises_exception
    receiver.process_message('localhost', 'test@test.com', 'test@test.com',
                             'Fake body.')

    receiver.close()

