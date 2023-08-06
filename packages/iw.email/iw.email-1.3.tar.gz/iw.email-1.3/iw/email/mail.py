# -*- coding: utf-8 -*-
## Copyright (C) 2007 Ingeniweb - all rights reserved
## No publication or distribution without authorization.

"""
$Id: mail.py 25629 2007-06-07 00:58:39Z edegoute $
"""
__author__  = ''
__docformat__ = 'restructuredtext'

import zope.component
import zope.interface
from zope.component.factory import Factory
from iw.email import interfaces
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage
from email import quopriMIME
from email import Header
from time import strftime
from time import localtime
import types
import os

from iw.email.utils import safe_unicode


class MultipartMail(object):
    """Provide a clean way to generate an email
    """
    zope.interface.implements(interfaces.IMail)

    def __init__(self, html=None, text=None, mfrom=None, mto=None, subject=''):
        """Verify thats mfrom and mto are required::

            >>> from iw.email.mail import MultipartMail
            >>> MultipartMail(mfrom='gael@ingeniweb.com')
            Traceback (most recent call last):
            ...
            ValueError: Emails invalid: mfrom: "'gael@ingeniweb.com'", mto: "None"

            >>> MultipartMail(mto='gael@ingeniweb.com')
            Traceback (most recent call last):
            ...
            ValueError: Emails invalid: mfrom: "None", mto: "'gael@ingeniweb.com'"
        """
        if not mfrom or not mto:
            raise ValueError(
                    'Emails invalid: mfrom: "%r", mto: "%r"' % (mfrom, mto))
        if not text and not html:
            raise ValueError('You must give at least one mail content')
        self.text = text
        self.html = html
        self.mfrom = mfrom
        self.mto = mto
        self.subject = subject
        self.charset = 'iso-8859-1'
        self.in_charset = 'utf-8'
        self.contentType = 'text/html'
        self.images = []

    def addImage(self, image, filename='', content_type=''):
        """add an image
        """
        if not filename:
            if hasattr(image, 'getId'):
                filename = image.getId()
            else:
                raise RuntimeError(
                        'You must give a filename'
                        ' or an object with a getId method')
        if not content_type:
            if hasattr(image, 'getContentType'):
                content_type = image.getContentType()
            elif filename:
                x, ext = os.path.splitext(filename.lower())
                if ext in ('.jpg',):
                    content_type = 'image/jpeg'
                if ext in ('.gif', '.png'):
                    content_type = 'image/%s' % ext[1:]

        if not content_type:
            raise RuntimeError(
                    'You must give a filename'
                    ' or an object with a getContentType method')

        #get data
        if hasattr(image, 'read'):
            data = image.read()
        elif hasattr(image, 'meta_type'):
            if image.meta_type == 'Filesystem Image':
                # CMFCore.FSImage
                data = image._readFile(0)
            if image.meta_type == 'Image':
                # OFS.Image
                data = image.data
        else:
            data = image
        data = str(data)

        subtype = content_type.split('/')[1]
        image = MIMEImage(data, subtype, name=filename)
        image.add_header('Content-ID', '<%s>' % filename)
        self.images.append(image)

    def as_string(self, unixfrom=True):

        if type(self.subject) != types.UnicodeType:
            self.subject = unicode(self.subject, self.in_charset)
        subject = self.subject.encode(self.charset, 'ignore')

        alternative = MIMEMultipart('alternative', charset=self.charset)

        if self.text:
            text = safe_unicode(self.text, self.in_charset)
            text = text.encode(self.charset, 'ignore')
            email = MIMEText(text, 'plain', self.charset)
            alternative.attach(email)

        if self.html:
            html = safe_unicode(self.html, self.in_charset)
            html = html.encode(self.charset, 'ignore')
            email = MIMEText(html, 'html', self.charset)
            alternative.attach(email)

        related = MIMEMultipart('related', charset=self.charset)
        related['To'] = self.mto
        related['From'] = self.mfrom
        related['Subject'] = str(Header.Header(subject, self.charset))
        related['Date'] = strftime('%a, %d %b %Y %H:%M:%S %z', localtime())
        related['X-Mailer'] = 'iw.email'
        related.attach(alternative)

        for image in self.images:
            related.attach(image)

        return related.as_string(unixfrom=unixfrom)

    __call__ = as_string

    def __str__(self):
        return self.as_string(unixfrom=False)


MultipartMailFactory = Factory(MultipartMail, 'MultipartMail', '')

