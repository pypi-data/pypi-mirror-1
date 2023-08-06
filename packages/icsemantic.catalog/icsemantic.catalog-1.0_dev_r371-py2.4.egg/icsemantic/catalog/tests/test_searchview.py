# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: test_searchview.py 240 2008-06-11 05:01:23Z esmenttes $
#
# end: Platecom header
"""Test the search helper view
"""
import unittest
from zope.component import getMultiAdapter

from Products.CMFCore.utils import getToolByName
from Products.LinguaPlone.tests.utils import makeTranslation
from icsemantic.thesaurus.Thesaurus import thesaurus_utility

from icsemantic.catalog.tests.base import ICSemanticCatalogTestCase


class TestSearchView(ICSemanticCatalogTestCase):
    """Testing search view"""

    def test_contexts(self):
        """Test the contexts method"""
        t = thesaurus_utility()
        request = self.portal.REQUEST
        search_view = getMultiAdapter((self.portal, request,),
                                      name='ontocatalog-advanced-search')
        self.assertEquals(t.contexts(), search_view.contexts())

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSearchView))
    return suite