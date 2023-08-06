"""
Implements the Lamson command line tool's commands, which are run
by the lamson.args module dynamically.  Each command has it's
actual user displayed command line documentation as the __doc__
string.

You will notice that all of the command functions in this module
end in _command.  This is not required by the lamson.args module
but it is the default.  You could easily use any other suffix, or
none at all.

This is done to disambiguate the command that it implements
so that your command line tools do not clash with Python's
reserved words and built-ins.  With this design you can have a
list_command without clashing with list().

You will also notice that commands which take trailing positional
arguments give a TRAILING=[] or TRAILING=None (if it's required).
This is done instead of *args because we need to use None to indicate
that this command requires positional arguments.  TRAILING=[] is 
like saying they are optional (but expected), and TRAILING=None is
like saying they are required.  You can't (afaik) do TRAILING=None
with *args.

See lamson.args for more details.
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


def log_command(port=8825, host='127.0.0.1', debug=1, queue="", chroot=False,
                cd=".", uid=False, gid=False, umask=False, pid="./run/log.pid"):
    """
    Runs a logging only server on the given hosts and port.  It logs
    each message it receives and also stores it to the run/queue 
    so that you can make sure it was received in testing.

    lamson log -port 8825 -host 127.0.0.1 -debug 1 \\
            -pid ./run/log.pid -chroot False  \\
            -cd "." -umask False -uid False -gid False
    """
    if os.path.exists(pid):
        print "PID file %s exists, delete it first." % pid
        sys.exit(1)

    utils.daemonize(pid, cd, chroot, uid, gid, umask, files_preserve=[])
    sys.path.append(os.getcwd())
    logging.basicConfig(filename="logs/logger.log", level=logging.DEBUG)

    routing.Router.load(['lamson.handlers.log', 'lamson.handlers.queue'])

    settings = utils.make_fake_settings(host, port)
    settings.receiver.start()


def send_command(port=8825, host='127.0.0.1', debug=1, sender=None, to=None,
                 subject=None, body=None, file=False):
    """
    Sends an email to someone as a test message.
    See the sendmail command for a sendmail replacement.
    
    lamson send -port 8825 -host 127.0.0.1 -debug 1 \\
            -sender EMAIL -to EMAIL -subject STR -body STR -file False'
    """
    message = mail.MailResponse(From=sender,
                                  To=to,
                                  Subject=subject,
                                  Body=body)
    if file:
        message.attach(file)

    relay = server.Relay(host, port=port,
                         debug=debug)
    relay.deliver(message)


def sendmail_command(port=8825, host='127.0.0.1', debug=0, TRAILING=[]):
    """
    Used as a testing sendmail replacement for use in programs
    like mutt as an MTA.  It reads the email to send on the stdin
    and then delivers it based on the port and host settings.

    lamson sendmail -port 8825 -host 127.0.0.1 -debug 0 -- [recipients]
    """
    relay = server.Relay(host, port=port,
                           debug=debug)
    data = sys.stdin.read()
    msg = mail.MailRequest(None, TRAILING, None, data)
    relay.deliver(msg)



def syncdb_command(create=True):
    """
    Creates the database and other stuff for Lamson.

    lamson syncdb -create True
    """
    settings = utils.import_settings(False, from_dir=os.getcwd())
    database = utils.configure_database(settings.database_config)
    database.create()


def start_command(pid='./run/smtp.pid', FORCE=False, chroot=False, cd=".",
                  boot="config.boot", uid=False, gid=False, umask=False):
    """
    Runs a lamson server out of the current directory:

    lamson start -pid ./run/smtp.pid -FORCE False -chroot False -cd "." \\
            -umask False -uid False -gid False -boot config.boot
    """
    if os.path.exists(pid):
        if not FORCE:
            print "PID file %s exists, so assuming Lamson is running.  Give -FORCE to force it to start." % pid
            sys.exit(1)
        else:
            os.unlink(pid)

    utils.daemonize(pid, cd, chroot, uid, gid, umask, files_preserve=[])

    sys.path.append(os.getcwd())
    settings = utils.import_settings(True, from_dir=os.getcwd())
    settings.receiver.start()


def stop_command(pid='./run/smtp.pid', KILL=False, ALL=False):
    """
    Stops a running lamson server.  Give -KILL True to have it
    stopped violently.  The PID file is removed after the 
    signal is sent.  Give -ALL the name of a run directory and
    it will stop all pid files it finds there.

    lamson stop -pid ./run/smtp.pid -KILL False -ALL False
    """
    pid_files = []

    if ALL:
        pid_files = glob.glob(ALL + "/*.pid")
    else:
        pid_files = [pid]

        if not os.path.exists(pid):
            print "PID file %s doesn't exist, maybe Lamson isn't running?" % pid
            sys.exit(1)

    print "Stopping processes with the following PID files: %s" % pid_files

    # TODO: carve this out into a separate function
    for file in pid_files:
        pid = open(file).readline()

        print "Attempting to stop lamson at pid %d" % int(pid)

        try:
            if KILL:
                os.kill(int(pid), signal.SIGKILL)
            else:
                os.kill(int(pid), signal.SIGHUP)
            
            os.unlink(file)
        except OSError, exc:
            print "ERROR stopping Lamson on PID %d: %s" % (int(pid), exc)


def restart_command(**options):
    """
    Simply attempts a stop and then a start command.  All options for both
    apply to restart.  See stop and start for options available.
    """

    stop_command(**options)
    time.sleep(2)
    start_command(**options)


def status_command(pid='./run/smtp.pid'):
    """
    Prints out status information about lamson useful for finding out if it's
    running and where.

    lamson status -pid ./run/smtp.pid
    """
    if os.path.exists(pid):
        pid = open(pid).readline()
        print "Lamson running with PID %d" % int(pid)
    else:
        print "Lamson not running."


def help_command(**options):
    """
    Prints out help for the commands. 

    lamson help

    You can get help for one command with:

    lamson help -for STR
    """
    if "for" in options:
        help = args.help_for_command(lamson.commands, options['for'])
        if help:
            print help
        else:
            args.invalid_command_message(lamson.commands, exit_on_error=True)
    else:
        print "Lamson help:\n"
        print "\n".join(args.available_help(lamson.commands))


def queue_command(pop=False, get=False, keys=False, remove=False, count=False,
                  clear=False, name="run/queue"):
    """
    Let's you do most of the operations available to a queue.

    lamson queue (-pop | -get | -remove | -count | -clear | -keys) -name run/queue
    """
    q = queue.Queue(name)

    if pop:
        key, msg = q.pop()
        if key:
            print "KEY: ", key
            print msg
    elif get:
        print q.get(get)
    elif remove:
        q.remove(remove)
    elif count:
        print "Queue %s contains %d messages" % (name, q.count())
    elif clear:
        q.clear()
    elif keys:
        print "\n".join(q.keys())
    else:
        print "Give something to do.  Try lamson help -for queue to find out what."
        sys.exit(1)
        

def routes_command(TRAILING=['config.testing'], path=os.getcwd(), testing=True):
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
    modules = TRAILING
    sys.path += path.split(':')

    for module in modules:
        __import__(module, globals(), locals())

    print "Routing ORDER: ", routing.Router.ORDER
    print "Routing TABLE: \n---"
    for format in routing.Router.REGISTERED:
        print "%r: " % format,
        for func in routing.Router.REGISTERED[format][1]:
            print "%s.%s " % (func.__module__, func.__name__),
        print "\n---"


def gen_command(project=None):
    """
    Generates various useful things for you to get you started.

    lamson gen -project STR
    """
    project = project

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

def spell_command(TRAILING=None, language="en_US"):
    """
    Runs the PyEnchant spell checker on the given file.  Use this to train
    the spell checker for unit test runs when new words show up.

    lamson spell -langauge en_US -- [files]

    It will run interactively and if you perform an edit on the file it will save
    your changes back to the file and make a backup named with .bak.
    """
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
        enchant.Dict(language)
    except DictNotFoundError, exc:
        print "PyEnchant couldn't find your dictionary.  Put them in ~/.enchant/myspell."
        print exc
        return False

    for file in TRAILING:
        text = open(file).read()
        chkr = SpellChecker(language,filters=[EmailFilter,URLFilter]) 
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


def web_command(basedir=".", port=8888, host='127.0.0.1'):
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

    os.chdir(basedir)
    server = HTTPServer((host, port), SimpleHTTPRequestHandler)
    print "Starting server on %s:%d out of directory %r" % (
        host, port, basedir)
    server.serve_forever()

