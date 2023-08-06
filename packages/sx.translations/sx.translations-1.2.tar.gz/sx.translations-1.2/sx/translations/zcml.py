# Copyright (c) 2006 Simplistix Ltd
#
# This Software is released under the MIT License:
# http://www.opensource.org/licenses/mit-license.html
# See license.txt for more details.

import os

from sx.translations import Translations,MissingTranslations
# from sx.translations.missingmessagecatalog import MissingMessageCatalog
from zope.component.zcml import utility
from zope.configuration.fields import Path
from zope.i18n.gettextmessagecatalog import GettextMessageCatalog
from zope.i18n.interfaces import ITranslationDomain
from zope.i18n.interfaces import ILanguageAvailability
from zope.i18n.testmessagecatalog import TestMessageCatalog
from zope.interface import Interface
from zope.schema import ASCII

class IRegisterTranslationsDirective(Interface):
    """Register translations with the global site manager."""

    locales = Path(
        title=u"Locales Directory",
        description=u"Directory containing the translations",
        required=True
        )

    missing = Path(
        title=u"Missing File",
        description=u"Path to which .pot for missing msgids will be appended",
        required=False
        )

    encoding = ASCII(
        title=u"Encoding for Missing File",
        description=u"This defaults to utf-8",
        required=False
        )

def registerTranslations(_context,
                         locales,
                         missing=None,
                         encoding='utf-8'):
    path = os.path.normpath(locales)
    domains = {}

    # Gettext has the domain-specific catalogs inside the language directory,
    # which is exactly the opposite as we need it. So create a dictionary that
    # reverses the nesting.
    for language in os.listdir(path):
        lc_messages_path = os.path.join(path, language, 'LC_MESSAGES')
        if os.path.isdir(lc_messages_path):
            for domain_file in os.listdir(lc_messages_path):
                if domain_file.endswith('.mo'):
                    domain_path = os.path.join(lc_messages_path, domain_file)
                    domain = domain_file[:-3]
                    if not domain in domains:
                        domains[domain] = {}
                    domains[domain][language] = domain_path

    # Now create Translations objects and add them as utilities
    for name, langs in domains.items():
        if missing:
            domain = MissingTranslations(name,
                                         missing_path=missing,
                                         encoding=encoding)
        else:
            domain = Translations(name)

        for lang, file in langs.items():
            domain.addCatalog(GettextMessageCatalog(lang, name, file))

        utility(_context, ITranslationDomain, domain, name=name)
        utility(_context, ILanguageAvailability, domain, name=name)
