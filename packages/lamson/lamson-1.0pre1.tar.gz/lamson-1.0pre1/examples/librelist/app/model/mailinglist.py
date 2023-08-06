from webapp.librelist.models import *
from django.db.models import Q
from email.utils import parseaddr
from lamson.mail import MailResponse
from config import settings
from lib import metaphone
import Stemmer

def stem_and_meta(list_name):
    s = Stemmer.Stemmer('english')
    name = " ".join(s.stemWords(list_name.split('.')))
    return metaphone.dm(name)

def create_list(list_name):
    list_name = list_name.lower()
    mlist = find_list(list_name)
    sim_pri, sim_sec = stem_and_meta(list_name)

    if not mlist:
        mlist = MailingList(archive_url = "/archives/" + list_name,
                            archive_queue = "/queues/" + list_name,
                            name=list_name,
                            similarity_pri = sim_pri,
                            similarity_sec = sim_sec)
        mlist.save()

    return mlist

def delete_list(list_name):
    MailingList.objects.filter(name = list_name).delete()

def find_list(list_name):
    mlists = MailingList.objects.filter(name = list_name)
    if mlists:
        return mlists[0]
    else:
        return None

def add_subscriber(address, list_name):
    mlist = create_list(list_name)
    sub_name, sub_addr = parseaddr(address)
    subs = find_subscriptions(address, list_name)

    if not subs:
        sub = Subscription(subscriber_name = sub_name,
                           subscriber_address = sub_addr,
                           mailing_list = mlist)
        sub.save()
        return sub
    else:
        return subs[0]

def remove_subscriber(address, list_name):
    find_subscriptions(address, list_name).delete()

def remove_all_subscriptions(address):
    find_subscriptions(address).delete()

def find_subscriptions(address, list_name=None):
    sub_name, sub_addr = parseaddr(address)

    if list_name:
        mlist = find_list(list_name)
    else:
        mlist = None

    if mlist:
        subs = Subscription.objects.filter(
            subscriber_address=sub_addr, mailing_list = mlist
        ).exclude(
            enabled=False)
    else:
        subs = Subscription.objects.filter(
            subscriber_address=sub_addr
        ).exclude(
            enabled=False)

    return subs


def post_message(relay, message, list_name, host):
    mlist = find_list(list_name)
    assert mlist, "User is somehow able to post to list %s" % list_name

    for sub in mlist.subscription_set.all().values('subscriber_address'):
        list_addr = "%s@%s" % (list_name, host)
        delivery = craft_response(message, list_addr) 
        relay.deliver(delivery, To=sub['subscriber_address'], From=list_addr)


def craft_response(message, list_addr):
    response = MailResponse(To=list_addr, 
                            From=message['from'],
                            Subject=message['subject'],
                            Body=message.body())
    response.update({
        "Sender": list_addr, 
        "Reply-To": list_addr,
        "List-Id": list_addr,
        "Return-Path": list_addr, 
        "Precedence": 'list',})

    if 'message-id' in message:
        response["In-Reply-To"] = message['Message-Id']
        response["References"] = message['Message-Id']

    return response


def disable_all_subscriptions(address):
    Subscription.objects.filter(subscriber_address=address).update(enabled=False)

def enable_all_subscriptions(address):
    Subscription.objects.filter(subscriber_address=address).update(enabled=True)

def similar_named_lists(list_name):
    sim_pri, sim_sec = stem_and_meta(list_name)
    sim_sec = sim_sec or sim_pri

    return MailingList.objects.filter(Q(similarity_pri = sim_pri) | 
                                       Q(similarity_sec =
                                         sim_sec))

