# -*- coding: utf-8 -*-
import os, smtplib

TEST_MAIL = None

if os.environ.has_key('TEST_MAIL'):
    TEST_MAIL = os.getenv('TEST_MAIL')
    TEST_MAILFROM = os.getenv('TEST_MAILFROM', 'test@ingeniweb.com')
    TEST_MAILHOST = os.getenv('TEST_MAILHOST', 'localhost')
    TEST_MAILPORT = os.getenv('TEST_MAILPORT', 25)
    server = smtplib.SMTP(TEST_MAILHOST, int(TEST_MAILPORT))


class SMTP(object):

    def __init__(self, *args, **kwargs):
        pass

    def sendmail(self, mfrom, mto, message):
        if TEST_MAIL:
            server.sendmail(TEST_MAILFROM, TEST_MAIL, str(message))
        print message

