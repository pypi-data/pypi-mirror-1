from nose.tools import *
from lamson.testing import *
from lamson.mail import MailRequest, MailResponse
from app.model import archive, mailinglist
from config import settings
from lamson import encoding

def setup():
    clear_queue(archive.queue_path('test.list'))

def teardown():
    clear_queue(archive.queue_path('test.list'))

def test_archive_enqueue():
    fake = MailResponse(From="zedshaw@zedshaw.com", To="test.list@librelist.com",
                       Subject="test message", Body="This is a test.")

    msg = MailRequest('fakepeer', fake['From'], fake['To'], str(fake))

    archive.enqueue('test.list', msg)
    assert delivered('zedshaw', to_queue=queue(archive.queue_path('test.list')))


def test_white_list_cleanse():
    msg = MailRequest('fakepeer', None, None, open('tests/lots_of_headers.msg').read())
    resp = mailinglist.craft_response(msg, 'test.list@librelist.com')

    archive.white_list_cleanse(resp)
    
    for key in resp.msg.keys():
        assert key in archive.ALLOWED_HEADERS

    assert '@' not in resp['from']
    assert str(resp)

