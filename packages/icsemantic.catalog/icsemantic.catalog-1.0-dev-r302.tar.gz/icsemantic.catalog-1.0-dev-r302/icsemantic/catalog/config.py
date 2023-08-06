# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: config.py 236 2008-06-10 20:28:23Z crocha $
#
# end: Platecom header
"""Global constants for OntoCatalog.
"""

GLOBALS = globals()
try:
    import Products.CMFPlone.migrations.v3_0
    HAS_PLONE3 = True
except ImportError:
    HAS_PLONE3 = False

import icsemantic.catalog
PROJECTNAME = "icsemantic.catalog"
PACKAGE = icsemantic.catalog
PACKAGENAME = "icsemantic.catalog"
DEPENDENCIES = ['LinguaPlone', 'pluggablecatalog', 'icsemantic.langfallback', 'icsemantic.thesaurus']

SYNONYM_IDX = 'SearchableSynonymousText'
TRANSLATION_IDX = 'SearchableTranslatedText'
RELATED_IDX = 'SearchableRelatedText'