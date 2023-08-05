# -*- coding: utf-8 -*-
import zope.interface

def IMail(self):
    """an email
    """

    def __str__():
        """render as string
        """


class IMailTemplate(zope.interface.Interface):
    """an interface for objects able to generate email body
    """

    def cook(**options):
        """cook the templates with extra args
        """

    def __str__():
        """render as string
        """
