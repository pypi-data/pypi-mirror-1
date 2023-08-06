# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: interfaces.py 236 2008-06-10 20:28:23Z crocha $
#
# end: Platecom header
"""Interfaces for the browser module
"""

from zope.interface import Interface, Attribute


class IAdvancedSearch(Interface):
    """A helper view for the custom search form"""

    def ontocatalog_fields_enabled():
        """True if the OntoCatalog options are enabled for search"""

    def available_languages():
        """Return all the avalilable languages"""

    def contexts():
        """Return all the contexts in the thesaurus"""