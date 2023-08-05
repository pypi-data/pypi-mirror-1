# -*- coding: utf-8 -*-
import os, smtplib

TEST_MAIL = None

if os.environ.has_key('TEST_MAIL'):
    TEST_MAIL = os.getenv('TEST_MAIL')

TEST_MAILFROM = os.getenv('TEST_MAILFROM', 'test@ingeniweb.com')
TEST_MAILHOST = os.getenv('TEST_MAILHOST', 'localhost')
TEST_MAILPORT = os.getenv('TEST_MAILPORT', 25)

def smtpSetUp(test):
    smtplib.SMTP._old___init__ = smtplib.SMTP.__init__
    smtplib.SMTP._old_sendmail = smtplib.SMTP.sendmail

    def __init__(self, *args, **kwargs):
        if TEST_MAIL:
            smtplib.SMTP._old___init__(self, TEST_MAILHOST, int(TEST_MAILPORT))
    smtplib.SMTP.__init__ = __init__

    def sendmail(self, mfrom, mto, message):
        if TEST_MAIL:
            smtplib.SMTP._old_sendmail(self, TEST_MAILFROM, TEST_MAIL, str(message))
        print message
    smtplib.SMTP.sendmail = sendmail

def smtpTearDown(self):
    smtplib.SMTP.__init__ = smtplib.SMTP._old___init__
    smtplib.SMTP.sendmail = smtplib.SMTP._old_sendmail

