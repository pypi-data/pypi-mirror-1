# -*- coding: utf-8 -*-
import os
import zope.interface
from iw.email.templates import BasicMailTemplate
from iw.email.interfaces import IMailTemplate
from iw.email.mail import MultipartMail
from docutils.core import publish_parts
from mako.template import Template
from utils import safe_unicode
import types

class MakoMailTemplate(BasicMailTemplate):
    zope.interface.implements(IMailTemplate)

    def __init__(self, path, format='rst', cache=None):
        if not os.path.isfile(path):
            raise IOError('No such file %s' % path)
        if cache and not os.path.isdir(cache):
            raise IOError('No such cache directory %s' % cache)
        self.path = path
        self.format = format
        self.cache = cache

    def cook(self, **options):
        options = self.clean_options(**options)
        options['safe_unicode'] = safe_unicode
        self.cooked = Template(filename=self.path,
                               output_encoding='utf8',
                               default_filters=['decode.utf8'],
                               module_directory=self.cache
                               ).render_unicode(**options)

def MakoMail(path, format='rst', cache=None,
                mfrom=None, mto=None, subject='', **options):
    options.update(dict(mfrom=mfrom, mto=mto, subject=subject))
    template = MakoMailTemplate(path, format=format, cache=cache)
    template.cook(**options)
    html = text = None
    if format == 'plain':
        text = str(template)
    else:
        html = str(template)
    return MultipartMail(html=html, text=text,
                         mfrom=mfrom, mto=mto, subject=subject)


__all__ = ('MakoMailTemplate', 'MakoMail')

