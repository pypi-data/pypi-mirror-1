from config import settings
from lamson.routing import Router
from lamson.server import Relay, SMTPReceiver
from lamson.utils import configure_database
from lamson import view
import logging
import jinja2

# configure logging to go to a log file
logging.basicConfig(filename=settings.log_file, level=logging.DEBUG)

# the relay host to actually send the final message to
settings.relay = Relay(host=settings.relay_config['host'], 
                       port=settings.relay_config['port'], debug=1)

# where to listen for incoming messages
settings.receiver = SMTPReceiver(settings.receiver_config['host'],
                                 settings.receiver_config['port'])

settings.database = configure_database(settings.database_config, also_create=False)

Router.defaults(**settings.router_defaults)
Router.load(settings.handlers)
Router.RELOAD=True

view.LOADER = jinja2.Environment(
    loader=jinja2.PackageLoader(settings.template_config['dir'], 
                                settings.template_config['module']))

