# -*- coding: utf-8 -*-
import types

WINDOWS_CHARS = (
   (u'\u201a',u','),    # 0x82 lower single quote
   (u'\u201e',u'"'),    # 0x84 lower double quote (german?)
   (u'\u02c6',u'^'),    # 0x88 small upper ^
   (u'\u2039',u'<'),    # 0x8b small <
   (u'\u2018',u'`'),    # 0x91 single curly backquote
   (u'\u2019',u"'"),    # 0x92 single curly quote
   (u'\u201c',u'"'),    # 0x93 double curly backquote
   (u'\u201d',u'"'),    # 0x94 double curly quote
   (u'\u2013',u'-'),    # 0x96 small dash
   (u'\u2014',u'-'),    # 0x97 dash
   (u'\u02dc',u'~'),    # 0x98 upper tilda
   (u'\u203a',u'>'),    # 0x9b small >
   (u'\xb4'  ,u"'"),    # 0xb4 almost horizontal single quote
   (u'\u2026',u'...'),  # 0x85 dots in one char
   (u'\u2022',u'.'),    # bullet
)

def safe_unicode(data, charset='utf-8'):
    """transform string to unicode and  replace special chars::

        >>> from iw.email.utils import safe_unicode
        >>> safe_unicode('a')
        u'a'
        >>> safe_unicode(u'\u2013')
        u'-'
        >>> safe_unicode('\xc3\xa9').encode('iso-8859-1') == '\xe9'
        True
        >>> safe_unicode(unicode('\xe2\x80\x93\xc3\xa9', 'utf-8')).encode('iso-8859-1') == '-\xe9'
        True
        >>> safe_unicode(unicode('\xe2\x80\x93', 'utf-8'))
        u'-'
    """
    if type(data) in (types.ListType, types.TupleType):
        return [safe_unicode(v, charset) for v in data]
    elif type(data) == types.DictType:
        return dict([(safe_unicode(k, charset), safe_unicode(v, charset)) \
                            for k, v in data.items()])
    elif type(data) not in types.StringTypes:
        return data

    if type(data) != types.UnicodeType:
        data = unicode(data, charset)
    for old, new in WINDOWS_CHARS:
        data = data.replace(old, new)
    return data
