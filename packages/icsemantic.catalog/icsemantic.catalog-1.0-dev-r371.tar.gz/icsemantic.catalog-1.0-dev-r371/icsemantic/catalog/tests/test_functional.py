# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: test_functional.py 240 2008-06-11 05:01:23Z esmenttes $
#
# end: Platecom header
"""Functional tests for OntoCatalog.
"""

import unittest
import doctest

from zope.testing import doctestunit
from zope.component import testing
from Testing import ZopeTestCase as ztc

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase.layer import PloneSite

from icsemantic.catalog.config import *
import base

def test_suite():
    return unittest.TestSuite([

        # Test the SearchableSynonymousText index in collections
        ztc.ZopeDocFileSuite(
            'tests/synonymous_criterion.txt', package=PACKAGENAME,
            test_class=base.ICSemanticCatalogFunctionalTestCase,
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE | doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),

        # Test the SearchableTranslatedText index in collections
        ztc.ZopeDocFileSuite(
            'tests/translated_criterion.txt', package=PACKAGENAME,
            test_class=base.ICSemanticCatalogFunctionalTestCase,
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE | doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),

        # Test the SearchableRelatedText index in collections
        ztc.ZopeDocFileSuite(
            'tests/related_criterion.txt', package=PACKAGENAME,
            test_class=base.ICSemanticCatalogFunctionalTestCase,
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE | doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),

        # Test the custom advance search form
        ztc.ZopeDocFileSuite(
            'tests/advanced_search.txt', package=PACKAGENAME,
            test_class=base.ICSemanticCatalogFunctionalTestCase,
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE | doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),
        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')