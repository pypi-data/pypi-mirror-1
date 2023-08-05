# -*- coding: utf-8 -*-
import os
from docutils.core import publish_parts
from Cheetah.Template import Template
import zope.interface
#from zope.pagetemplate.pagetemplatefile import PageTemplateFile
from interfaces import IMailTemplate
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

import Cheetah.Template

class CheetahMailTemplate(BasicMailTemplate):
    zope.interface.implements(IMailTemplate)

    def __init__(self, path, format='rst'):
        if not os.path.isfile(path):
            raise IOError('No such file %s' % path)
        self.path = path
        self.format = format

    def cook(self, **options):
        options = self.clean_options(**options)
        fd = open(self.path)
        source = safe_unicode(fd.read())
        fd.close()
        self.cooked = u'%s' % (Template(source=source,
                searchList=[options]))


        #class PageTemplate(PageTemplateFile):

#    def pt_getContext(self, args=(), options={}, **kw):
#        rval = PageTemplate.pt_getContext(self, args=args)
#        options.update(rval)
#        return options


#class ZopeMailTemplate(BasicMailTemplate):
#    zope.interface.implements(IMailTemplate)
#    format = 'html'

#    def __init__(self, path):
#        if not os.path.isfile(path):
#            raise IOError('No such file %s' % path)
#        self.template = PageTemplate(path)

#    def cook(self, **options):
#        options = self.clean_options(**options)
#        self.cooked = self.template(**options)

__all__ = ('BasicMailTemplate',
           'CheetahMailTemplate',
           #'ZopeMailTemplate'
          )
