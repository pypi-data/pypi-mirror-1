from zope.interface import implements
from zope.component import getMultiAdapter
from Products.CMFCore.utils import getToolByName
from collective.portlet.dropdownbox.interfaces import ILinksBuilder, ILinkItemBuilder



class LinkItemBuilder(object):

    implements(ILinkItemBuilder)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def portal(self):
        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        return portal_state.portal()
        
    @property
    def portal_properties(self):
        return getToolByName(self.portal, 'portal_properties')
        
    @property
    def site_properties(self):
        return getToolByName(self.portal_properties, 'site_properties')

    @property
    def view_action_types(self):
        return self.site_properties.getProperty('typesUseViewActionInListings', ())
        
    def link_item(self, brain=None):
        dic = {
            'title': brain.Title,
            'description': brain.Description,
            'url' : brain.getURL(), 
        }
        
        # TODO: a link in a ATLink could be an internal / relative link
        # like /news - try to implement a solution that takes care of this use case also.
        # Though if redirect_to() still are used in dropdownbox.py then its not urgent
        # it handle usecase with internal urls link /news
        
        # use getRemoteUrl if its available
        if brain.getRemoteUrl:
            dic['url'] = brain.getRemoteUrl
        elif brain.portal_type in self.view_action_types:
            # support portal types requiring '/view'
            dic['url'] += '/view'
        return dic


class LinksBuilder(object):

    implements(ILinksBuilder)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def portal(self):
        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        return portal_state.portal()

    @property
    def portal_catalog(self):

        return getToolByName(self.portal, 'portal_catalog')

    def links(self, obj):

        # is it ok to use the getPhysicalPath() here ? 
        path =  '/'.join(obj.getPhysicalPath())
        search_results = self.portal_catalog.searchResults(
            
            # TODO: not sure about the review state thing, if no review_state is set
            # the tests should a least cover taht it dont break any thing permission wize
            # though a catalog query should handle this properly relayted to the corrent user
            # review_state='published',
            path = {'query' : path, 'depth' : 1}, 
            sort='getObjPositionInParent', 
        )
        results = []
        if search_results:
            link_item_helper = getMultiAdapter((self.context, self.request), ILinkItemBuilder)
            for item in search_results:
                results.append(link_item_helper.link_item(brain=item))                    
        return results


class CollectionLinksBuilder(object):

    implements(ILinksBuilder)

    def __init__(self, context, request):
        self.context = context
        self.request = request

        
    def links(self, obj):
        search_results = obj.queryCatalog()
        results = []
        if search_results:
            link_item_helper = getMultiAdapter((self.context, self.request), ILinkItemBuilder)
            for item in search_results:
                results.append(link_item_helper.link_item(brain=item))                    
        return results
        
        