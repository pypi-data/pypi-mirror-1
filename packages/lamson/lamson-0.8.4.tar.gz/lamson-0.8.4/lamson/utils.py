from lamson import server, handlers
import sys, os
import logging

def import_settings():
    """Used to import the settings in a Lamson project."""
    sys.path.append(".")
    from config import settings
    return settings


def daemonize(pid_file, stdin="/dev/null", stdout="logs/lamson.out", stderr="logs/lamson.err"):
    """
    A function to do a proper daemonize for the server.
    There's gotta be something better than this.  Taken from http://code.activestate.com/recipes/66012/
    """
    try: 
        pid = os.fork() 
        if pid > 0:
            # exit first parent
            sys.exit(0) 
    except OSError, e: 
        logging.error("fork #1 failed: %d (%s)" % (e.errno, e.strerror))
        sys.exit(1)

    # we don't do chmod and friends yet because people usually expect it to run
    # like their user id initially

    # do second fork
    try: 
        pid = os.fork() 
        if pid > 0:
            # exit from second parent
            sys.exit(0)
    except OSError, e: 
        logging.error("fork #2 failed: %d (%s)" % (e.errno, e.strerror))
        sys.exit(1) 

    si = file(stdin, 'r')
    so = file(stdout, 'a+')
    se = file(stderr, 'a+', 0)
    pid = str(os.getpid())

    sys.stderr.flush()
    file(pid_file,'w+').write("%s\n" % pid)

    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())


def configure_database(settings, also_create=False):
    """Configures the lamson database, and can create it as well."""
    if settings:
        database = server.Database(settings["metadata"],
                                  settings["url"],
                                  log_level=settings["log_level"])
        database.configure()
        if also_create:
            logging.info("Creating the database with %s." % database.url)
            database.create()
    else:
        database = None
        logging.warning("No database configured, create a database variable in settings.py")

    return database


def start_server(settings, pid_file="./run/smtp.pid"):
    """
    Uses the settings given to startup the server."""
    daemonize(pid_file)

    relay = server.Relay(
        settings.relay["host"], 
        port=settings.relay["port"],
        debug=settings.relay["debug"],
    )

    database = configure_database(settings.database)
    router = server.Router(settings.handlers, relay, database,
        settings.templates["directories"],
        settings.templates["module_directory"])
    receiver = server.SMTPReceiver(settings.receiver, router)

    logging.info("Receiving on %s:%s" % (settings.receiver["host"],
                                  settings.receiver["port"]))

    receiver.start()


class FakeSettings(object): 
    """
    Used to pass fake settings in the situations where we're running a server
    that doesn't have an actual application to use.  The log command is a good
    example of this.
    """

def make_fake_settings(options, handlers):
    settings = FakeSettings()
    # configure up basic settings for logging
    settings.handlers = handlers
    settings.receiver = {"host" : options['host'], "port" : options['port'], "debug": options['debug']}
    settings.relay = settings.receiver
    settings.database = None
    settings.templates = {"directories": "/tmp", "module_directory": "/tmp"}
    logging.info("Logging mode enabled, will not send email to anyone, just log.")

    return settings

