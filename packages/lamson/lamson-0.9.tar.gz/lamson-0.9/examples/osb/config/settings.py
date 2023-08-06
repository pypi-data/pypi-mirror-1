# This file contains python variables that configure Lamson for email processing.
from app.model import table
import logging

# configure logging to go to a log file
log_file = "logs/lamson.log"

relay_config = {'host': 'localhost', 'port': 8825}

receiver_config = {'host': 'localhost', 'port': 8823}

database_config = {
    "metadata" : table.metadata,
    "url" : 'sqlite:///app/data/main.db',
    "log_level" : logging.DEBUG
}


handlers = ['app.handlers.osb']

router_defaults = {'host': 'test\\.com'}

template_config = {'dir': 'app', 'module': 'templates'}

BLOG_BASE="app/data/posts"
