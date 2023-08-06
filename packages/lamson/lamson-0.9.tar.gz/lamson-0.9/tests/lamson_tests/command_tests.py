from nose.tools import *
import os
import shutil
from lamson.testing import spelling
from lamson import commands

def test_send_command():
    commands.send_command({'sender': 'test@test.com',
                           'to': 'test@test.com',
                           'body': 'Test body',
                           'subject': 'Test subject',
                           'file': 'setup.py',
                           'port': 8899,
                          })

def test_status_command():
    commands.status_command({})
    commands.status_command({'pid': 'run/donotexist.pid'})


def test_help_command():
    commands.help_command({})
    commands.help_command({'for': 'status'})

def test_queue_command():
    for op in  ['pop', 'count', 'clear', 'keys']:
        commands.queue_command({op: True})

def test_gen_command():
    project = 'tests/testproject'
    if os.path.exists(project):
        shutil.rmtree(project)

    commands.gen_command({'project':project})
    assert os.path.exists(project)
    shutil.rmtree(project)


def test_route_command():
    commands.routes_command({'TRAILING': ['lamson.handlers.log',
                                          'lamson.handlers.queue']})

def test_spell_command():
    if 'PYENCHANT_LIBRARY_PATH' not in os.environ:
        os.environ['PYENCHANT_LIBRARY_PATH'] = '/opt/local/lib/libenchant.dylib'

    # we have to make sure the template is spelled correctly or else the command
    # will block the nosetests since it expects input from the user
    template = "tests/lamson_tests/template.txt"
    contents = open(template).read()
    assert spelling(template, contents), "%s has to be spelled right." % template

    assert commands.spell_command({'TRAILING': ["tests/lamson_tests/template.txt"], 'language': 'en_US'})


