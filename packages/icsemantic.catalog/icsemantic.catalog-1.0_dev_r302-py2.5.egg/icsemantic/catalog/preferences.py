# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: preferences.py 272 2008-06-13 21:29:17Z esmenttes $
#
# end: Platecom header
from zope.interface import implements
from zope.component import getUtility
from OFS.SimpleItem import SimpleItem
from zope.schema.fieldproperty import FieldProperty
#from icsemantic.core.annotations import KeywordBasedAnnotations
#from fieldproperty import ToolDependentFieldProperty, AuthenticatedMemberFieldProperty

import interfaces

class icSemanticManagementAdvancedSearchOptions(SimpleItem):
    implements(interfaces.IicSemanticManagementAdvancedSearchOptions)

    include_ontocatalog_criteria = FieldProperty(interfaces.IicSemanticManagementAdvancedSearchOptions['include_ontocatalog_criteria'])

    def __call__(self):
        pass

def advanced_search_form_adapter(context):
    return getUtility(interfaces.IicSemanticManagementAdvancedSearchOptions, name='icsemantic.advancedsearch', context=context)

