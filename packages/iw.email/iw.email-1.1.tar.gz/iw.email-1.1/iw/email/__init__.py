from iw.email.mail import MultipartMail
from iw.email.templates import BasicMailTemplate
from iw.email.templates import CheetahMailTemplate

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

