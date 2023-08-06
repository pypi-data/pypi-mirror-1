from __future__ import with_statement
from nose.tools import *
import re
import os
from lamson import encoding
import mailbox
import email
from email import encoders
from email.utils import parseaddr
from mock import *
import chardet


BAD_HEADERS = [
    u'"\u8003\u53d6\u5206\u4eab" <Ernest.Beard@msa.hinet.net>'.encode('utf-8'),
    '"=?windows-1251?B?RXhxdWlzaXRlIFJlcGxpY2E=?="\n\t<wolfem@barnagreatlakes.com>',
    '=?iso-2022-jp?B?Zmlicm91c19mYXZvcmF0ZUB5YWhvby5jby5qcA==?=<fibrous_favorate@yahoo.co.jp>',

    '=?windows-1252?Q?Global_Leadership_in_HandCare_-_Consumer,\n\t_Professional_and_Industrial_Products_OTC_:_FLKI?=',
    '=?windows-1252?q?Global_Leadership_in_Handcare_-_Consumer, _Auto,\n\t_Professional_&_Industrial_Products_-_OTC_:_FLKI?=',
    'I am just normal.',
    '=?koi8-r?B?WW91ciBtYW6ScyBzdGFtaW5hIHdpbGwgY29tZSBiYWNrIHRvIHlvdSBs?=\n\t=?koi8-r?B?aWtlIGEgYm9vbWVyYW5nLg==?=',
    '=?koi8-r?B?WW91IGNhbiBiZSBvbiB0b3AgaW4gYmVkcm9vbSBhZ2FpbiCWIGp1c3Qg?=\n\t=?koi8-r?B?YXNrIHVzIGZvciBhZHZpY2Uu?=',
    '"=?koi8-r?B?5MXMz9DSz8na18/E09TXzw==?=" <daniel@specelec.com>',
    '=?utf-8?b?IumrlOiCsuWckuWNgOermSDihpIg6ZW35bqa6Yar6Zmi56uZIOKGkiDmlofljJbk?=\n =?utf-8?b?uInot6/nq5kiIDx2Z3hkcmp5Y2lAZG5zLmh0Lm5ldC50dz4=?=',
]

DECODED_HEADERS = encoding.header_from_mime_encoding(BAD_HEADERS)

NORMALIZED_HEADERS = [encoding.header_to_mime_encoding(x) for x in DECODED_HEADERS]


def test_MailBase():
    the_subject = u'p\xf6stal'
    m = encoding.MailBase()
    
    m['To'] = "testing@test.com"
    m['Subject'] = the_subject

    assert m['To'] == "testing@test.com"
    assert m['TO'] == m['To']
    assert m['to'] == m['To']

    assert m['Subject'] == the_subject
    assert m['subject'] == m['Subject']
    assert m['sUbjeCt'] == m['Subject']
    
    msg = encoding.to_message(m)
    m2 = encoding.from_message(msg)

    assert_equal(len(m), len(m2) - 1)

    for k in m:
        assert m[k] == m2[k], "%s: %r != %r" % (k, m[k], m2[k])
    
    for k in m.keys():
        assert k in m
        del m[k]
        assert not k in m

def test_header_to_mime_encoding():
    for i, header in enumerate(DECODED_HEADERS):
        assert_equal(NORMALIZED_HEADERS[i], encoding.header_to_mime_encoding(header))
        

def test_header_from_mime_encoding():
    assert not encoding.header_from_mime_encoding(None)
    assert_equal(len(BAD_HEADERS), len(encoding.header_from_mime_encoding(BAD_HEADERS)))
    
    for i, header in enumerate(BAD_HEADERS):
        assert_equal(DECODED_HEADERS[i], encoding.header_from_mime_encoding(header))


def test_to_message_from_message_with_spam():
    mb = mailbox.mbox("tests/spam")
    fails = 0
    total = 0

    for msg in mb:
        try:
            m = encoding.from_message(msg)
            out = encoding.to_message(m)
            m2 = encoding.from_message(out)

            for k in m:
                if '@' in m[k]:
                    assert_equal(parseaddr(m[k]), parseaddr(m2[k]))
                else:
                    assert m[k].strip() == m2[k].strip(), "%s: %r != %r" % (k, m[k], m2[k])

                assert not m[k].startswith(u"=?")
                assert not m2[k].startswith(u"=?")
                assert m.body == m2.body, "Bodies don't match."
                assert_equal(len(m.parts), len(m2.parts), "Not the same number of parts.")
                for i, part in enumerate(m.parts):
                    assert part.body == m2.parts[i].body, "Part %d isn't the same: %r \nvs\n. %r" % (i, part.body, m2.parts[i].body)
            total += 1
        except encoding.EncodingError, exc:
            fails += 1

    assert fails/total < 0.01, "There were %d failures out of %d total." % (fails, total)


