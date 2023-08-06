from lamson import commands, utils, mail, routing
from lamson.testing import spelling
from nose.tools import *
import os
import shutil
from mock import *
import sys
import imp


def setup():
    if os.path.exists("run/fake.pid"):
        os.unlink("run/fake.pid")

def teardown():
    if os.path.exists("run/fake.pid"):
        os.unlink("run/fake.pid")

def make_fake_pid_file():
    f = open("run/fake.pid","w")
    f.write("0")
    f.close()


def test_send_command():
    commands.send_command(sender='test@test.com',
                           to='test@test.com',
                           body='Test body',
                           subject='Test subject',
                           file='setup.py',
                           port=8899,debug=0)

def test_status_command():
    commands.status_command(pid='run/log.pid')
    commands.status_command(pid='run/donotexist.pid')


@patch('sys.exit', new=Mock())
def test_help_command():
    commands.help_command()
    commands.help_command(**{'for': 'status'})

    # test with an invalid command
    commands.help_command(**{'for': 'invalid_command'})
    assert sys.exit.called

@patch('lamson.queue.Queue')
@patch('sys.exit', new=Mock())
def test_queue_command(MockQueue):
    mq = MockQueue()
    mq.get.return_value = "A sample message"
    mq.keys.return_value = ["key1","key2"]
    mq.pop.return_value = ('key1', 'message1')
    mq.count.return_value = 1
    
    commands.queue_command(pop=True)
    assert mq.pop.called
    
    commands.queue_command(get='somekey')
    assert mq.get.called
    
    commands.queue_command(remove='somekey')
    assert mq.remove.called
    
    commands.queue_command(clear=True)
    assert mq.clear.called
    
    commands.queue_command(keys=True)
    assert mq.keys.called

    commands.queue_command(count=True)
    assert mq.count.called

    commands.queue_command()
    assert sys.exit.called


@patch('sys.exit', new=Mock())
def test_gen_command():
    project = 'tests/testproject'
    if os.path.exists(project):
        shutil.rmtree(project)

    commands.gen_command(project=project)
    assert os.path.exists(project)

    # test that it exits if the project exists
    commands.gen_command(project=project)
    assert sys.exit.called

    shutil.rmtree(project)


def test_routes_command():
    commands.routes_command(TRAILING=['lamson.handlers.log',
                                      'lamson.handlers.queue'])

    # test with the -test option
    commands.routes_command(TRAILING=['lamson.handlers.log',
                                      'lamson.handlers.queue'],
                            test="anything@anywhere.com")

    # test with the -test option but no matches
    routing.Router.clear_routes()
    commands.routes_command(TRAILING=[], test="anything@anywhere.com")

def test_spell_command():
    if 'PYENCHANT_LIBRARY_PATH' not in os.environ:
        if os.path.exists('/opt/local/lib/libenchant.dylib'):
            os.environ['PYENCHANT_LIBRARY_PATH'] = '/opt/local/lib/libenchant.dylib'
        else:
            print "Can't test the spelling APIs on this machine.  Sorry."
            return

    # we have to make sure the template is spelled correctly or else the command
    # will block the nosetests since it expects input from the user
    template = "tests/lamson_tests/template.txt"
    contents = open(template).read()
    assert spelling(template, contents), "%s has to be spelled right." % template

    assert commands.spell_command(TRAILING=["tests/lamson_tests/template.txt"],
                                  language='en_US')


@patch('sys.exit', new=Mock())
@patch('lamson.utils.daemonize', new=Mock())
@patch('lamson.server.SMTPReceiver')
def test_log_command(MockSMTPReceiver):
    ms = MockSMTPReceiver()
    ms.start.function()

    setup()  # make sure it's clear for fake.pid
    commands.log_command(pid="run/fake.pid")
    assert utils.daemonize.called
    assert ms.start.called

    # test that it exits on existing pid
    make_fake_pid_file()
    commands.log_command(pid="run/fake.pid")
    assert sys.exit.called

@patch('sys.stdin', new=Mock())
def test_sendmail_command():
    sys.stdin.read.function()

    msg = mail.MailResponse(To="tests@tester.com", From="tests@test.com",
                            Subject="Hello", Body="Test body.")
    sys.stdin.read.return_value = str(msg)
    commands.sendmail_command(port=8899)

@patch('lamson.utils.configure_database', new=Mock())
@patch('lamson.utils.import_settings', new=Mock())
def test_syncdb_command():
    commands.syncdb_command()
    commands.syncdb_command(create=True)


@patch('sys.exit', new=Mock())
@patch('lamson.utils.daemonize', new=Mock())
@patch('lamson.utils.import_settings', new=Mock())
@patch('lamson.utils.drop_priv', new=Mock())
@patch('sys.path', new=Mock())
def test_start_command():
    # normal start
    commands.start_command()
    assert utils.daemonize.called
    assert utils.import_settings.called

    # start with pid file existing already
    make_fake_pid_file()
    commands.start_command(pid="run/fake.pid")
    assert sys.exit.called

    # start with pid file existing and force given
    assert os.path.exists("run/fake.pid")
    commands.start_command(FORCE=True, pid="run/fake.pid")
    assert not os.path.exists("run/fake.pid")

    # start with a uid but no gid
    commands.start_command(uid=1000, gid=False, pid="run/fake.pid", FORCE=True)
    assert not utils.drop_priv.called

    # start with a uid/gid given that's valid
    commands.start_command(uid=1000, gid=1000, pid="run/fake.pid", FORCE=True)
    assert utils.drop_priv.called



def raise_OSError(*x, **kw):
    raise OSError('Fail')

@patch('sys.exit', new=Mock())
@patch('os.kill', new=Mock())
@patch('glob.glob', new=lambda x: ['run/fake.pid'])
def test_stop_command():
    # gave a bad pid file
    try:
        commands.stop_command(pid="run/dontexit.pid")
    except IOError:
        assert sys.exit.called

    make_fake_pid_file()
    commands.stop_command(pid="run/fake.pid")

    make_fake_pid_file()
    commands.stop_command(ALL="run")

    make_fake_pid_file()
    commands.stop_command(pid="run/fake.pid", KILL=True)
    assert os.kill.called
    assert not os.path.exists("run/fake.pid")

    make_fake_pid_file()
    os.kill.side_effect = raise_OSError
    commands.stop_command(pid="run/fake.pid", KILL=True)


@patch('glob.glob', new=lambda x: ['run/fake.pid'])
@patch('lamson.utils.daemonize', new=Mock())
@patch('lamson.utils.import_settings', new=Mock())
@patch('os.kill', new=Mock())
@patch('sys.exit', new=Mock())
@patch('sys.path', new=Mock())
def test_restart_command():
    make_fake_pid_file()
    commands.restart_command(pid="run/fake.pid")

@patch('os.chdir', new=Mock())
@patch('BaseHTTPServer.HTTPServer', new=Mock())
@patch('SimpleHTTPServer.SimpleHTTPRequestHandler', new=Mock())
def test_web_command():
    commands.web_command()
    assert os.chdir.called

