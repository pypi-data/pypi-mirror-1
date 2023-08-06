# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: interfaces.py 265 2008-06-13 05:20:36Z crocha $
#
# end: Platecom header
""" icsemantic.catalog interfaces.
"""
# pylint: disable-msg=W0232,R0903

from zope import schema
from zope.interface import Interface
from icsemantic.core.i18n import _

class IicSemanticManagementAdvancedSearchOptions(Interface):
    """Interface to turn on/off the advanced search criteria from
    OntoCatalog.
    """
    include_ontocatalog_criteria = \
        schema.Bool(title = _(u'Include OntoCatalog criteria in the advanced '
                              'search'),
                    default = False,
                    required = True,
                    description = _(u'When set, there are options to search '
                                    'for synonyms, related content and '
                                    'translations in the advanced search '
                                    'form.'))