def test_to_file_from_file():
    mb = mailbox.mbox("tests/spam")
    msg = encoding.from_message(mb[0])

    outfile = "run/encoding_test.msg"

    with open(outfile, 'w') as outfp:
        encoding.to_file(msg, outfp)

    with open(outfile) as outfp:
        msg2 = encoding.from_file(outfp)
    
    outdata = open(outfile).read()

    assert_equal(len(msg), len(msg2) - 1)
    os.unlink(outfile)


def test_guess_encoding_and_decode():
    for header in DECODED_HEADERS:
        try:
            encoding.guess_encoding_and_decode('ascii', header.encode('utf-8'))
        except encoding.EncodingError:
            pass


def test_attempt_decoding():
    for header in DECODED_HEADERS:
        encoding.attempt_decoding('ascii', header.encode('utf-8'))


def test_parse_charset_header():
    for i, header in enumerate(BAD_HEADERS):
        if header.startswith("=?"):
            parsed = encoding.parse_charset_header(header)
            assert_equal(DECODED_HEADERS[i], parsed)

    wrong_encoding = '=?iso-2022-jp?X?Zmlicm91c19mYXZvcmF0ZUB5YWhvby5jby5qcA==?=<fibrous_favorate@yahoo.co.jp>'
    assert_raises(encoding.EncodingError, encoding.parse_charset_header, wrong_encoding)


def test_properly_decode_header():
    for i, header in enumerate(BAD_HEADERS):
        parsed = encoding.parse_charset_header(header)
        assert_equal(DECODED_HEADERS[i], parsed)


def test_headers_round_trip():
    # round trip the headers to make sure they convert reliably back and forth
    for header in BAD_HEADERS:
        original = encoding.header_from_mime_encoding(header)

        assert original
        assert "=?" not in original and "?=" not in original, "Didn't decode."

        encoded = encoding.header_to_mime_encoding(original)
        assert encoded

        return_original = encoding.header_from_mime_encoding(encoded)
        assert_equal(original, return_original)

        return_encoded = encoding.header_to_mime_encoding(return_original)
        assert_equal(encoded, return_encoded)


def test_MIMEPart():
    text1 = encoding.MIMEPart("text/plain")
    text1.set_payload("The first payload.")
    text2 = encoding.MIMEPart("text/plain")
    text2.set_payload("The second payload.")

    image_data = open("tests/lamson.png").read()
    img1 = encoding.MIMEPart("image/png")
    img1.set_payload(image_data)
    img1.set_param('attachment','', header='Content-Disposition')
    img1.set_param('filename','lamson.png', header='Content-Disposition')
    encoders.encode_base64(img1)
    
    multi = encoding.MIMEPart("multipart/mixed")
    for x in [text1, text2, img1]:
        multi.attach(x)

    mail = encoding.from_message(multi)

    assert mail.parts[0].body == "The first payload."
    assert mail.parts[1].body == "The second payload."
    assert mail.parts[2].body == image_data

    encoding.to_message(mail)


@patch('chardet.detect', new=Mock())
@raises(encoding.EncodingError)
def test_guess_encoding_fails_completely():
    chardet.detect.return_value = {'encoding': None, 'confidence': 0.0}
    encoding.guess_encoding_and_decode('ascii', 'some data', errors='strict')


def test_attach_text():
    mail = encoding.MailBase()
    mail.attach_text("This is some text.", 'text/plain')

    msg = encoding.to_message(mail)
    assert msg.get_payload(0).get_payload() == "This is some text."
    assert encoding.to_string(mail)

    mail.attach_text("<html><body><p>Hi there.</p></body></html>", "text/html")
    msg = encoding.to_message(mail)
    assert len(msg.get_payload()) == 2
    assert encoding.to_string(mail)


def test_attach_file():
    mail = encoding.MailBase()
    png = open("tests/lamson.png").read()
    mail.attach_file("lamson.png", png, "image/png", "attachment")
    msg = encoding.to_message(mail)

    payload = msg.get_payload(0)
    assert payload.get_payload(decode=True) == png
    assert payload.get_filename() == "lamson.png", payload.get_filename()


