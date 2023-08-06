# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: setuphandlers.py 268 2008-06-13 18:39:16Z esmenttes $
#
# end: Platecom header
"""This module handles the product install process.
"""

from StringIO import StringIO
import logging
logger = logging.getLogger('icsemantic.catalog: setuphandlers')

import transaction

from zope.interface import alsoProvides

from Products.CMFCore.utils import getToolByName

from zope.app.component.hooks import setSite
from zope.app.component.interfaces import ISite
from Products.Five.site.localsite import enableLocalSiteHook

from icsemantic.core.interfaces import IicSemanticSite

from icsemantic.catalog.config import PROJECTNAME, DEPENDENCIES
from icsemantic.catalog.config import RELATED_IDX
from icsemantic.catalog.config import SYNONYM_IDX
from icsemantic.catalog.config import TRANSLATION_IDX
from icsemantic.catalog.config import HAS_PLONE3
from icsemantic.catalog.interfaces import IicSemanticManagementAdvancedSearchOptions
from icsemantic.catalog.preferences import icSemanticManagementAdvancedSearchOptions

def is_icsemantic_catalog_profile(context):
    """Ordinarily, GenericSetup handlers check for the existence of
    XML files. Here, we are not parsing an XML file, but we use this
    text file as a flag to check that we actually meant for this import
    step to be run. The file is found in profiles/default.
    """
    return context.readDataFile("icsemantic_catalog_marker.txt") is not None

def add_indexes(context):
    """Add fake catalog indexes for synonyms, translations and
    relations.
    """
    catalog = getToolByName(context.getSite(), 'portal_catalog')
    if not SYNONYM_IDX in catalog.indexes():
        catalog.manage_addIndex(SYNONYM_IDX, 'SynonymIndex')

    if not TRANSLATION_IDX in catalog.indexes():
        catalog.manage_addIndex(TRANSLATION_IDX, 'TranslationIndex')

    if not RELATED_IDX in catalog.indexes():
        catalog.manage_addIndex(RELATED_IDX, 'RelatedIndex')


def update_portal_atct(context):
    """Update ATCT tool with criteria for synonyms, translations and
    relations.
    """
    atct_tool = getToolByName(context.getSite(), 'portal_atct')
    atct_tool.addIndex(SYNONYM_IDX, friendlyName='Synonyms', enabled=1)
    atct_tool.addIndex(TRANSLATION_IDX, friendlyName='Translations', enabled=1)
    atct_tool.addIndex(RELATED_IDX, friendlyName='Relations', enabled=1)


def install_dependencies(context):
    """Install dependencies"""
    quickinstaller = getToolByName(context.getSite(), 'portal_quickinstaller')
    for product in DEPENDENCIES:
        if quickinstaller.isProductInstalled(product):
            quickinstaller.reinstallProducts([product])
            transaction.savepoint()
        else:
            quickinstaller.installProduct(product)
            transaction.savepoint()

def setup_site(portal, out):
    """

        >>> from icsemantic.core import interfaces
        >>> from zope.app.component.hooks import setSite
        >>> setSite(portal)

        >>> sm = portal.getSiteManager()
        >>> pmas = sm.queryUtility(interfaces.IicSemanticManagementAdvancedSearchOptions,
        ...                        name='icsemantic.advancedsearch')
        >>> pmas.include_ontocatalog_criteria == False
        True

    """
    alsoProvides(portal, IicSemanticSite)
    sm = portal.getSiteManager()

    if not sm.queryUtility(IicSemanticManagementAdvancedSearchOptions, name='icsemantic.advancedsearch'):
        if HAS_PLONE3:
            sm.registerUtility(icSemanticManagementAdvancedSearchOptions(),
                               interfaces.IicSemanticManagementAdvancedSearchOptions,
                               'icsemantic.advancedsearch')
        else:
            sm.registerUtility(IicSemanticManagementAdvancedSearchOptions,
                               icSemanticManagementAdvancedSearchOptions(),
                               'icsemantic.advancedsearch')

def setup_various(context):
    """Basically the install method"""
    if not is_icsemantic_catalog_profile(context):
        return

    site = context.getSite()
    out = StringIO()
    logger = context.getLogger("icsemantic.catalog")

    if not ISite.providedBy(site):
        enableLocalSiteHook(site)
        setSite(site)

    install_dependencies(context)
    add_indexes(context)
    update_portal_atct(context)
    setup_site(site, out)

    print >> out, 'Various settings imported.'

    logger.info(out.getvalue())
    return out.getvalue()


