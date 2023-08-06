# -*- coding: utf-8 -*-
import zope.interface

class IMail(zope.interface.Interface):
    """an email
    """

    def addImage(image, filename='', content_type=''):
        """add an image as attachment
        """

    def as_string(self, unixfrom=True):
        """email.MIMEMessage api
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
