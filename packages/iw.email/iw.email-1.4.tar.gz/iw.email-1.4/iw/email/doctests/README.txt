MultipartMail
=============

The base class of the package is the MultipartMail.  You can use it to easily
generate email both in html or text format with a correct encoding.

We need some html for email body::

    >>> umail = unicode('''<html><body>
    ... corps du maiil avec caractère unicode:
    ... utf-8: é à î ö 
    ... cp552: \xe2\x80\x93 \xe2\x80\x99
    ... </body></html>''', 'utf-8')


And a smtp server::

    >>> from smtplib import SMTP
    >>> server = SMTP('localhost')

Now we can use the MultipartMail class to generate an email::

    >>> from iw.email import MultipartMail

    >>> mail = MultipartMail(html=umail,
    ...             mfrom='sender@ingeniweb.com',
    ...             mto='recipient@ingeniweb.com',
    ...             subject=unicode('sujèéèt','utf-8'))

And send it::

    >>> server.sendmail('sender@ingeniweb.com','recipient@ingeniweb.com', str(mail))
    Content-Type: multipart/related; charset="iso-8859-1";
    ...
    MIME-Version: 1.0
    To: recipient@ingeniweb.com
    From: sender@ingeniweb.com
    Subject: =?iso-8859-1?q?suj=E8=E9=E8t?=
    ...
    Content-Type: multipart/mixed; charset="iso-8859-1";
    ...
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
    ...


Ok, that's cool but sometimes we want to add images.
So, just do it::

    >>> image = open(os.path.join(testdir, 'bullet.gif'))
    >>> image.read()
    'GIF89a\x05\x00\r\x00\x80\x00\x00c\x8c\x9c\xff\xff\xff!\xf9\x04\x01\x00\x00\x01\x00,\x00\x00\x00\x00\x05\x00\r\x00\x00\x02\t\x8c\x8f\xa9\xbb\xe0\x0f\xa3\x84\xa9\x00;'
    >>> image.seek(0)

    >>> mail.addImage(image, filename='bullet.gif')
    >>> mail.images
    [<email...MIMEImage instance at ...>]
    >>> print mail.images[0].as_string()
    Content-Type: image/gif; name="bullet.gif"
    MIME-Version: 1.0
    Content-Transfer-Encoding: base64
    Content-ID: <bullet.gif>
    <BLANKLINE>
    R0lGODlhBQANAIAAAGOMnP///yH5BAEAAAEALAAAAAAFAA0AAAIJjI+pu+APo4SpADs=

CheetahMail
===========

We can also use Cheetah template to generate an email::

    >>> from iw.email import CheetahMail

Path is the path to the cheetah template::

    >>> path = os.path.join(testdir, 'mail.tmpl')
    >>> print open(path).read()
    ==========
    $title
    ==========
    <BLANKLINE>
    $paragraph
    <BLANKLINE>


    
We need a few arguments::

    >>> umail = unicode('''
    ... corps du maiil avec caractère unicode:
    ... utf-8: é à î ö 
    ... cp552: \xe2\x80\x93 \xe2\x80\x99
    ... ''', 'utf-8')

Then we can use the CheetahMail to generate an email from the template::

    >>> mail = CheetahMail(path=path,
    ...             title='nice title',
    ...             paragraph=umail,
    ...             mfrom='sender@ingeniweb.com',
    ...             mto='recipient@ingeniweb.com',
    ...             subject=unicode('sujèéèt','utf-8'))
    >>> server.sendmail('sender@ingeniweb.com','recipient@ingeniweb.com', str(mail))
    Content-Type: multipart/related; charset="iso-8859-1";
    ...
    To: recipient@ingeniweb.com
    From: sender@ingeniweb.com
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

