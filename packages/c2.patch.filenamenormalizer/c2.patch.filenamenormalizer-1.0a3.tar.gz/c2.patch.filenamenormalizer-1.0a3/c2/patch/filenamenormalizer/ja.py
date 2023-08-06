# -*- coding: UTF-8 -*-
"""
ja.py

Created by Manabu Terada on 2010-02-12.
Copyright (c) 2010 CMScom. All rights reserved.
"""
from zope.interface import implements
from zope.component import getUtility
from Products.CMFCore.interfaces import ISiteRoot

from plone.i18n.normalizer.interfaces import INormalizer
from plone.i18n.normalizer.base import baseNormalize
try:
    from plone.i18n.normalizer.interfaces import IUserPreferredFileNameNormalizer, \
                            IUserPreferredURLNormalizer
    from plone.i18n.normalizer import FILENAME_REGEX
    FILE_NORMALIZER = True
except ImportError:
    FILE_NORMALIZER = False
    
from config import *

def get_normalize_value(ua, filename, instance):

    if 'MSIE' in ua:        
        if FILE_NORMALIZER and not IE_NORMALIZE:
            filename = IUserPreferredURLNormalizer(instance.REQUEST).normalize(
                    unicode(filename, instance.getCharset()))
            base = filename
            ext = ""
            m = FILENAME_REGEX.match(filename)
            if m is not None:
                base = m.groups()[0]
                ext  = m.groups()[1]
            if len(base) > 8:
                base = base[:8]
            if ext:
                base = base + '.' + ext
            filename=base
        elif not JA_DEPENDENCE:
            filename = urllib.quote(
                unicode(filename, instance.getCharset()).encode('utf-8', 'replace'))
        else:
            filename = unicode(filename, instance.getCharset()).encode('shift_jis', 'replace')
            # header_value = m['content-disposition'].replace("\\\\", "\\")
    elif 'Chrome' in ua:
        filename = unicode(filename, instance.getCharset()).encode(charset, 'replace')
    elif 'Safari' in ua:
        filename = unicode(filename, instance.getCharset()).encode(charset, 'replace')
    elif 'Opera' in ua:
        filename = unicode(filename, instance.getCharset()).encode(charset, 'replace')
    else:
        filename = unicode(filename, instance.getCharset()).encode(charset, 'replace')
    return filename


class FileNormalizer(object):
    """
    This normalizer can normalize any unicode string and returns a version
    that only contains of ASCII characters.

    Let's make sure that this implementation actually fulfills the API.

      >>> from zope.interface.verify import verifyClass
      >>> verifyClass(INormalizer, FileNormalizer)
      True

      >>> norm = FileNormalizer()
      >>> text = unicode("ファイル名.txt", 'utf-8')
      >>> norm.normalize(text)
      '30c630b930c830fc'
    """
    implements(INormalizer)

    def normalize(self, text, locale=None, max_length=None):
        """
        Returns a normalized text. text has to be a unicode string.
        """
        portal = getUtility(ISiteRoot)
        print "terada test ", portal
        print dir(portal)
        print portal.REQUEST
        return baseNormalize(text, transliterate=False)

filenormalizer = FileNormalizer()