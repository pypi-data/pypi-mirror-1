# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: synonym.py 236 2008-06-10 20:28:23Z crocha $
#
# end: Platecom header
"""A friendly criterion for ATTopic that matches the
SearchableSynonymousText index parameters.
"""

from Products.CMFCore.permissions import View
from AccessControl import ClassSecurityInfo

from Products.ATContentTypes.criteria import registerCriterion
from Products.ATContentTypes.interfaces import IATTopicSearchCriterion
from Products.ATContentTypes.permission import ChangeTopics
from Products.ATContentTypes.criteria.simplestring import \
    ATSimpleStringCriterion
from Products.ATContentTypes.criteria.simplestring import \
    ATSimpleStringCriterionSchema

from icsemantic.catalog import OntoCatalogMessageFactory as _

ATSynonymCriterionSchema = ATSimpleStringCriterionSchema


class ATSynonymCriterion(ATSimpleStringCriterion):
    """A synonym text criterion"""

    __implements__ = ATSimpleStringCriterion.__implements__ + \
                     (IATTopicSearchCriterion,)

    security       = ClassSecurityInfo()
    schema         = ATSynonymCriterionSchema
    meta_type      = 'ATSynonymCriterion'
    archetype_name = 'Friendly Synonym Criterion'
    shortDesc      = 'Synonym Criterion'


registerCriterion(ATSynonymCriterion, ['SynonymIndex'])
