# This file contains python variables that configure Lamson for email processing.
import logging

# configure logging to go to a log file
log_file = "logs/lamson.log"

relay_config = {'host': 'localhost', 'port': 8825}

receiver_config = {'host': 'localhost', 'port': 8823}

database_config = {
    "metadata" : None,
    "url" : 'sqlite:///app/data/main.db',
    "log_level" : logging.DEBUG
}

handlers = []

router_defaults = {'host': 'test\\.com'}

template_config = {'dir': 'lamson_tests', 'module': '.'}

BLOG_BASE="app/data/posts"

# this is for when you run the config.queue boot
queue_config = {'queue': 'run/deferred', 'sleep': 10}

queue_handlers = []

