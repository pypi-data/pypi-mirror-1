"""
Mostly utility functions Lamson uses internally that don't
really belong anywhere else in the modules.  This module
is kind of a dumping ground, so if you find something that
can be improved feel free to work up a patch.
"""

from lamson import server
import sys, os
import logging
import grp
import signal
import daemon
from daemon import pidlockfile
import lockfile
import logging
import imp


def import_settings(boot_also, from_dir=None, boot_module="config.boot"):
    """Used to import the settings in a Lamson project."""
    if from_dir:
        sys.path.append(from_dir)

    from config import settings

    if boot_also:
        __import__(boot_module, globals(), locals())

    return settings


def daemonize(pid, cd, chroot, uid, gid, umask, files_preserve=[], do_open=True):
    """
    Uses python-daemonize to do all the junk needed to make a
    server a server.  It supports all the features daemonize
    has, except that chroot probably won't work at all without
    some serious configuration on the system.
    """
    context = daemon.DaemonContext()
    context.pidfile=pidlockfile.PIDLockFile(pid)
    context.stdout=open("logs/lamson.out","a+")
    context.stderr=open("logs/lamson.err","a+")
    context.files_preserve = files_preserve
    context.working_directory=os.path.expanduser(cd)
    
    if chroot: 
        context.chroot_directory = os.path.expanduser(chroot)
    if uid != False: 
        context.uid = uid
    if gid != False: 
        context.gid = gid
    if umask != False:
        context.umask = umask

    if do_open:
        context.open()

    return context


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



def make_fake_settings(host, port):
    """
    When running as a logging server we need a fake settings module to work with
    since the logging server can be run in any directory, so there may not be
    a config/settings.py file to import.
    """
    settings = imp.new_module('settings')
    settings.receiver = server.SMTPReceiver(host, port)
    settings.relay = None
    settings.database = None
    settings.log_file = "logs/lamson.log"
    logging.info("Logging mode enabled, will not send email to anyone, just log.")

    return settings

