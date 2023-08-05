# -*- coding: utf-8 -*-
## Copyright (C) 2007 Ingeniweb - all rights reserved
## No publication or distribution without authorization.

"""
$Id: mail.py 25629 2007-06-07 00:58:39Z edegoute $
"""
__author__  = ''
__docformat__ = 'restructuredtext'

import zope.component
from zope.component.factory import Factory
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage
from email import quopriMIME
from email import Header
from time import strftime
from time import localtime
import types

from utils import safe_unicode


class MultipartMail(object):
    """Provide a clean way to generate an email

    """

    def __init__(self, html=None, text=None, mfrom=None, mto=None, subject=''):
        if not mfrom or not mto:
            raise ValueError('Emails invalid: %s %s' % (mfrom, mto))
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
        """
        """
        if not filename:
            if hasattr(image, 'getId'):
                filename = image.getId()
            else:
                raise RuntimeError('You must give a filename or an object with a getId method')
        if not content_type:
            if hasattr(image, 'getContentType'):
                content_type = image.getContentType()
                raise RuntimeError('You must give a filename or an object with a getContentType method')

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
        #image.add_header('Content-Disposition', 'attachment; filename="%s"' % name)
        self.images.append(image)

    def __str__(self):

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

        return related.as_string(unixfrom=False)

    __call__ = __str__

MultipartMailFactory = Factory(MultipartMail, 'MultipartMail', '')

