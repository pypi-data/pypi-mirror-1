# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: translation.py 268 2008-06-13 18:39:16Z esmenttes $
#
# end: Platecom header
"""TranslationIndex is an index for the catalog that does not index
anything.

Instead, the _apply_index performs a query to a thesaurus object for
translations of the keyword parameters and then queries the site
catalog for the result of the thesaurus query.
"""

from logging import getLogger

from zope.interface import implements
from zope.component import queryUtility
from zope.i18n.interfaces import IUserPreferredLanguages


from Globals import Persistent, DTMLFile
from OFS.SimpleItem import SimpleItem
from BTrees.IIBTree import IITreeSet, IISet, intersection, union

from Products.PluginIndexes import PluggableIndex
from Products.PluginIndexes.common.util import parseIndexRequest
from Products.PluginIndexes.interfaces import IPluggableIndex

from Products.CMFCore.utils import getToolByName

from icsemantic.catalog.indexes import utils


class TranslationIndex(Persistent, SimpleItem):
    """An index for translations that does not index anything"""

    __implements__ = (PluggableIndex.PluggableIndexInterface,)
    implements(IPluggableIndex)

    meta_type = "TranslationIndex"
    manage_workspace = DTMLFile('dtml/manageFakeIndex', globals())

    def __init__(self, id, extra=None, caller=None):
        """Creates a new index"""
        self.id = id
        self.catalog = caller

    def index_object(self, docid, obj ,threshold=100):
        """Hook for (Z)Catalog. Since this is a fake index, nothing is
        done here.
        """
        return 1

    def unindex_object(self, docid):
        """Hook for (Z)Catalog. Since this is a fake index, nothing is
        done here.
        """
        return

    def _apply_index(self, request, cid=''):
        """Apply the index to query parameters given in the argument,
        request.

        The argument should be a mapping object.

        If the request does not contain the needed parameters, then
        None is returned.

        Otherwise two objects are returned.  The first object is a
        ResultSet containing the record numbers of the matching
        records.  The second object is a tuple containing the names of
        all data fields used.
        """
        portal = getToolByName(self, 'portal_url').getPortalObject()
        query_options = ('query', 'language')
        record = parseIndexRequest(request, self.id, query_options)
        if record.keys is None:
            return None

        language = record.get('language', None)

        if language is not None:
            language = ('',) + tuple(language)
        else:
            language = ('',)

        #Languages dance
        langutil = queryUtility(IUserPreferredLanguages,
                                name='icsemantic_preferred_languages')
        user_languages = tuple(langutil.getPreferredLanguages(request=self.REQUEST))

        thesaurus_results = []
        catalog_results = ()
        for k in record.keys:
            for lang in  user_languages:
                filtered_langs = [l for l in language if
                                  l not in [lang, '']]
                key = "%s@%s" % (k, lang)
                thesaurus_results += utils.get_equivalent(portal, key,
                                                          filtered_langs)

                # TODO check if it is the same to move this outside the inner
                # for statement
                if thesaurus_results != []:
                    tuples = [tl.split('@') for tl in thesaurus_results]
                    translations = ['\"%s\"' % (t,) for (t,l) in tuples]
                    search_text = ' OR '.join(translations)
                    query = {'SearchableText': search_text,
                             'Language': language}
                    catalog_results += tuple(self.catalog(self.REQUEST,
                                                          **query))

        result = utils.build_catalog_results(self.id, self.catalog._catalog,
                                             catalog_results)
        return result


manage_addTranslationIndexForm = DTMLFile('dtml/addFakeIndex', globals())

def manage_addTranslationIndex(self, id, extra=None, REQUEST=None,
                               RESPONSE=None, URL3=None):
    """Add a fake index"""
    return self.manage_addIndex(id, 'TranslationIndex', extra=extra,
                REQUEST=REQUEST, RESPONSE=RESPONSE, URL1=URL3)