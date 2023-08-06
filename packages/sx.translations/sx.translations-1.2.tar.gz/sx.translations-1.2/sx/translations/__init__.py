# Copyright (c) 2006-2009 Simplistix Ltd
#
# This Software is released under the MIT License:
# http://www.opensource.org/licenses/mit-license.html
# See license.txt for more details.

import os.path
import re

from datetime import datetime
from zope.component import getUtility
from zope.i18n import interpolate
from zope.i18n.interfaces import ILanguageAvailability
from zope.i18n.interfaces import ITranslationDomain
from zope.i18n.interfaces import INegotiator
from zope.i18n.translationdomain import TranslationDomain
from zope.i18nmessageid import Message
from zope.interface import implements

class Translations(TranslationDomain):

    implements(ILanguageAvailability)

    def getAvailableLanguages(self):
        result = []
        for language in self._catalogs.keys():
            bits = language.split('_')
            if len(bits)>3:
                raise NotImplementedError('Odd language found: %r'%language)
            if len(bits)>2:
                variant = bits[2]
            else:
                variant = None
            if len(bits)>1:
                country = bits[1]
            else:
                country = None
            language = bits[0]
            result.append((language,country,variant))
        return result

marker = object()

pot_template = u'''
#. Orginal text:%(original)s
#. Added on: %(date)s
msgid "%(id)s"
msgstr ""
'''

msgid_re = re.compile('\nmsgid "(.*)"\n')

class MissingTranslations(Translations):
    
    def __init__(self, domain, fallbacks=None,
                 missing_path=None,
                 encoding='utf-8'):
        super(MissingTranslations, self).__init__(domain,fallbacks)
        if missing_path is None:
            raise RuntimeError('missing_path cannot be None!')        
        self.missing_path = missing_path
        self.encoding = encoding
        self.seen = set()
        if os.path.exists(missing_path):
            for msgid in msgid_re.findall(open(missing_path).read()):
                self.seen.add(msgid)

    def translate(self, msgid, mapping=None, context=None,
                  target_language=None, default=None):
        """See zope.i18n.interfaces.ITranslationDomain"""

        # if the msgid is empty, let's save a lot of calculations and return
        # an empty string.
        if msgid == u'':
            return u''

        if target_language is None and context is not None:
            langs = self._catalogs.keys()
            # invoke local or global unnamed 'INegotiator' utilities
            negotiator = getUtility(INegotiator)
            # try to determine target language from negotiator utility
            target_language = negotiator.getLanguage(langs, context)

        # MessageID attributes override arguments
        if isinstance(msgid,Message):
            if msgid.domain != self.domain:
                util = getUtility(ITranslationDomain, msgid.domain)
                return util.translate(msgid,mapping,context,
                                      target_language,default)
            mapping = msgid.mapping
            default = msgid.default

        if default is None:
            default = unicode(msgid)

        # Get the translation. Use the specified fallbacks if this fails
        catalog_names = self._catalogs.get(target_language)
        if catalog_names is None:
            for language in self._fallbacks:
                catalog_names = self._catalogs.get(language)
                if catalog_names is not None:
                    break

        text = marker
        if catalog_names:
            if len(catalog_names) == 1:
                # this is a slight optimization for the case when there is a
                # single catalog. More importantly, it is extremely helpful
                # when testing and the test language is used, because it
                # allows the test language to get the default. 
                text = self._data[catalog_names[0]].queryMessage(
                    msgid, marker)
            else:
                for name in catalog_names:
                    catalog = self._data[name]
                    s = catalog.queryMessage(msgid,marker)
                    if s is not marker:
                        text = s
                        break

        if text is marker:
            if msgid not in self.seen:
                f = open(self.missing_path,'a')
                f.write((pot_template % {
                    'id':msgid.replace('"', r'\"'),
                    'original':''.join(
                        ['\n#. '+line for line in unicode(default).split('\n')]
                        ),
                    'date':datetime.now(),
                    }).encode(self.encoding))
                f.close()
                self.seen.add(msgid)
            text = default

        # Now we need to do the interpolation
        if text and mapping:
            text = interpolate(text, mapping)
        return text
