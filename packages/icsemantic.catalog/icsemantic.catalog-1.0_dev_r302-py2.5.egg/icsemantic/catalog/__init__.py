# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: __init__.py 236 2008-06-10 20:28:23Z crocha $
#
# end: Platecom header
"""OntoCatalog
"""

from AccessControl import ModuleSecurityInfo
from zope.i18nmessageid import MessageFactory
from zope import component
from zope import interface

from Products.pluggablecatalog.interfaces import IQueryDefaults
from Products.CMFCore.DirectoryView import registerDirectory

OntoCatalogMessageFactory = MessageFactory('icsemantic.catalog')
ModuleSecurityInfo('icsemantic.catalog').declarePublic('OntoCagalogMessageFactory')


#Import indexes
from icsemantic.catalog.indexes.related import RelatedIndex, \
    manage_addRelatedIndex, manage_addRelatedIndexForm
from icsemantic.catalog.indexes.synonym import SynonymIndex, \
    manage_addSynonymIndex, manage_addSynonymIndexForm
from icsemantic.catalog.indexes.translation import TranslationIndex, \
    manage_addTranslationIndex, manage_addTranslationIndexForm

GLOBALS = globals()
registerDirectory('skins', GLOBALS)

def initialize(context):
    """Initialize the package"""
    import criteria
    register_fake_index(context)
    replace_catalog(context)


def _catalog_search_defaults(context, request, args):
    """Ignore the Language keyword when we are looking for translations
    or related content.
    """
    #When searching for translations or related content we don't want Language
    #filtering.
    nofilterkeys = ['SearchableRelatedText', 'SearchableTranslatedText',
                    'SearchableSynonymousText']

    for index in nofilterkeys:
        if args.has_key(index) or request.has_key(index):
            return {'Language': 'all'}

    return {}


def replace_catalog(context):
    """Make _catalog_search_defaults provide IQueryDefaults so
    pluggablecatalog uses it for the default search paramenters for all
    catalog searches.
    """
    interface.directlyProvides(_catalog_search_defaults, IQueryDefaults)
    component.provideUtility(_catalog_search_defaults)


def register_fake_index(context):
    """Register indexes"""
    context.registerClass(
        RelatedIndex,
        permission='Add Pluggable Index',
        constructors=(manage_addRelatedIndexForm,
                      manage_addRelatedIndex),
        icon='indexes/www/index.gif',
        visibility=None
    )

    context.registerClass(
        SynonymIndex,
        permission='Add Pluggable Index',
        constructors=(manage_addSynonymIndexForm,
                      manage_addSynonymIndex),
        icon='indexes/www/index.gif',
        visibility=None
    )

    context.registerClass(
        TranslationIndex,
        permission='Add Pluggable Index',
        constructors=(manage_addTranslationIndexForm,
                      manage_addTranslationIndex),
        icon='indexes/www/index.gif',
        visibility=None
    )
