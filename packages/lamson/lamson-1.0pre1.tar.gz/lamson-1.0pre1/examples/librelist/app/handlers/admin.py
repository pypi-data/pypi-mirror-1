from email.utils import parseaddr
from config.settings import relay
from lamson import view, queue
from lamson.routing import route, stateless, route_like, state_key_generator
from lamson.bounce import bounce_to
from app.model import confirmation, mailinglist, bounce, archive
import logging
from app.handlers import bounce

@state_key_generator
def module_and_to(module_name, message):
    name, address = parseaddr(message['to'])
    if '-' in address:
        list_name = address.split('-')[0]
    else:
        list_name = address.split('@')[0]

    return module_name + ':' + list_name


@route('(list_name)@(host)')
@route('(list_name)-subscribe@(host)')
@bounce_to(soft=bounce.BOUNCED_SOFT, hard=bounce.BOUNCED_HARD)
def START(message, list_name=None, host=None):
    if mailinglist.find_list(list_name):
        action = "subscribe to"
        confirmation.send(relay, list_name, message, 'mail/confirmation.msg',
                          locals())
    else:
        similar_lists = mailinglist.similar_named_lists(list_name)
        confirmation.send(relay, list_name, message, 'mail/create_confirmation.msg',
                          locals())


    return CONFIRMING_SUBSCRIBE

@route('(list_name)-confirm-(id_number)@(host)')
def CONFIRMING_SUBSCRIBE(message, list_name=None, id_number=None, host=None):
    original = confirmation.verify(list_name, message, id_number)

    if original:
        mailinglist.add_subscriber(message['from'], list_name)
        mailinglist.post_message(relay, original, list_name, host)

        msg = view.respond(locals(), "mail/subscribed.msg",
                           From="noreply@%(host)s",
                           To=message['from'],
                           Subject="Welcome to %(list_name)s list.")
        relay.deliver(msg)

        return POSTING
    else:
        logging.warning("Invalid confirm from %s", message['from'])
        return CONFIRMING_SUBSCRIBE


@route('(list_name)-(action)@(host)', action='[a-z]+')
@route('(list_name)@(host)')
def POSTING(message, list_name=None, action=None, host=None):
    if action == 'unsubscribe':
        action = "unsubscribe from"
        confirmation.send(relay, list_name, message, 'mail/confirmation.msg',
                          locals())
        return CONFIRMING_UNSUBSCRIBE
    else:
        mailinglist.post_message(relay, message, list_name, host)
        # archive makes sure it gets cleaned up before archival
        final_msg = mailinglist.craft_response(message, list_name + '@' + host)
        archive.enqueue(list_name, final_msg)

        return POSTING
    

@route_like(CONFIRMING_SUBSCRIBE)
def CONFIRMING_UNSUBSCRIBE(message, list_name=None, id_number=None, host=None):
    original = confirmation.verify(list_name, message, id_number)

    if original:
        mailinglist.remove_subscriber(message['from'], list_name)

        msg = view.respond(locals(), 'mail/unsubscribed.msg',
                           From="noreply@%(host)s",
                           To=message['from'],
                           Subject="You are now unsubscribed from %(list_name)s.")
        relay.deliver(msg)

        return START
    else:
        logging.warning("Invalid unsubscribe confirm from %s", message['from'])
        return CONFIRMING_UNSUBSCRIBE


@route("(address)@(host)", address=".+")
def BOUNCING(message, address=None, host=None):
    msg = view.respond(locals(), 'mail/we_have_disabled_you.msg',
                       From='unbounce@librelist.com',
                       To=message['from'],
                       Subject='You have bounced and are disabled.')
    relay.deliver(msg)
    return BOUNCING

