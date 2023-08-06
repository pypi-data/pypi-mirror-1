# -*- coding: utf-8 -*-
import os
import sys
import smtplib
import unittest
from cStringIO import StringIO
from webtest import TestResponse

TEST_MAIL = None

if os.environ.has_key('TEST_MAIL'):
    TEST_MAIL = os.getenv('TEST_MAIL')

TEST_MAILFROM = os.getenv('TEST_MAILFROM', 'test@ingeniweb.com')
TEST_MAILHOST = os.getenv('TEST_MAILHOST', 'localhost')
TEST_MAILPORT = os.getenv('TEST_MAILPORT', 25)

try:
    from zope.sendmail.interfaces import IMailDelivery
except ImportError:
    pass
else:
    import zope.interface
    class TestMailDelivery(object):
        zope.interface.implements(IMailDelivery)
        def send(self, mfrom, mto, messageText):
            smtplib.SMTP().sendmail(mfrom, mto, str(messageText))
            return 'fake-message-id@example.com'

def smtpSetUp(*args, **kwargs):
    if TEST_MAIL:
        server = smtplib.SMTP(TEST_MAILHOST, int(TEST_MAILPORT))

    fd = kwargs.get('fd', None)

    smtplib.SMTP._old___init__ = smtplib.SMTP.__init__
    smtplib.SMTP._old_sendmail = smtplib.SMTP.sendmail
    smtplib.SMTP._old_close = smtplib.SMTP.close

    def __init__(self, *args, **kwargs):
        """patch __init__"""
    smtplib.SMTP.__init__ = __init__

    def sendmail(self, mfrom, mto, message):
        """patche sendmail"""
        if TEST_MAIL:
            server._old_sendmail(TEST_MAILFROM, TEST_MAIL, str(message))
        if 'fd' in kwargs and callable(fd):
            print >> fd(), message
        else:
            print message
    smtplib.SMTP.sendmail = sendmail

    def close(self):
        """do nothing
        """
    smtplib.SMTP.close = close

def smtpTearDown(*args):
    smtplib.SMTP.__init__ = smtplib.SMTP._old___init__
    smtplib.SMTP.sendmail = smtplib.SMTP._old_sendmail
    smtplib.SMTP.close = smtplib.SMTP._old_close


class EmailTestCase(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)
        self.setUpEmail()

    def setUpEmail(self):
        self._mail_output = []
        smtpSetUp(fd=self.reset_mail_output)

    def reset_mail_output(self):
        fd = StringIO()
        self._mail_output.append(fd)
        return fd

    def mail_output(self):
        output = ''
        for fd in self._mail_output:
            fd.seek(0)
            output += fd.read()
        if not output:
            raise AssertionError('No mail content')
        self._mail_output = []
        mail = TestResponse()
        mail.content_type = 'text/plain'
        mail.body = output
        return mail

    def tearDownEmail(self):
        smtpTearDown()

    def tearDown(self):
        unittest.TestCase.tearDown(self)
        self.tearDownEmail()
