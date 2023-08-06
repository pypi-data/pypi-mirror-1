# -*- encoding: utf-8 -*-

import logging
import os
import smtplib
import socket
import sys
import traceback
from email.mime.text import MIMEText
log = logging.getLogger(__name__)

class MissingServer(Exception):
    """Server could not be connected or something more sinister. Can
    be chained to the current traceback if requested politely."""

    def __init__(self, host, exc=True):
        self.host  = host
        self.error = ''
        if exc:
            self.error = traceback.format_exc()

    def __str__(self):
        return self.error

def message(msg):
    """Constructs a message to one person, given the Unicode message
    body. Returns a :class:`email.mime.text.MIMEText` object. Client
    needs to set additional headers: To, From, Subject."""

    assert isinstance(msg, unicode)

    # Use ASCII if possible, otherwise UTF-8. This is done to avoid
    # base64, which is ugly and not human-readable.
    charset = 'utf8'
    try:
        msg.encode('ascii')
        charset = 'ascii'
    except:
        pass

    msg = MIMEText(msg.encode(charset), _charset=charset)
    return msg

def send(msg, host, port):
    """Sends a :class:`email.mime.text.MIMEText` object on localhost's
    SMTP server."""

    try:
        s = smtplib.SMTP(host, port)
        s.sendmail(msg['From'], msg['To'], msg.as_string())
        s.quit()
    except (smtplib.SMTPServerDisconnected, socket.error), e:
        raise MissingServer(host, True)
