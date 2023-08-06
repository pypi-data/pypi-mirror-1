from nose.tools import *
from lamson.testing import *
from lamson import mail
from config import settings
from app.model import addressing


client = RouterConversation("person@test.com", "Anonymizing Tests")
marketroid = RouterConversation("buymycrap@stuff.com", "Marketroid Tests")
host = "myinboxisnota.tv"

def setup():
    client.begin()
    marketroid.begin()

def teardown():
    addressing.delete("person@test.com")
    addressing.delete("buymycrap@stuff.com")


def test_client_subscribes():
    client.begin()
    confirm = client.say("start@%s" % host, "subscribe me", "start-confirm")
    welcome = client.say(confirm['from'], "confirm me", "user")

    return welcome['from']

def test_client_receives_normal_mail():
    marketroid.begin()
    user_id = test_client_subscribes()
    
    to_user = marketroid.say(user_id, "I have a great offer for you!", "marketroid")

    assert to_user['reply-to'] != "buymycrap@stuff.com"
    to_marketroid = client.say(to_user['reply-to'], "I don't want your junk.", "user")
   
    assert to_marketroid['from'] != 'person@test.com'

    to_user2 = marketroid.say(to_marketroid['from'], "Hey you should buy my stuff.", "marketroid")

    assert_equal(to_user['reply-to'], to_user2['reply-to'])

    addressing.delete(user_id.split('@')[0])


def test_user_to_user_forbid():
    user_id = test_client_subscribes()

    client.say(user_id, "I want to email myself.", "noreply")
    

