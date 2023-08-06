from time import time

from zope.interface import implements
from Products.CMFCore.utils import getToolByName

from quintagroup.portlet.cumulus.interfaces import ITagsRetriever
from quintagroup.portlet.cumulus.catalog import GlobalTags

from plone.memoize import ram

def _cachekey(method, self, path):
    """Time, language, settings and member based cache
    """
    membership = getToolByName(self.context, 'portal_membership')
    lang = self.context.REQUEST.get('LANGUAGE', 'en')
    memberid = membership.getAuthenticatedMember()
    return hash((lang, memberid, path, time() // self.data.refreshInterval))

class DummyData(object):
    path = None

class LocalTags(GlobalTags):
    implements(ITagsRetriever)

    def __init__(self, context):
        GlobalTags.__init__(self, context)
        self.portal = getToolByName(context, 'portal_url')
        self.data = DummyData()

    def getTags(self, number=None, data=None):
        """ Entries of 'Categories' archetype field on content are assumed to be tags.
        """
        if data:
            self.data = data
        cat = getToolByName(self.context, 'portal_catalog')
        index = cat._catalog.getIndex('Subject')
        tags = []
        if not self.data.path:
            tags = self.getGlobalTags(number)
        else:
            tags = self.getLocalTags(number)
        return tags

    
    def getPath(self, path):
        result = path
        ppath = self.portal.getPortalPath()
        if result.startswith('/'):
            if not result.startswith(ppath):
                result = ppath + result
        else:
            result = '/'.join(list(self.context.getPhysicalPath())+[result])
        return result
 
    @ram.cache(_cachekey)
    def getSubKeywords(self, path):
        cat = getToolByName(self.context, 'portal_catalog')
        brains = cat.searchResults(**{'path': path})
        tags = {}
        for brain in brains:
            for key in brain.Subject:
                if not key in tags:
                    tags[key] = 0
                tags[key] += 1
        return tags

    def getLocalTags(self, number=None):
        """ Entries of 'Categories' archetype field on content are assumed to be tags.
        """
        path = self.getPath(self.data.path)
        tags = self.getSubKeywords(path)
        res = []
        for name in tags:
            name = name.decode(self.default_charset)
            url = '%s/search?path=%s&Subject:list=%s' % (self.portal_url, path, name)
            res.append((name, tags[name], url))
        if number:
            if number >= res: number = res
            res = res[:number]
        return res


    def getGlobalTags(self, number=None):
        """ Entries of 'Categories' archetype field on content are assumed to be tags.
        """
        return GlobalTags.getTags(self, number)

