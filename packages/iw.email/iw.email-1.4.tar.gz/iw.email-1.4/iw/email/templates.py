# -*- coding: utf-8 -*-
import os
from docutils.core import publish_parts
import zope.interface
from iw.email.interfaces import IMailTemplate
from utils import safe_unicode
import types


class BasicMailTemplate(object):
    zope.interface.implements(IMailTemplate)

    def __init__(self, source, format='plain'):
        self.template = source
        self.format = format

    def clean_options(self, **options):
        return safe_unicode(options)

    def cook(self, **options):
        options = self.clean_options(**options)
        template = safe_unicode(self.template)
        self.cooked = self.template % options

    def __str__(self):
        format = self.format
        if 'rst' in format:
            parts = publish_parts(source=self.cooked,
                  writer_name="html4css1",
                  settings_overrides={})
            if 'body' in format:
                contents = parts['fragment']
            else:
                contents = parts['whole']
            self.cooked = contents.replace('utf-8',
                                            'iso-8859-1')
        return self.cooked.encode('utf-8')

    __call__ = __str__


__all__ = ('BasicMailTemplate',)
