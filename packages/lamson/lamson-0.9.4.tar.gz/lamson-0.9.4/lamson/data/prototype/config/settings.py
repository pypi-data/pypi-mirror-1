# This file contains python variables that configure Lamson for email processing.
from app.model import table
import logging

relay_config = {'host': 'localhost', 'port': 8825}

receiver_config = {'host': 'localhost', 'port': 8823}

database_config = {
    "metadata" : table.metadata,
    "url" : 'sqlite:///app/data/main.db',
    "log_level" : logging.DEBUG
}


handlers = ['app.handlers.sample']

router_defaults = {'host': 'test\\.com'}

template_config = {'dir': 'app', 'module': 'templates'}

# the config/boot.py will turn these values into variables set in settings
