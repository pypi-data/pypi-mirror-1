from nose.tools import *
from lamson import view
import jinja2

view.LOADER = jinja2.Environment(loader=jinja2.PackageLoader('lamson_tests', '.'))

def test_load():
    template = view.load("template.txt")
    assert template
    assert template.render()

def test_render():
    # try with some empty vars
    text = view.render("template.txt", {})
    assert text

def test_respond_locals():
    From = "test@test.com"
    To = "receiver@test.com"
    Subject = "Test with locals."
    dude = 'Tester'

    msg = view.respond("template.txt", locals())
    assert msg['From'] == From
    assert msg['To'] == To
    assert msg['Subject'] == Subject
    assert msg.Body.strip() == "Hey there %s I like your shirt." % dude, msg.Body


def test_respond_dict():
    vars = {
        "From": "test@test.com",
        "To": "receiver@test.com",
        "Subject": "Test with locals.",
        "dude": 'Tester',
    }

    msg = view.respond("template.txt", vars)
    del vars['dude']  # don't need this for the asserts

    for key in vars:
        assert key in msg, "Key in template %s not in message." % key
        assert vars[key] == msg[key], "Key %s don't match." % key

    assert msg.Body.strip() == "Hey there Tester I like your shirt.",  msg.Body

def test_respond_html():
    From = "test@test.com"
    To = "receiver@test.com"
    Subject = "Test with locals."
    dude = 'Tester'

    msg = view.respond("template.txt", locals(), html=True)
    assert msg.Html
