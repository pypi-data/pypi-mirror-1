from mail import MultipartMail
from templates import BasicMailTemplate
from templates import CheetahMailTemplate
from utils import safe_unicode

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

