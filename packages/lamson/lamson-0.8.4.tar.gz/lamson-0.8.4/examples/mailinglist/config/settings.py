# This file contains python variables that configure SoS for email processing.

from lamson.handlers import Conversation, LogHandler, ForwardHandler
import logging
from app.model import table

# configure logging to go to a log file
logging.basicConfig(filename="logs/lamson.log", level=logging.DEBUG)

# the relay host to actually send the final message to
relay = { "host": "localhost", "port": 8899, "debug": 1}

# where to listen for incoming messages
receiver = { "host": "localhost", "port": 8823}

database = {
    "metadata" : table.metadata,
    "url" : 'sqlite:///app/data/main.db',
    "log_level" : logging.DEBUG
}

DEBUG=True
DELIVER_DIRECTLY=False
HOST="test.com"

handlers = [
    ("^([a-z.A-Z0-9]+)-(unsubscribe)@(HOST)$", 
         Conversation('app.handlers.admin', reload=DEBUG)),
    ("^([a-z.A-Z0-9]+)-(subscribe)@(HOST)$", 
         Conversation('app.handlers.admin', reload=DEBUG)),
    ("^([a-z.A-Z0-9]+)-(pause)@(HOST)$", 
         Conversation('app.handlers.admin', reload=DEBUG)),
    ("^([a-z.A-Z0-9]+)-(unpause)@(HOST)$", 
         Conversation('app.handlers.admin', reload=DEBUG)),
    ("^([a-z.A-Z0-9]+)-(confirm)-([0-9]+)@(HOST)$", 
         Conversation('app.handlers.admin', reload=DEBUG)),
    ("^([a-z.A-Z0-9]+)@(HOST)$", 
         Conversation('app.handlers.debate', unique=True, reload=DEBUG)),
    ("^([a-z.A-Z0-9]+)-(.+)@(HOST)$", 
         Conversation('app.handlers.admin', reload=DEBUG)),
    ("^(.+)@(HOST)$", ForwardHandler()),
    ("^(.+)@(.+)$", LogHandler()),
]

# this just does a quick replace on the handlers so we can set the host
handlers = [(m.replace("HOST", HOST), h) for m,h in handlers]


# this used by app.handlers.delivery to figure out if it should deliver right
# away to the relay server or enqueue for itself later.

queue_dir = "run/queue"

queue_handlers = [
    ("^([a-z.A-Z0-9]+)@(.+)$", 
         Conversation('app.handlers.delivery', unique=True, reload=DEBUG)),
    ("^(.+)@(.+)$", LogHandler()),
]

templates = {
    "directories": ["./app/templates"],
    "module_directory": "/tmp/lamson_modules"
}


