from nose.tools import *
from lamson.testing import *
from lamson import view
import os


def test_spelling():
    message = {}
    original = {}
    for template in ['confirm.msg','page_ready.msg', 'welcome.msg']:
        result = view.render(template, locals())
        assert spelling(template, result), "%s is spelled wrong" % template


