# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: install.py 236 2008-06-10 20:28:23Z crocha $
#
# end: Platecom header
"""Install the product.
"""

from StringIO import StringIO

from Products.CMFCore.utils import getToolByName
from Products.Archetypes.utils import shasattr
from Products.Archetypes.Extensions.utils import install_subskin

from icsemantic.catalog import GLOBALS

def install(self):
    """External module to install the product.

    @type self: PloneSite
    @param self: The Plone site object

    @rtype: StringIO
    @return: Messages from the install process
    """
    out = StringIO()

    install_subskin(self, out, GLOBALS)
    # Run all import steps for icsemantic.catalog
    setup_tool = getToolByName(self, 'portal_setup')
    if shasattr(setup_tool, 'runAllImportStepsFromProfile'):
        # Plone 3
        setup_tool.runAllImportStepsFromProfile('profile-icsemantic.catalog:default')
    else:
        # Plone 2.5.
        old_context = setup_tool.getImportContextID()
        setup_tool.setImportContext('profile-icsemantic.catalog:default')
        setup_tool.runAllImportSteps()
        setup_tool.setImportContext(old_context)

    return out.getvalue()


def uninstall( self ):
    """Uninstall method.
    """
    out = StringIO()
    print >> out, "Uninstalling"
    return out.getvalue()
