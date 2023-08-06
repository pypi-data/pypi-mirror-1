# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: translation.py 302 2008-06-19 21:33:06Z esmenttes $
#
# end: Platecom header
"""A friendly criterion for ATTopic that matches the
SearchableTranslatedText index parameters.
"""

from zope.component import queryUtility
from zope.app.schema.vocabulary import IVocabularyFactory

from Products.CMFCore.permissions import View
from AccessControl import ClassSecurityInfo

from Products.Archetypes.atapi import Schema
from Products.Archetypes.atapi import StringField, StringWidget
from Products.Archetypes.atapi import LinesField, MultiSelectionWidget

from Products.ATContentTypes.criteria import registerCriterion
from Products.ATContentTypes.interfaces import IATTopicSearchCriterion
from Products.ATContentTypes.permission import ChangeTopics
from Products.ATContentTypes.criteria.base import ATBaseCriterion
from Products.ATContentTypes.criteria.schemata import ATBaseCriterionSchema

from Products.Archetypes.atapi import DisplayList

from icsemantic.catalog import OntoCatalogMessageFactory as _


ATTranslationCriterionSchema = ATBaseCriterionSchema + Schema((
    StringField('value',
                required=1,
                mode="rw",
                write_permission=ChangeTopics,
                accessor="Value",
                mutator="setValue",
                default="",
                widget=StringWidget(
                    label=_(u'label_translation_criterion_value',
                            default=u'Value'),
                    description=_(u'help_translation_criterion_value',
                                  default=u'A string value.'))
                ),
    LinesField('language',
                required=1,
                mode="rw",
                write_permission=ChangeTopics,
                accessor="Language",
                mutator="setLanguage",
                default=[],
                vocabulary="getLanguages",
                widget=MultiSelectionWidget(
                    label=_(u'label_translation_criterion_language',
                            default=u'Language'),
                    description=_(u'help_translation_criterion_language',
                                  default=u'A list of languages.'))
                ),

    ))


class ATTranslationCriterion(ATBaseCriterion):
    """A translation text criterion"""

    __implements__ = ATBaseCriterion.__implements__ + (IATTopicSearchCriterion,)

    security       = ClassSecurityInfo()
    schema         = ATTranslationCriterionSchema
    meta_type      = 'ATTranslationCriterion'
    archetype_name = 'Friendly Translation Criterion'
    shortDesc      = 'Translation Criterion'

    def getLanguages(self):
        vocab = queryUtility(IVocabularyFactory, name=u'icsemantic.languages')
        langs = [(i.token, i.title) for i in vocab(self)]

        return DisplayList(langs)

    security.declareProtected(View, 'getCriteriaItems')
    def getCriteriaItems(self):
        result = []
        value = self.Value()
        language = self.Language()

        if value is not '':
            result.append((self.Field(), value))

        if language is not '':
            result.append((self.Field(),
                           {'query': value, 'language': language}))

        return tuple(result)


registerCriterion(ATTranslationCriterion, ['TranslationIndex'])
