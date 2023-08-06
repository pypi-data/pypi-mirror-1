# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: base.py 268 2008-06-13 18:39:16Z esmenttes $
#
# end: Platecom header
"""Test setup for unit, integration and functional tests.

When we import PloneTestCase and then call setupPloneSite(), all of
Plone's products are loaded, and a Plone site will be created. This
happens at module level, which makes it faster to run each test, but
slows down test runner startup.
"""
from Products.Five import zcml
from Products.Five import fiveconfigure

from Testing import ZopeTestCase as ztc

from Products.CMFCore.utils import getToolByName
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

from zope.app.component.hooks import setSite

from icsemantic.thesaurus.Thesaurus import thesaurus_utility
#from icsemantic.catalog.indexes.utils import thesaurus_utility
from icsemantic.thesaurus.interfaces import IThesaurus
from icsemantic.catalog.config import *
from pyThesaurus.Concept import Concept

from icsemantic.langfallback.tests import utils

#
# When ZopeTestCase configures Zope, it will *not* auto-load products
# in Products/. Instead, we have to use a statement such as:
#
#   ztc.installProduct('SimpleAttachment')
#
# This does *not* apply to products in eggs and Python packages (i.e.
# not in the Products.*) namespace. For that, see below.
#
# All of Plone's products are already set up by PloneTestCase.
#

if not HAS_PLONE3:
    ztc.installProduct('PloneLanguageTool')

ztc.installProduct('LinguaPlone')
ztc.installProduct('pluggablecatalog')

@onsetup
def setup_icsemantic_catalog():
    ztc.installProduct('Five')
    fiveconfigure.debug_mode = True
    zcml.load_config('configure.zcml', PACKAGE)
    fiveconfigure.debug_mode = False

    # XXX monkey patch everytime (until we figure out the problem where
    # monkeypatch gets overwritten somewhere)
    try:
        from Products.Five import pythonproducts
        pythonproducts.setupPythonProducts(None)

        # MONKEYPATCH: arregla los problemas con el
        # control panel y la instalacion de Five...
        import App
        App.ApplicationManager.ApplicationManager.Five=utils.Five

        # MONKEYPATCH: arregla los problemas con el
        # HTTP_REFERER en los tests funcionales. Tiene la
        # contra de enviarnos al raiz del plone cada vez
        # que un metodo depende de esa variable, pero es
        # mejor que morir con una excepcion o llenar los
        # tests de try blocks...
        ztc.zopedoctest.functional.http=utils.http


    except ImportError:
        # Not needed in Plone 3
        ztc.installPackage('icsemantic.core')
        ztc.installPackage('icsemantic.langfallback')
        ztc.installPackage('icsemantic.thesaurus')
        ztc.installPackage(PROJECTNAME)
        pass

setup_icsemantic_catalog()

ptc.setupPloneSite(products=[PROJECTNAME,])

def add_test_thesaurus(context):
    """Fill the thesaurus local utility with some useful information"""

    # XXX: this shouldn't be necesary, but doesn't look like something
    # to take care in this package.
    setSite(context)

    t = thesaurus_utility()
    c = Concept(et = ["fútbol@es", "balón pie@es", "soccer@en", "football@en",
                      "football@fr"])
    t.append_concept(c)
    t.append_term("mundial@es", rt=["fútbol@es"], automatic=False)

    t.append_term("pelota@es", rt=["balón pie@es"], contexts=['publicidad'],
                  automatic=False)


class ICSemanticCatalogTestCase(ptc.PloneTestCase):
    """We use this base class for all the tests in this package. If
    necessary, we can put common utility or setup code in here. This
    applies to unit test cases.
    """
    def afterSetUp(self):
        ptc.PloneTestCase.afterSetUp(self)
        try:
            add_test_thesaurus(self.portal)
        except:
            pass
        self.loginAsPortalOwner()

        # Supported languages set to 'en', 'es' and 'fr' and 'en' as
        # default
        langtool = getToolByName(self.portal, 'portal_languages')
        langtool.addSupportedLanguage('en')
        langtool.addSupportedLanguage('es')
        langtool.addSupportedLanguage('fr')
        langtool.setDefaultLanguage('en')

        # Create a few members with the language property set
        self.add_member('member1', 'Member One', 'none1@test.com',
                        ('Member',), 'en')
        self.add_member('member2', 'Member Two', 'none2@test.com',
                        ('Member',), 'es')

    def add_member(self, username, fullname, email, roles, language):
        self.portal.portal_membership.addMember(username, 'secret', roles, [])
        member = self.portal.portal_membership.getMemberById(username)
        member.setMemberProperties({'fullname': fullname, 'email': email,
                                    'language': language})


class ICSemanticCatalogFunctionalTestCase(ptc.FunctionalTestCase):
    """We use this class for functional integration tests that use
    doctest syntax. Again, we can put basic common utility or setup
    code in here.
    """
    def setUp(self):
        super(ptc.FunctionalTestCase, self).setUp()
        add_test_thesaurus(self.portal)

