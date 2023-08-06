from nose.tools import *
from lamson import utils, view


def test_make_fake_settings():
    settings = utils.make_fake_settings('localhost', 8800)
    assert settings
    assert settings.receiver
    assert settings.relay == None
    assert settings.database == None
    assert settings.log_file
    settings.receiver.close()

def test_import_settings():
    loader = view.LOADER

    settings = utils.import_settings(True, from_dir='tests', boot_module='config.testing')
    assert settings
    assert settings.receiver_config
    assert settings.database_config
    assert settings.log_file

    view.LOADER = loader
    settings = utils.import_settings(False, from_dir='examples/osb')
    assert settings
    assert settings.receiver_config
    assert settings.database_config
    assert settings.log_file


def test_configure_database():
    settings = utils.import_settings(False, from_dir='examples/osb')
    assert settings

    db = utils.configure_database(settings.database_config, also_create=False)

    # without settings
    db = utils.configure_database(None, also_create=False)


def test_daemonize_not_fully():
    context = utils.daemonize("run/tests.pid", ".", False, False, do_open=False)
    context = utils.daemonize("run/tests.pid", ".", "/tmp", 0002, do_open=False)
    assert context
