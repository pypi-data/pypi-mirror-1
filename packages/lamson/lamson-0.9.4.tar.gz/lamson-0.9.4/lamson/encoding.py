"""
Lamson takes the policy that email it receives is most likely complete garbage 
using bizarre pre-Unicode formats that are irrelevant and unnecessary in today's
modern world.  These emails must be cleansed of their unholy stench of
randomness and turned into something nice and clean that a regular Python
programmer can work with:  unicode.

That's the receiving end, but on the sending end Lamson wants to make the world
better by not increasing the suffering.  To that end, Lamson will canonicalize
all email it sends to be ascii or utf-8 (whichever is simpler and works to
encode the data).  When you get an email from Lamson, it is a pristine easily
parseable clean unit of goodness you can count on.

To accomplish these tasks, Lamson goes back to basics and assert a few simple
rules on each email it receives:

1) NO ENCODING IS TRUSTED, NO LANGUAGE IS SACRED, ALL ARE SUSPECT.
2) Python wants Unicode, it will get Unicode.
3) Any email that CANNOT become Unicode, CANNOT be processed by Lamson or
Python.
4) Email addresses are ESSENTIAL to Lamson's routing and security, and therefore
will be canonicalized and properly encoded.
5) Lamson will therefore try to "upgrade" all email it receives to Unicode
internally, and cleaning all email addresses.
6) It does this by decoding all codecs, and if the codec LIES, then it will
attempt to statistically detect the codec using chardet.
7) If it can't detect the codec, and the codec lies, then the email is bad.
8) All text bodies and attachments are then converted to Python unicode in the
same way as the headers.
9) All other attachments are converted to raw strings as-is.

Once Lamson has done this, your Python handler can now assume that all
MailRequest objects are happily unicode enabled and ready to go.  The rule is:

    IF IT CANNOT BE UNICODE, THEN PYTHON CANNOT WORK WITH IT.

On the outgoing end (when you send a MailResponse), Lamson tries to create the
email it wants to receive by canonicalizing it:

1) All email will be encoded in the simplest cleanest way possible without
losing information.
2) All headers are converted to 'ascii', and if that doesn't work, then 'utf-8'.
3) All text/* attachments and bodies are converted to ascii, and if that doesn't
work, 'utf-8'.
4) All other attachments are left alone.
5) All email addresses are normalized and encoded if they have not been already.

The end result is an email that has the highest probability of not containing
any obfuscation techniques, hidden characters, bad characters, improper
formatting, invalid non-characterset headers, or any of the other billions of
things email clients do to the world.  The output rule of Lamson is:

    ALL EMAIL IS ASCII FIRST, THEN UTF-8, AND IF CANNOT BE EITHER THOSE IT WILL
    NOT BE SENT.

Following these simple rules, this module does the work of converting email
to the canonical format and sending the canonical format.  The code is 
probably the most complex part of Lamson since the job it does is difficult.

Test results show that Lamson can safely canonicalize most email from any
culture (not just English) to the canonical form, and that if it can't then the
email is not formatted right and/or spam.

If you find an instance where this is not the case, then submit it to the
project as a test case.
"""

import string
from email.charset import Charset
import chardet
import re
import email
from email import encoders
from email.mime.base import MIMEBase
from email.utils import parseaddr


DEFAULT_ENCODING = "utf-8"
DEFAULT_ERROR_HANDLING = "strict"
CONTENT_ENCODING_KEYS = set(['Content-Type', 'Content-Transfer-Encoding', 'Content-Disposition'])

S_ENCODING = lambda x, token: ['E', token.split("?")[0:-1]] 
S_DATA = lambda x, token: ['D', token[0:-2]]
S_SPACE = lambda x, token: ['S', token]
S_EMAIL_ADDR = lambda x, token: ['M', token]
S_LITERAL = lambda x, token: ['L', token]

EMAIL_REGEX_PATTERN = r"<?[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}>?"

SCANNER = re.Scanner([
    (r"=\?", None),
    (r"\?=", None),
    (r"\n\s+", S_SPACE),
    (r'"', S_LITERAL),
    (r"([a-z0-9\-]+)?\?([qb])\?", S_ENCODING),
    (EMAIL_REGEX_PATTERN, S_EMAIL_ADDR),
    (r"(.|[\n\r\s])*?\?=", S_DATA),
], re.IGNORECASE)


class EncodingError(Exception): 
    """Thrown when there is an encoding error."""
    pass


