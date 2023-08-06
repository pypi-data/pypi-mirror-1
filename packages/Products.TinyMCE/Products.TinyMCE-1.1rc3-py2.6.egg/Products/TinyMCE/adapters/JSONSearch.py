from zope.interface import implements
from zope.component import adapts
from zope.component import getUtility
from z3c.json import interfaces
from z3c.json import testing

from Products.TinyMCE.interfaces.utility import ITinyMCE
from Products.TinyMCE.adapters.interfaces.JSONSearch import IJSONSearch
from Products.CMFCore.interfaces._content import IContentish, IFolderish
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from Products.CMFPlone.interfaces import INonStructuralFolder
from Products.CMFPlone import utils
from Products.CMFCore.utils import getUtilityByInterfaceName
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_inner

class JSONSearch(object):
    """Returns a list of search results in JSON"""
    implements(IJSONSearch)

    def __init__(self, context):
        """Constructor"""
        self.context = context

    def getInfoFromBrain(self, brain):
        """Gets information from a brain id, url, portal_type, title, icon, is_folderish"""

        id = brain.getId
        uid = brain.UID
        url = brain.getURL()
        portal_type = brain.portal_type
        title = brain.Title
        icon = brain.getIcon
        is_folderish = brain.is_folderish

        return {
        'id': id,
        'uid': uid,
        'url': url,
        'portal_type': portal_type,
        'title' : title,
        'icon' : icon,
        'is_folderish' : is_folderish
        }

    def getSearchResults(self, filter_portal_types, searchtext):
        """Returns the actual search result"""

        catalog_results = []
        results = {}

        results['parent_url'] = ''
        results['path'] = []

        if searchtext:
            for brain in self.context.portal_catalog.searchResults({'SearchableText':'%s*' % searchtext, 'portal_type':filter_portal_types, 'sort_on':'sortable_title'}):
                catalog_results.append(self.getInfoFromBrain(brain))

        # add catalog_ressults
        results['items'] = catalog_results 

        # return results in JSON format
        testing.setUpJSONConverter()
        jsonWriter = getUtility(interfaces.IJSONWriter)
        return jsonWriter.write(results)
