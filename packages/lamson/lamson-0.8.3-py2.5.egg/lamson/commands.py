from lamson import server, handlers, args, utils, queue
import lamson
import smtplib
import sys
import logging
import signal
import os
import time
import glob
from pkg_resources import resource_stream
from zipfile import ZipFile



def log_command(options):
    """
    Runs a logging only server on the given hosts and port:

    lamson log -port 8825 -host 127.0.0.1 -debug 1 -queue "" -pid ./run/log.pid

    Set -queue to the name of the queue to use.
    """
    args.defaults(options, port=8825, host='127.0.0.1', debug=1, queue="",
                  pid="./run/log.pid")

    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    routing = []

    if options['queue']:
        queue_dir = options["queue"]
        routing.append( ("^(.*)@(.*)$", handlers.QueueHandler(queue_dir)) )
    else:
        routing.append( ("^(.*)@(.*)$", handlers.LogHandler()) )

    settings = utils.make_fake_settings(options, routing)
    utils.start_server(settings, options["pid"])


def send_command(options):
    """
    Sends an email to someone as a test message.
    See the sendmail command for a sendmail replacement.
    
    lamson send -port 8825 -host 127.0.0.1 -debug 1 -sender EMAIL -to EMAIL -subject STR -body STR -file False'
    """
    args.defaults(options, port=8825, host='127.0.0.1', debug=1, sender=None,
                  to=None, subject=None, body=None, file=False)

    message = server.MailResponse(From=options['sender'],
                                     To=options['to'],
                                     Subject=options['subject'])
    if options["file"]:
        message.attach(options["file"])

    relay = server.Relay(options['host'], port=options['port'],
                         debug=options['debug'])
    relay.deliver(message)


def sendmail_command(options):
    """
    Used as a testing sendmail replacement for use in programs
    like mutt as an MTA.  It reads the email to send on the stdin
    and then delivers it based on the port and host settings.

    lamson sendmail -port 8825 -host 127.0.0.1 -debug 0 -- [recipients]
    """
    args.defaults(options, port=8825, host='127.0.0.1', debug=0)

    relay = server.Relay(options['host'], port=options['port'],
                           debug=options['debug'])
    data = sys.stdin.read()
    msg = server.MailRequest(None, options['TRAILING'], None, data)
    relay.deliver(msg)



def syncdb_command(options):
    """
    Creates the database and other stuff for Lamson.

    lamson syncdb -create True
    """
    args.defaults(options, create=True)

    settings = utils.import_settings()
    utils.configure_database(settings.database, also_create=options['create'])


def start_command(options):
    """
    Runs a lamson server out of the current directory:

    lamson start -pid ./run/smtp.pid -FORCE False
    """
    args.defaults(options, pid='./run/smtp.pid', FORCE=False)

    if os.path.exists(options["pid"]):
        if not options["FORCE"]:
            print "PID file %s exists, so assuming Lamson is running.  Give -FORCE to force it to start." % options["pid"]
            sys.exit(1)

    settings = utils.import_settings()
    utils.start_server(settings, options["pid"])


def stop_command(options):
    """
    Stops a running lamson server.  Give -KILL True to have it
    stopped violently.  The PID file is removed after the 
    signal is sent.  Give -ALL the name of a run directory and
    it will stop all pid files it finds there.

    lamson stop -pid ./run/smtp.pid -KILL False -ALL False
    """
    args.defaults(options, pid='./run/smtp.pid', KILL=False, ALL=False)



    pid_files = []

    if options["ALL"]:
        pid_files = glob.glob(options["ALL"] + "/*.pid")
    else:
        pid_files = [options["pid"]]

        if not os.path.exists(options["pid"]):
            print "PID file %s doesn't exist, maybe Lamson isn't running?" % options["pid"]
            sys.exit(1)

    print "Stopping processes with the following PID files: %s" % pid_files

    # TODO: carve this out into a separate function
    for file in pid_files:
        pid = open(file).readline()

        print "Attempting to stop lamson at pid %d" % int(pid)

        try:
            if options['KILL']:
                os.kill(int(pid), signal.SIGKILL)
            else:
                os.kill(int(pid), signal.SIGTERM)
            
            os.unlink(file)
        except OSError, exc:
            print "ERROR stopping Lamson on PID %d: %s" % (int(pid), exc)