class MailBase(object):
    """MailBase is used as the basis of lamson.mail and contains the basics of
    encoding an email.  You actually can do all your email processing with this
    class, but it's more raw.
    """
    def __init__(self, items=()):
        self.headers = dict(items)
        self.parts = []
        self.body = None
        self.content_encoding = {'Content-Type': (None, {}), 
                                 'Content-Disposition': (None, {}),
                                 'Content-Transfer-Encoding': (None, {})}

    def __getitem__(self, key):
        return self.headers.get(normalize_header(key), None)

    def __len__(self):
        return len(self.headers)

    def __iter__(self):
        return iter(self.headers)

    def __contains__(self, key):
        return normalize_header(key) in self.headers

    def __setitem__(self, key, value):
        self.headers[normalize_header(key)] = value

    def __delitem__(self, key):
        del self.headers[normalize_header(key)]

    def keys(self):
        return self.headers.keys()

    def attach_file(self, filename, data, ctype, disposition):
        """
        A file attachment is a raw attachment with a disposition that
        indicates the file name.
        """
        part = MailBase()
        part.body = data
        part.content_encoding['Content-Type'] = (ctype, {})
        part.content_encoding['Content-Disposition'] = (disposition,
                                                        {'filename': filename})
        self.parts.append(part)


    def attach_text(self, data, ctype):
        """
        This attaches a simpler text encoded part, which doesn't have a
        filename.
        """
        part = MailBase()
        part.body = data
        part.content_encoding['Content-Type'] = (ctype, {})
        self.parts.append(part)



class MIMEPart(MIMEBase):
    """
    A reimplementation of nearly everything in email.mime to be more useful
    for actually attaching things.  Rather than one class for every type of
    thing you'd encode, there's just this one, and it figures out how to
    encode what you ask it.
    """
    def __init__(self, type, **params):
        self.maintype, self.subtype = type.split('/')
        MIMEBase.__init__(self, self.maintype, self.subtype, **params)

    def add_text(self, content):
        # this is text, so encode it in canonical form
        try:
            encoded = content.encode('ascii')
            charset = 'ascii'
        except UnicodeError:
            encoded = content.encode('utf-8')
            charset = 'utf-8'

        self.set_payload(encoded, charset=charset)


    def extract_payload(self, mail):
        if mail.body == None: return  # only None, '' is still ok

        ctype, _ = mail.content_encoding['Content-Type']
        cdisp, cdisp_params = mail.content_encoding['Content-Disposition']

        assert ctype, "Extract payload requires that mail.content_encoding have a valid Content-Type."

        if ctype.startswith("text/"):
            self.add_text(mail.body)
        else:
            # it's something we shouldn't touch, so replicate
            self.add_header('Content-Type', ctype)

            if cdisp:
                # replicate the content-disposition settings
                self.add_header('Content-Disposition', cdisp, **cdisp_params)

            self.set_payload(mail.body)
            encoders.encode_base64(self)


def from_message(message):
    """
    Given a MIMEBase or similar Python email API message object, this
    will canonicalize it and give you back a pristine MailBase.
    If it can't then it raises a EncodingError.
    """
    mail = MailBase()

    # parse the content information out of message
    for k in CONTENT_ENCODING_KEYS:
        params = parse_parameter_header(message, k)
        mail.content_encoding[k] = params

    # copy over any keys that are not part of the content information
    for k in message.keys():
        if normalize_header(k) not in mail.content_encoding:
            mail[k] = header_from_mime_encoding(message[k])
  
    # if this isn't a multi-part message, then process the payload into a
    # normalized body that can be used
    if not message.is_multipart():
        decode_message_body(mail, message)
    else:
        # recursively go through each subpart and decode in the same way
        for msg in message.get_payload():
            if msg != message:  # skip the multipart message itself
                mail.parts.append(from_message(msg))

    return mail



def to_message(mail):
    """
    Given a MailBase message, this will construct a MIMEPart 
    that is canonicalized for use with the Python email API.
    """
    ctype, _ = mail.content_encoding['Content-Type']

    if not ctype:
        if mail.parts:
            ctype = 'multipart/mixed'
        else:
            ctype = 'text/plain'

    mail.content_encoding['Content-Type'] = (ctype, {})

    out = MIMEPart(ctype)

    for k, v in mail.headers.items():
        out[k.encode('ascii')] = header_to_mime_encoding(v)

    # now we have recursive payloads, and each has its original content_encoding
    # information, we need to re-encode each payload
    if len(mail.parts) == 0:
        # just set this one payload to the out message and return
        out.extract_payload(mail)
    else:
        assert mail.body is None, "You have parts and a body in your mail.  Do one or the other."
        for part in mail.parts:
            out.attach(to_message(part))

    return out


