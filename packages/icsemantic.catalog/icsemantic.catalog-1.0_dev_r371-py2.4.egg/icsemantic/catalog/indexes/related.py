# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: related.py 275 2008-06-13 23:21:56Z esmenttes $
#
# end: Platecom header
"""RelatedIndex is an index for the catalog that does not index
anything.

Instead, the _apply_index performs a query to a thesaurus object for
related words of the keyword parameters and then queries the site
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


class RelatedIndex(Persistent, SimpleItem):
    """An index for related words that does not index anything"""

    __implements__ = (PluggableIndex.PluggableIndexInterface,)
    implements(IPluggableIndex)

    meta_type = "RelatedIndex"
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
        query_options = ('query', 'contexts')
        record = parseIndexRequest(request, self.id, query_options)
        if record.keys is None:
            return None

        #Languages dance
        langutil = queryUtility(IUserPreferredLanguages,
                                name='icsemantic_preferred_languages')
        user_languages = tuple(langutil.getPreferredLanguages(request=self.REQUEST))

        contexts = record.get('contexts', None)

        if contexts == ['']:
            contexts = None

        thesaurus_results = []
        catalog_results = ()
        for k in record.keys:
            for lang in  user_languages:
                key = '%s@%s' % (k, lang)
                thesaurus_results += utils.get_related(portal, key,
                                                       lang=user_languages,
                                                       contexts=contexts)

                if thesaurus_results != []:
                    tuples = [tl.split('@') for tl in thesaurus_results]
                    related = ['\"%s\"' % (t,) for (t,l) in tuples]
                    search_text = ' OR '.join(related)
                    query = {'SearchableText': search_text,
                             'Language': user_languages}
                    catalog_results += tuple(self.catalog(self.REQUEST,
                                                          **query))

        result = utils.build_catalog_results(self.id, self.catalog._catalog,
                                             catalog_results)
        return result


manage_addRelatedIndexForm = DTMLFile('dtml/addFakeIndex', globals())

def manage_addRelatedIndex(self, id, extra=None, REQUEST=None, RESPONSE=None,
                           URL3=None):
    """Add a fake index"""
    return self.manage_addIndex(id, 'RelatedIndex', extra=extra,
                REQUEST=REQUEST, RESPONSE=RESPONSE, URL1=URL3)
