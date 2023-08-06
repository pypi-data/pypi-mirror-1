"""
These are helper functions that make it easier to work with either
Jinja2 or Mako templates.  You MUST configure it by setting
lamson.view.LOADER to one of the template loaders in your config.boot
or config.testing.

After that these functions should just work.
"""

from lamson import mail
import email

LOADER = None

def load(template):
    """
    Uses the registered loader to load the template you ask for.
    It assumes that your loader works like Jinja2 or Mako in that
    it has a LOADER.get_template() method that returns the template.
    """
    assert LOADER, "You haven't set lamson.view.LOADER to a loader yet."
    return LOADER.get_template(template)

def render(template, variables):
    """
    Takes the variables given and renders the template for you.
    Assumes the template returned by load() will have a .render()
    method that takes the variables as a dict.

    Use this if you just want to render a single template and don't
    want it to be a message.  Use render_message if the contents
    of the template are to be interpreted as a message with headers
    and a body.
    """
    return load(template).render(variables)

def respond(template, variables, html=False):
    """
    Returns a lamson.mail.MailResponse object that is the result
    of rendering the given template with the variables, parsing the
    results as an email message, and then setting the body
    as either the Body of the MailResponse or Html of the 
    MailResponse, depending on how html is set.

    WARNING: The template is encoded into 'ascii' for
    email.message_from_string() to work properly in Python 2.6.
    """

    results = render(template, variables)

    data = email.message_from_string(results.encode('ascii', 'replace'))

    if html:
        msg = mail.MailResponse(Html=data.get_payload())
    else:
        msg = mail.MailResponse(Body=data.get_payload())

    msg.update(data)

    return msg


