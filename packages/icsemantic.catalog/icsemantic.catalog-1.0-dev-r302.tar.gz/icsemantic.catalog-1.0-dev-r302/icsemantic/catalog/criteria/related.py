# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: related.py 240 2008-06-11 05:01:23Z esmenttes $
#
# end: Platecom header
"""A friendly criterion for ATTopic that matches the
SearchableRelatedText index parameters
"""

from Products.CMFCore.permissions import View
from AccessControl import ClassSecurityInfo

from Products.Archetypes.atapi import Schema
from Products.Archetypes.atapi import StringField, StringWidget, \
    MultiSelectionWidget
from Products.Archetypes.atapi import DisplayList

from Products.ATContentTypes.criteria import registerCriterion
from Products.ATContentTypes.interfaces import IATTopicSearchCriterion
from Products.ATContentTypes.permission import ChangeTopics
from Products.ATContentTypes.criteria.base import ATBaseCriterion
from Products.ATContentTypes.criteria.schemata import ATBaseCriterionSchema

from icsemantic.thesaurus.Thesaurus import thesaurus_utility
from icsemantic.catalog import OntoCatalogMessageFactory as _


ATRelatedCriterionSchema = ATBaseCriterionSchema + Schema((
    StringField('value',
                required=1,
                mode="rw",
                write_permission=ChangeTopics,
                accessor="Value",
                mutator="setValue",
                default="",
                widget=StringWidget(
                    label=_(u'label_related_criterion_value', default=u'Value'),
                    description=_(u'help_related_criterion_value',
                                  default=u'A string value.'))
                ),
    StringField('contexts',
                required=0,
                mode="rw",
                write_permission=ChangeTopics,
                accessor="Contexts",
                mutator="setContexts",
                default="",
                vocabulary="getContexts",
                widget=MultiSelectionWidget(
                    label=_(u'label_related_criterion_contexts',
                            default=u'Language'),
                    description=_(u'help_related_criterion_contexts',
                                  default=u'A list of contexts.'))
                ),
    ))


class ATRelatedCriterion(ATBaseCriterion):
    """A related text criterion"""

    __implements__ = ATBaseCriterion.__implements__ + (IATTopicSearchCriterion,)

    security       = ClassSecurityInfo()
    schema         = ATRelatedCriterionSchema
    meta_type      = 'ATRelatedCriterion'
    archetype_name = 'Friendly Related Criterion'
    shortDesc      = 'Related Criterion'

    def getContexts(self):
        """Get contexts from the thesaurus utility"""
        contexts = thesaurus_utility().contexts()
        return DisplayList(zip(contexts, contexts))

    security.declareProtected(View, 'getCriteriaItems')
    def getCriteriaItems(self):
        result = []
        value = self.Value()
        contexts = self.Contexts()

        if value is not '':
            result.append((self.Field(), value))

        if contexts is not '' and contexts is not None:
            result.append((self.Field(), {'query': value, 'contexts': contexts}))

        return tuple(result)

registerCriterion(ATRelatedCriterion, ['RelatedIndex'])
