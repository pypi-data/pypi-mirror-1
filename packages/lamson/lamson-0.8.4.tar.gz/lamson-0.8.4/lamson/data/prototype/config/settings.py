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

# SQLAlchemy database configuration for a simple sqlite3 setup.
# Run lamson syncdb to get this created based on your app/models/table.py
database = {
    "metadata" : table.metadata,
    "url" : 'sqlite:///app/data/main.db',
    "log_level" : logging.DEBUG
}

# used to tell the conversation handlers whether to reload each handler or not
DEBUG=True


# replaced in the regex patterns so you can set the host on deployment
HOST="test.com"

# Base handlers you should have.  Notice you need a ForwardHandler that
# sends unknown mail to your relay, but then a LogHandler catches all
# email not meant for your HOST and just logs it.  This prevents your
# lamson server from being an open relay.  Look at the
# tests/handlers/open_relay_tests.py for tests you'll need too.
handlers = [
    ("^([a-z.A-Z0-9]+)-(.+)@(service.HOST)$", 
         Conversation('app.handlers.sample', reload=DEBUG)),
    ("^(.+)@(HOST)$", ForwardHandler()),
    ("^(.+)@(.+)$", LogHandler()),
]

# does the replace of the HOST in the handler regexes
handlers = [(m.replace("HOST", HOST), h) for m,h in handlers]

# used if you have a handler that works off the run/queue rather than directly
# Typically you'd set this True in testing and then False in real setup.
DELIVER_DIRECTLY=False

# When you have handlers that work off the run/queue for deferred processing
# you use these.
queue_dir = "run/queue"
queue_handlers = [
    ("^(.+)@(.+)$", LogHandler()),
]

# The Mako template configuration.
templates = {
    "directories": ["./app/templates"],
    "module_directory": "/tmp/lamson_modules"
}


