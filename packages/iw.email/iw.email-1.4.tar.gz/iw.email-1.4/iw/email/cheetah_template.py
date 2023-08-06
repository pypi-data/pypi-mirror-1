# -*- coding: utf-8 -*-
import os
import zope.interface
from iw.email.templates import BasicMailTemplate
from iw.email.interfaces import IMailTemplate
from iw.email.mail import MultipartMail
from docutils.core import publish_parts
from Cheetah.Template import Template
from utils import safe_unicode
import types

class CheetahMailTemplate(BasicMailTemplate):
    zope.interface.implements(IMailTemplate)

    def __init__(self, path, format='rst'):
        if not os.path.isfile(path):
            raise IOError('No such file %s' % path)
        self.path = path
        self.format = format

    def cook(self, **options):
        options = self.clean_options(**options)
        options['safe_unicode'] = safe_unicode
        fd = open(self.path)
        source = safe_unicode(fd.read())
        fd.close()
        self.cooked = u'%s' % (Template(source=source,
                searchList=[options]))

def CheetahMail(path, format='rst',
                mfrom=None, mto=None, subject='', **options):
    options.update(dict(mfrom=mfrom, mto=mto, subject=subject))
    template = CheetahMailTemplate(path, format=format)
    template.cook(**options)
    html = text = None
    if format == 'plain':
        text = str(template)
    else:
        html = str(template)
    return MultipartMail(html=html, text=text,
                         mfrom=mfrom, mto=mto, subject=subject)


__all__ = ('CheetahMailTemplate', 'CheetahMail')

