sx.translations

  This package provides components for use with Zope 3 and Zope 2 +
  Five that implement both ITranslationDomain and
  ILanguageAvailability as well as supporting the recording of
  untranslated msgids. This means that, not only do the components
  support the interface require to provide message to Zope 3's i18n
  framework, they can also be used to generate a list of avaiable
  languages using code similar to the following:

  from zope.component import getUtility
  from zope.i18n.interfaces import ILanguageAvailability
  from zope.i18n.locales import locales, LoadLocaleError

  domain = 'myproject'

  def getLanguages(self):
    options = getUtility(ILanguageAvailability,
                         domain).getAvailableLanguages()
    options.sort()
    result = []
    for option in options:
        lang = option[0]
        try:
            locale = locales.getLocale(lang)
        except LoadLocaleError:
            # probably not a real locale
            continue
        result.append(
            {'code':lang,
             'name':locale.displayNames.languages[lang],}
            )
    return result

  Requirements

    Zope 2.9.0 or higher is required.

  Installation

    To install, simply place the sx folder contained in the distribution
    onto your PYTHONPATH.

  Configuration

    Configuration is through ZCML, a complete example of which is
    shows below:

    <configure xmlns="http://namespaces.zope.org/zope"
               xmlns:i18n="http://namespaces.simplistix.co.uk/translations">

    <!-- make the sx.translations' registerTranslations directive
         available -->
    <include package="sx.translations" file="meta.zcml" />

    <!-- register our locales using sx.translations -->
    <i18n:registerTranslations locales="../locales" 
                               missing="../locales/myproj.pot"
                               encoding="utf-8"/>

    </configure>

    "locales" is a path pointing to a folder containing locale
    information in the standard GNU gettext layout, as currently
    supported by Zope 3.

    "missing" is a file to which untranslated msgids will be appended in
    .pot fortmat.

    "encoding" is optional and specifies the encoding to use for the
    file specified in the "missing" attribute. If not supplied, a
    default of utf-8 is used.

  Licensing

     Copyright (c) 2006-2009 Simplistix Ltd

     This Software is released under the MIT License:
     http://www.opensource.org/licenses/mit-license.html
     See license.txt for more details.

  Changes

     1.1

       - bring up to date for zope.i18n 3.7.0

     1.0

       - Initial release

