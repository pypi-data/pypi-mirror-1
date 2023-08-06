from lamson import queue
from config import settings
from datetime import datetime
import os
import shutil

ALLOWED_HEADERS = set([
 "From", "In-Reply-To", "List-Id",
 "Precedence", "References", "Reply-To",
 "Return-Path", "Sender",
 "Subject", "To", "Message-Id",
 "Date",
])


def day_of_year_path():
    return "%d/%0.2d/%0.2d" % datetime.today().timetuple()[0:3]

def queue_path(list_name):
    datedir = os.path.join(settings.ARCHIVE_BASE, list_name, day_of_year_path())

    if not os.path.exists(datedir):
        os.makedirs(datedir)

    return os.path.join(datedir, 'queue')

def enqueue(list_name, message):
    qpath = queue_path(list_name)
    pending = queue.Queue(qpath, safe=True)

    white_list_cleanse(message)

    pending.push(message)


def white_list_cleanse(message):
    for key in message.msg.keys():
        if key not in ALLOWED_HEADERS:
            del message[key]

    message['from'] = message['from'].replace(u'@',u'-AT-')
    

