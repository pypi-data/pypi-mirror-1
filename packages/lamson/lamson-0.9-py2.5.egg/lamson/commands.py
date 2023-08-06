"""
Implements the Lamson command line tool's commands, which are run
by the lamson.args module dynamically.  Each command has it's
actual user displayed command line documentation as the __doc__
string.
"""

from lamson import server, args, utils, queue, mail, routing
import lamson
import smtplib
import sys
import logging
import signal
import os
import time
import glob
import imp
from pkg_resources import resource_stream
from zipfile import ZipFile


def log_command(options):
    """
    Runs a logging only server on the given hosts and port.  It logs
    each message it receives and also stores it to the run/queue 
    so that you can make sure it was received in testing.

    lamson log -port 8825 -host 127.0.0.1 -debug 1 \\
            -pid ./run/log.pid -chroot False  \\
            -cd "." -umask False -uid False -gid False
    """
    args.defaults(options, port=8825, host='127.0.0.1', debug=1, queue="",
             chroot=False, cd=".", uid=False, gid=False, umask=False, pid="./run/log.pid")

    if os.path.exists(options['pid']):
        print "PID file %s exists, delete it first." % options['pid']
        sys.exit(1)

    utils.daemonize(options, [])
    sys.path.append(os.getcwd())
    logging.basicConfig(filename="logs/logger.log", level=logging.DEBUG)

    routing.Router.load(['lamson.handlers.log', 'lamson.handlers.queue'])

    settings = utils.make_fake_settings(options)
    settings.options = options
    settings.receiver.start()


def send_command(options):
    """
    Sends an email to someone as a test message.
    See the sendmail command for a sendmail replacement.
    
    lamson send -port 8825 -host 127.0.0.1 -debug 1 \\
            -sender EMAIL -to EMAIL -subject STR -body STR -file False'
    """
    args.defaults(options, port=8825, host='127.0.0.1', debug=1, sender=None,
                  to=None, subject=None, body=None, file=False)

    message = mail.MailResponse(From=options['sender'],
                                  To=options['to'],
                                  Subject=options['subject'],
                                  Body=options['body'])
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
    msg = mail.MailRequest(None, options['TRAILING'], None, data)
    relay.deliver(msg)



def syncdb_command(options):
    """
    Creates the database and other stuff for Lamson.

    lamson syncdb -create True
    """
    args.defaults(options, create=True)

    settings = utils.import_settings(False, from_dir=os.getcwd())
    database = utils.configure_database(settings.database_config)
    database.create()


def start_command(options):
    """
    Runs a lamson server out of the current directory:

    lamson start -pid ./run/smtp.pid -FORCE False -chroot False -cd "." -umask False -uid False -gid False
    """
    args.defaults(options, pid='./run/smtp.pid', FORCE=False, chroot=False, cd=".", uid=False, gid=False, umask=False)

    if os.path.exists(options["pid"]):
        if not options["FORCE"]:
            print "PID file %s exists, so assuming Lamson is running.  Give -FORCE to force it to start." % options["pid"]
            sys.exit(1)
        else:
            os.unlink(options["pid"])

    utils.daemonize(options, [])

    sys.path.append(os.getcwd())
    settings = utils.import_settings(True, from_dir=os.getcwd())
    settings.options = options
    settings.receiver.start()


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
                os.kill(int(pid), signal.SIGHUP)
            
            os.unlink(file)
        except OSError, exc:
            print "ERROR stopping Lamson on PID %d: %s" % (int(pid), exc)


def restart_command(options):
    """
    Simply attempts a stop and then a start command.  All options for both
    apply to restart.  See stop and start for options available.
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
        

def routes_command(options):
    """
    Prints out valuable information about an application's routing configuration
    after everything is loaded and ready to go.  Helps debug problems with
    messages not getting to your handlers.  Path has the search paths you want
    separated by a ':' character, and it's added to the sys.path.

    lamson routes -path $PWD -- config.testing

    It defaults to running your config.testing to load the routes. 
    If you want it to run the config.boot then give that instead:

    lamson routes -- config.boot

    """
    args.defaults(options, TRAILING=['config.testing'], path=os.getcwd(), testing=True)
    modules = options['TRAILING']
    sys.path += options['path'].split(':')

    for module in modules:
        __import__(module, globals(), locals())

    print "Routing ORDER: ", routing.Router.ORDER
    print "Routing TABLE: \n---"
    for format in routing.Router.REGISTERED:
        print "%r: " % format,
        for func in routing.Router.REGISTERED[format][1]:
            print "%s.%s " % (func.__module__, func.__name__),
        print "\n---"


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

def spell_command(options):
    """
    Runs the PyEnchant spell checker on the given file.  Use this to train
    the spell checker for unit test runs when new words show up.

    lamson spell -langauge en_US -- [files]

    It will run interactively and if you perform an edit on the file it will save
    your changes back to the file and make a backup named with .bak.
    """

    args.defaults(options, TRAILING=None, language="en_US")

    sys.path.append(os.getcwd())

    try:
        from config import testing
    except ImportError, exc:
        print "Couldn't import config.testing, assuming you know what you're doing."

    if 'PYENCHANT_LIBRARY_PATH' not in os.environ:
        print "You don't have 'PYENCHANT_LIBRARY_PATH' set, PyEnchant will fail.  Set it in config/testing.py"
        print "Looks like you don't know what you're doing.  :-)"

    try:
        from enchant import DictNotFoundError
        import enchant.checker 
        from enchant.checker.CmdLineChecker import CmdLineChecker 
        from enchant.checker import SpellChecker 
        from enchant.tokenize import EmailFilter, URLFilter 
    except ImportError, exc:
        print "PyEnchant failed to import, you probably have to set 'PYENCHANT_LIBRARY_PATH' in config.testing or in the ENV."
        print "Yep, you don't know what you're doing.  Read the documentation for help."
        return False

    try:
        enchant.Dict(options['language'])
    except DictNotFoundError, exc:
        print "PyEnchant couldn't find your dictionary.  Put them in ~/.enchant/myspell."
        print exc
        return False

    for file in options['TRAILING']:
        text = open(file).read()
        chkr = SpellChecker(options['language'],filters=[EmailFilter,URLFilter]) 
        chkr.set_text(text) 
        cmdln = CmdLineChecker() 
        cmdln.set_checker(chkr) 
        cmdln.run()
        new_text = chkr.get_text()
        if new_text != text:
            print "Saving old text to %s.bak and writing changes." % file
            open(file + ".bak", "w").write(text)
            open(file, "w").write(new_text)

    return True


def web_command(options):
    """
    Starts a very simple files only web server for easy testing of applications
    that need to make some HTML files as the result of their operation.
    If you need more than this then use a real web server.

    lamson web -basedir "." -port 8888 -host '127.0.0.1'

    This command doesn't exit so you can view the logs it prints out.
    """
    from BaseHTTPServer import HTTPServer
    from SimpleHTTPServer import SimpleHTTPRequestHandler 
    import os

    args.defaults(options, basedir=".", port=8888, host='127.0.0.1')

    os.chdir(options['basedir'])
    server = HTTPServer((options['host'], options['port']), SimpleHTTPRequestHandler)
    print "Starting server on %s:%d out of directory %r" % (
        options['host'], options['port'], options['basedir'])
    server.serve_forever()

