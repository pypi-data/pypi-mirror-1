from app.model import post, confirmation
from email.utils import parseaddr
from config.settings import relay, database
from lamson import view 
from lamson.routing import route, Router, stateless
import logging


Router.defaults(post_name="[a-zA-Z0-9.]+")

@route("(post_name)@osb\\.(host)")
def START(message, post_name=None, address=None, host=None):
    pending_id = confirmation.push(message)
    confirm_address = confirmation.register(message, post_name, host, pending_id)
    msg = view.respond("confirm.msg", locals())
    relay.deliver(msg)

    return NEW_USER


@route("(post_name)-confirm-(id_number)@osb\\.(host)", id_number="[a-z0-9]+")
def NEW_USER(message, post_name=None, id_number=None, host=None):
    pending_id = confirmation.verify(message, post_name, id_number)

    if pending_id:
        original = confirmation.get(pending_id)

        name, address = parseaddr(original['from'])
        post_id = post.post(post_name, address, original)
        msg = view.respond("welcome.msg", locals())
        relay.deliver(msg)

        return POSTING
    else:
        logging.debug("Invalid confirm from %s", message['from'])
        return NEW_USER



@route("(post_name)@osb\\.(host)")
@route("(post_name)-(action)@osb\\.(host)", action="[a-z]+")
def POSTING(message, post_name=None, host=None, action=None):
    name, address = parseaddr(message['from'])

    if not action:
        post.post(post_name, address, message)
        msg = view.respond('page_ready.msg', locals())
        relay.deliver(msg)
    elif action == "delete":
        post.delete(post_name, address)
    else:
        logging.debug("Invalid action: %r", action)

    return POSTING



