# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: test_setup.py 268 2008-06-13 18:39:16Z esmenttes $
#
# end: Platecom header
"""Test OntoCatalog setup on installation.
"""

import unittest

from Products.pluggablecatalog.tool import CatalogTool

from icsemantic.catalog.interfaces import IicSemanticManagementAdvancedSearchOptions
from icsemantic.catalog.tests.base import ICSemanticCatalogTestCase


class TestICSemanticCatalogSetup(ICSemanticCatalogTestCase):
    """Testing the product setup"""

    def afterSetUp(self):
        """Ran before every unit test"""
        self.qi = self.portal.portal_quickinstaller
        self.catalog = self.portal.portal_catalog
        self.indexes = self.catalog.indexes()
        self.atct = self.portal.portal_atct
        self.topic_indexes = self.atct.topic_indexes

    def test_langview_installed(self):
        """Test that plantecom.langview is installed as a dependency"""
        self.failUnless(self.qi.isProductInstalled('icsemantic.langfallback'))

    def test_pluggablecatalog_installed(self):
        """Test that pluggablecatalog is installed as a dependency"""
        self.failUnless(self.qi.isProductInstalled('pluggablecatalog'))

    def test_linguaplone_installed(self):
        """Test that LinguaPlone is installed as a dependency"""
        self.failUnless(self.qi.isProductInstalled('LinguaPlone'))

    def test_ontoplone_installed(self):
        """Test that icsemantic.thesaurus is installed as a dependency"""
        self.failUnless(self.qi.isProductInstalled('icsemantic.thesaurus'))

    def test_synonym_index_added(self):
        """Test that a new SynonymIndex was added to the catalog"""
        self.failUnless('SearchableSynonymousText' in self.indexes)

    def test_related_index_added(self):
        """Test that a new RelatedIndex was added to the catalog"""
        self.failUnless('SearchableRelatedText' in self.indexes)

    def test_translation_index_added(self):
        """Test that a new TranslationIndex was added to the catalog"""
        self.failUnless('SearchableTranslatedText' in self.indexes)

    def test_advanced_search(self):
        """Test that the criteria from OntoCatalog are turned off from
        the default search by default.
        """
        sm = self.portal.getSiteManager()
        pmas = sm.queryUtility(IicSemanticManagementAdvancedSearchOptions,
                               name='icsemantic.advancedsearch')
        self.failIf(pmas.include_ontocatalog_criteria)

    def test_ontocatalog_criteria_available_in_topics(self):
        """Test that the OntoCatalog criteria are available to use in
        ATTopics.
        """
        self.failUnless('SearchableTranslatedText' in self.topic_indexes.keys())
        self.failUnless('SearchableRelatedText' in self.topic_indexes.keys())
        self.failUnless('SearchableSynonymousText' in self.topic_indexes.keys())

    def test_catalog_replaced(self):
        """Test that the default values for a catalog search were
        replaced.
        """
        self.failUnless(isinstance(self.catalog.aq_base, CatalogTool))

    #def test_ontocatalog_indexes_not_filtered(self):
        #"""Test that if the indexes defined by OntoCatalog appear in a
        #query, then the language is not filtered by the catalog.
        #"""
        #pass

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestICSemanticCatalogSetup))
    return suite