def to_string(mail):
    """Returns a canonicalized email string you can use to send or store
    somewhere."""
    return str(to_message(mail))


def from_string(data):
    """Takes a string, and tries to clean it up into a clean MailBase."""
    return from_message(email.message_from_string(data))

def to_file(mail, fileobj):
    """Writes a canonicalized message to the given file."""
    fileobj.write(to_string(mail))

def from_file(fileobj):
    """Reads an email and cleans it up to make a MailBase."""
    return from_message(email.message_from_file(fileobj))


def normalize_header(header):
    return string.capwords(header, '-')


def parse_parameter_header(message, header):
    params = message.get_params(header=header)
    if params:
        value = params.pop(0)[0]
        return value, dict(params)
    else:
        return None, {}

def decode_message_body(mail, message):
    mail.body = message.get_payload(decode=True)
    if mail.body:
        # decode the payload according to the charset given if it's text
        ctype, params = mail.content_encoding['Content-Type']

        if not ctype:
            charset = 'ascii'
            mail.body = attempt_decoding(charset, mail.body)
        elif ctype.startswith("text/"):
            charset = params.get('charset', 'ascii')
            mail.body = attempt_decoding(charset, mail.body)
        else:
            # it's a binary codec of some kind, so just decode and leave it
            # alone for now
            pass



def header_to_mime_encoding(value):
    encoder = Charset(DEFAULT_ENCODING)
    try:
        return value.encode("ascii")
    except UnicodeEncodeError:
        if '@' in value:
            # this could have an email address, make sure we don't screw it up
            name, address = parseaddr(value)
            return '"%s" <%s>' % (encoder.header_encode(name.encode("utf-8")), address)

        return encoder.header_encode(value.encode("utf-8"))


def header_from_mime_encoding(header):
    if header is None: 
        return header
    elif type(header) == list:
        return [properly_decode_header(h) for h in header]
    else:
        return properly_decode_header(header)




def guess_encoding_and_decode(original, data, errors=DEFAULT_ERROR_HANDLING):
    try:
        charset = chardet.detect(str(data))

        if not charset['encoding']:
            raise EncodingError("Header claimed %r charset, but detection found none.  Decoding failed." % original)

        return data.decode(charset["encoding"], errors)
    except UnicodeError, exc:
        raise EncodingError("Header lied and claimed %r charset, guessing said "
                            "%r charset, neither worked so this is a bad email: "
                            "%s." % (original, charset, exc))


def attempt_decoding(charset, dec):
    try:
        if isinstance(dec, unicode):
            # it's already unicode so just return it
            return dec
        else:
            return dec.decode(charset)
    except UnicodeError:
        # looks like the charset lies, try to detect it
        return guess_encoding_and_decode(charset, dec)
    except LookupError:
        # they gave a crap encoding
        return guess_encoding_and_decode(charset, dec)


def apply_charset_to_header(charset, encoding, data):
    if encoding == 'b' or encoding == 'B':
        dec = email.base64mime.decode(data.encode('ascii'))
    elif encoding == 'q' or encoding == 'Q':
        dec = email.quoprimime.header_decode(data.encode('ascii'))
    else:
        raise EncodingError("Invalid header encoding %r should be 'Q' or 'B'." % encoding)

    return attempt_decoding(charset, dec)




def parse_charset_header(header):
    tokens, remainder = SCANNER.scan(header)

    results = []
    encoding = None
    charset = None
    current = []

    for i, toks in enumerate(tokens):
        ttype, token = toks

        if ttype == 'E':
            charset, encoding = token
        elif ttype == 'D':
            # the next one being a space boundary means we have to rebuild the
            # multiline header, so just append
            if i+1 < len(tokens) and tokens[i+1][0] == 'S':
                current.append(token)
            else:
                current.append(token)
                dec = apply_charset_to_header(charset, encoding, "".join(current))
                del current[:]  # clear it out for the next one
                results.append(dec)
        elif ttype == 'M':
            results.append(token)
        elif ttype == 'S':
            pass  # these are just skipped over and handled the 'D' branch above
        elif ttype == 'L':
            results.append(token) # literal tokens we need to maintain
        else:
            raise EncodingError("Invalid token type %r.", ttype)

    if remainder:
        remainder = attempt_decoding(charset or 'ascii', remainder)

    return "".join(results) + remainder


def properly_decode_header(header):
    if header.startswith("=?") or header.startswith('"=?'):
        return parse_charset_header(header)
    else:
        return attempt_decoding('ascii', header) 



