from nose.tools import *
from lamson import utils


def test_make_fake_settings():
    options = {
        'host': 'localhost',
        'port': 8800,
        'debug': 1
    }

    settings = utils.make_fake_settings(options)
    assert settings
    assert settings.receiver
    assert settings.relay == None
    assert settings.database == None
    assert settings.log_file
    settings.receiver.close()

def test_import_settings():
    settings = utils.import_settings(False, from_dir='examples/osb')
    assert settings
    assert settings.receiver_config
    assert settings.database_config
    assert settings.log_file

def test_configure_database():
    settings = utils.import_settings(False, from_dir='examples/osb')
    assert settings
    db = utils.configure_database(settings.database_config, also_create=False)