def restart_command(options):
    """
    Simply attempts a stop and then a start command.  All options for both
    apply to restart.

    lamson restart -pid ./run/smtp.pid -FORCE False -KILL False
    """

    stop_command(options)
    time.sleep(2)
    start_command(options)


def status_command(options):
    """
    Prints out status information about lamson useful for finding out if it's
    running and where.

    lamson status -pid ./run/smtp.pid
    """
    args.defaults(options, pid='./run/smtp.pid')


    if os.path.exists(options["pid"]):
        pid = open(options["pid"]).readline()
        print "Lamson running with PID %d" % int(pid)
    else:
        print "Lamson not running."


def help_command(options):
    """
    Prints out help for the commands. 

    lamson help

    You can get help for one command with:

    lamson help -for STR
    """
    if "for" in options:
        help = args.help_for_command(lamson.commands, options["for"])
        if help:
            print help
        else:
            args.invalid_command_message(lamson.commands, exit_on_error=True)
    else:
        print "Lamson help:\n"
        print "\n".join(args.available_help(lamson.commands))


def queue_command(options):
    """
    Let's you do most of the operations available to a queue.

    lamson queue (-pop | -get | -remove | -count | -clear | -keys) -name run/queue
    """
    args.defaults(options, pop=False, get=False, keys=False,
                  remove=False, count=False, clear=False,
                  name="run/queue")

    q = queue.Queue(options["name"])

    if options["pop"]:
        key, msg = q.pop()
        if key:
            print "KEY: ", key
            print msg
    elif options["get"]:
        print q.get(options["get"])
    elif options["remove"]:
        q.remove(options["remove"])
    elif options["count"]:
        print "Queue %s contains %d messages" % (options["name"], q.count())
    elif options["clear"]:
        q.clear()
    elif options["keys"]:
        print "\n".join(q.keys())
    else:
        print "Give something to do.  Try lamson help -for queue to find out what."
        sys.exit(1)
        

def deq_command(options):
    """
    Runs a lamson dequeue server, which reads messages out of a queue and
    processes them.

    lamson deq -pid ./run/deq.pid -FORCE False -sleep 60
    """
    args.defaults(options, pid='./run/deq.pid', FORCE=False, sleep=60)

    if os.path.exists(options["pid"]):
        if not options["FORCE"]:
            print "PID file %s exists, so assuming Lamson is running.  Give -FORCE to force it to start." % options["pid"]
            sys.exit(1)

    settings = utils.import_settings()

    utils.daemonize(options["pid"])

    relay = server.Relay(
        settings.relay["host"], 
        port=settings.relay["port"],
        debug=settings.relay["debug"],
    )

    database = utils.configure_database(settings.database)

    router = server.Router(settings.queue_handlers, relay, database,
        settings.templates["directories"],
        settings.templates["module_directory"])

    receiver = server.QueueReceiver(settings.queue_dir, router, options["sleep"])
    receiver.start()

def gen_command(options):
    """
    Generates various useful things for you to get you started.

    lamson gen -project STR
    """
    args.defaults(options, project=None)
    project = options['project']

    if os.path.exists(project):
        print "Project %s exists, delete it first." % project
        sys.exit(1)

    prototype = ZipFile(resource_stream(__name__, 'data/prototype.zip'))
    # looks like the very handy ZipFile.extractall is only in python 2.6

    os.makedirs(project)
    files = prototype.namelist()

    for file in files:
        if str(file).endswith('/'):
            target = os.path.join(project, file)
            if not os.path.exists(target):
                print "mkdir: %s" % target
                os.makedirs(target)
        else:
            target = os.path.join(project, file)
            if os.path.exists(target): continue
            print "copy: %s" % target
            out = open(target, 'w')
            out.write(prototype.read(file))
            out.close()

