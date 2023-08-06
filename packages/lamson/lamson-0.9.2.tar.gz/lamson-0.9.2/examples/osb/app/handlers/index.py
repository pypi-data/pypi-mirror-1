from app.model import post, confirmation
from email.utils import parseaddr
from config.settings import relay, database
from lamson import view, queue
from lamson.routing import route, Router, stateless
import logging


@route("(post_name)@osb\\.(host)")
@stateless
def START(message, post_name=None, host=None):
    logging.debug("Got message from %s", message['from'])


