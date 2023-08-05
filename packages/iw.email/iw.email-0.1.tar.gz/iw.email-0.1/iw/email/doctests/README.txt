========
iw.email
========

Provide a clean way to generate an email.

We need som html::

    >>> umail = unicode('''<html><body>
    ... corps du maiil avec caractère unicode:
    ... utf-8: é à î ö 
    ... cp552: \xe2\x80\x93 \xe2\x80\x99
    ... </body></html>''', 'utf-8')


And a smtp server::

    >>> from iw.email.tests.utils import SMTP
    >>> server = SMTP('localhost')

Now we can use the Mail class::

    >>> from iw.email import MultipartMail

    >>> mail = MultipartMail(html=umail,
    ...             mfrom='sender@ingeniweb.com',
    ...             mto='recipient@ingeniweb.com',
    ...             subject=unicode('sujèéèt','utf-8'))
    >>> server.sendmail('sender@ingeniweb.com','recipient@ingeniweb.com', mail)
    From nobody...
    Content-Type: multipart/related; charset="iso-8859-1";
        boundary="...
    MIME-Version: 1.0
    Subject: =?iso-8859-1?q?suj=E8=E9=E8t?=
    From: sender@ingeniweb.com
    To: recipient@ingeniweb.com
    <BLANKLINE>
    --===============...
    Content-Type: multipart/alternative; charset="iso-8859-1";
        boundary="...
    MIME-Version: 1.0
    <BLANKLINE>
    --===============...
    Content-Type: text/html; charset="iso-8859-1"
    MIME-Version: 1.0
    Content-Transfer-Encoding: quoted-printable
    <BLANKLINE>
    <html><body>
    corps du maiil avec caract=E8re unicode:
    utf-8: =E9 =E0 =EE =F6 =
    <BLANKLINE>
    cp552: - '
    </body></html>
    --===============...
    --===============...

Ok, that's cool but sometimes we want to add images.
So, just do it::

    >>> image = open(os.path.join(testdir, 'bullet.gif'))
    >>> image.read()
    'GIF89a\x05\x00\r\x00\x80\x00\x00c\x8c\x9c\xff\xff\xff!\xf9\x04\x01\x00\x00\x01\x00,\x00\x00\x00\x00\x05\x00\r\x00\x00\x02\t\x8c\x8f\xa9\xbb\xe0\x0f\xa3\x84\xa9\x00;'
    >>> image.seek(0)

    >>> mail.addImage(image, filename='bullet.gif', content_type='image/gif')
    >>> mail.images
    [<email.MIMEImage.MIMEImage instance at ...>]
    >>> print mail.images[0].as_string()
    Content-Type: image/gif; name="bullet.gif"
    MIME-Version: 1.0
    Content-Transfer-Encoding: base64
    Content-ID: <bullet.gif>
    <BLANKLINE>
    R0lGODlhBQANAIAAAGOMnP///yH5BAEAAAEALAAAAAAFAA0AAAIJjI+pu+APo4SpADs=


We can also use Cheetah template to generate an email::

    >>> from iw.email import CheetahMail
    >>> path = os.path.join(testdir, 'mail.tmpl')
    >>> umail = unicode('''
    ... corps du maiil avec caractère unicode:
    ... utf-8: é à î ö 
    ... cp552: \xe2\x80\x93 \xe2\x80\x99
    ... ''', 'utf-8')
    >>> mail = CheetahMail(path=path,
    ...             title='nice title',
    ...             paragraph=umail,
    ...             mfrom='sender@ingeniweb.com',
    ...             mto='recipient@ingeniweb.com',
    ...             subject=unicode('sujèéèt','utf-8'))
    >>> server.sendmail('sender@ingeniweb.com','recipient@ingeniweb.com', mail)
    From nobody ...
    Content-Type: multipart/related; charset="iso-8859-1";
    ...
    From: sender@ingeniweb.com
    To: recipient@ingeniweb.com
    ...
    <body>
    <div class=3D"document" id=3D"nice-title">
    <h1 class=3D"title">nice title</h1>
    <p>corps du maiil avec caract=E8re unicode:
    iso-8859-1: =E9 =E0 =EE =F6
    cp552: - '</p>
    </div>
    </body>
    </html>
    <BLANKLINE>
    ...

