import os
import logging

# Patch the Zope3 negotiator to cache the negotiated languages
from Products.PlacelessTranslationService.memoize import memoize_second
from zope.i18n.negotiator import Negotiator
Negotiator.getLanguage = memoize_second(Negotiator.getLanguage)


# Patch Zope3 to use a lazy message catalog, but only if we haven't
# restricted the available catalogs in the first place.
from Products.PlacelessTranslationService.load import PTS_LANGUAGES
if PTS_LANGUAGES is not None:
    from zope.i18n import gettextmessagecatalog
    from Products.PlacelessTranslationService.lazycatalog import \
        LazyGettextMessageCatalog
    gettextmessagecatalog.GettextMessageCatalog = LazyGettextMessageCatalog


# Patch the Zope3 i18n zcml statement:
#	- to compile po files to mo
#	- to check for an existing domain

from Products.PlacelessTranslationService.load import _compile_locales_dir

from zope.i18n.gettextmessagecatalog import GettextMessageCatalog
from zope.i18n.testmessagecatalog import TestMessageCatalog
from zope.i18n.translationdomain import TranslationDomain
from zope.i18n.interfaces import ITranslationDomain

from zope.component import queryUtility
from zope.component import getGlobalSiteManager

from Products.PlacelessTranslationService.interfaces \
     import IPTSTranslationDomain
from Products.PlacelessTranslationService.PlacelessTranslationService \
     import PlacelessTranslationService as PTS
from Products.PlacelessTranslationService.GettextMessageCatalog \
     import BrokenMessageCatalog, _moCache

# PTSTranslationDomain is incompatible with TranslationDomain, just as
# respectives GettextMessageCatalog. The idea is to get MO files compiled by PTS
# and registers them with zope.i18n. In configure.zcml we have included CMFPlone
# to be sure that PTSTranslationDomain utilities are registered before we starts
# registering translation. That way we will override these utilities with
# zope.i18n ones.

def addCatalogDecorator(func):
    def z3_addCatalog(self, catalog):
        func(self, catalog)
        if isinstance(catalog, BrokenMessageCatalog):
            return

        # force .mo build and get file path
        _moCache.cachedPoFile(catalog)
        domains = {
            catalog.getDomain(): {
                    catalog.getLanguage(): _moCache.getPath(catalog),
                    }
            }
        doRegisterTranslations(domains)
    return z3_addCatalog

PTS.addCatalog = addCatalogDecorator(PTS.addCatalog)
PTS.reloadCatalog = addCatalogDecorator(PTS.reloadCatalog)

def patched_registerTranslations(_context, directory):
    # compile mo files
    _compile_locales_dir(directory)

    path = os.path.normpath(directory)
    domains = {}
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

    if domains != {}:
        _context.action(
            ('i18n', directory,),
            doRegisterTranslations,
            args=(domains,)
            )

def doRegisterTranslations(domains):

    for name, langs in domains.items():
        # Try to get an existing domain and add catalogs to it
        domain = queryUtility(ITranslationDomain, name,)

        if domain is None or IPTSTranslationDomain.providedBy(domain):
            # create domain, or get rid of PTS tr. domain.
            domain = TranslationDomain(name)
            # make sure we have a TEST catalog for each domain:
            domain.addCatalog(TestMessageCatalog(name))
            gsm = getGlobalSiteManager()
            gsm.registerUtility(domain, name=name)

        for lang, file_path in langs.items():
            domain.addCatalog(GettextMessageCatalog(lang, name, file_path))

# applying the patch
#zcml.registerTranslations = patched_registerTranslations
LOG = logging.getLogger(__name__)
LOG.info("Patching zope.i18n.zcml.registerTranslations via our configure.zcml")
