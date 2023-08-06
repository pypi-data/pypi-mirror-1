from nose.tools import *
from lamson import utils, view


def test_make_fake_settings():
    settings = utils.make_fake_settings('localhost', 8800)
    assert settings
    assert settings.receiver
    assert settings.relay == None
    settings.receiver.close()

def test_import_settings():
    loader = view.LOADER

    settings = utils.import_settings(True, from_dir='tests', boot_module='config.testing')
    assert settings
    assert settings.receiver_config

    view.LOADER = loader
    settings = utils.import_settings(False, from_dir='examples/osb')
    assert settings
    assert settings.receiver_config



def test_daemonize_not_fully():
    context = utils.daemonize("run/tests.pid", ".", False, False, do_open=False)
    context = utils.daemonize("run/tests.pid", ".", "/tmp", 0002, do_open=False)
    assert context
