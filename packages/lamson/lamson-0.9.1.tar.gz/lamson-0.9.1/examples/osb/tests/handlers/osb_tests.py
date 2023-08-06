from nose.tools import *
from lamson.testing import *
import os
import time
import shutil

relay = relay(port=8823)
sender = "sender-%s@sender.com" % time.time()
host = "test.com"
blog_id = int(time.time())
blog_address = "test.blog.%d@osb.%s" % (blog_id, host)

# This line uses only internal routing code to simulate delivery of the mail.
client = RouterConversation(sender, "Blog testing.")

# Change to this line and the exact same tests will actually connect to a
# running lamson application server and deliver emails to test it.
#
# client = TestConversation(relay, sender, "Blog testing.")

def setup():
    shutil.rmtree("app/data/posts")
    os.mkdir("app/data/posts")

def test_START():
    client.begin()
    client.say(blog_address, "I'd like a blog thanks.", 'confirm')
    assert queue().count() == 1, "Should get one message."

def test_NEW_USER():
    qid, msg = queue().pop()
    assert msg, "No message to test with."

    client.begin()
    client.say(msg['Reply-To'], 'Confirmed I am.', 'noreply')

def test_POSTING_post():
    qid, msg = queue().pop()
    assert msg, "Should have a message in the queue from NEW_USER"

    client.begin()
    client.say(blog_address, "This is my new page.", "noreply")

    expected_file = "app/data/posts/%s/%s.html" % (sender, 'test.blog.%s' % blog_id)
    assert os.path.exists(expected_file), "Should get an html."

def test_POSTING_delete():
    expected_file = "app/data/posts/%s/%s.html" % (sender, 'test.blog.%s' % blog_id)

    blog_delete = "test.blog.%s-delete@osb.%s" % (blog_id, host)
    client.say(blog_delete, "Please delete.", "noreply")

    assert not os.path.exists(expected_file), "File should be gone."

def test_INDEXER():
    expected_file = "app/data/posts/index.html"


