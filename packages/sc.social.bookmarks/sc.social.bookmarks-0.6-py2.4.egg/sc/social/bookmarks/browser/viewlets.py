
from zope.component import getMultiAdapter, queryMultiAdapter, getUtility
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from plone.app.layout.viewlets import ViewletBase
from plone.memoize.view import memoize
from sc.social.bookmarks.config import all_providers

class SocialBookmarksViewlet(ViewletBase):
    """
    """
    render = ViewPageTemplateFile("templates/bookmarks.pt")
    
    def __init__(self, context, request, view, manager):
        super(SocialBookmarksViewlet, self).__init__(context, request, view, manager)
        pp = getToolByName(context,'portal_properties')
        if hasattr(pp,'sc_social_bookmarks_properties'):
            self.bookmark_providers = pp.sc_social_bookmarks_properties.getProperty("bookmark_providers") or []
            self.enabled_portal_types = pp.sc_social_bookmarks_properties.getProperty("enabled_portal_types") or []
        else:
            self.bookmark_providers = []
            self.enabled_portal_types = []
    @memoize
    def _availableProviders(self):
        """
        """
        bookmark_providers = self.bookmark_providers
        providers=[]
        for provider in all_providers:
            
            pId = provider.get('id','')
            if (not pId) or (not(pId in bookmark_providers)):
                continue
            logo = provider.get('logo','')
            url = provider.get('url','')
            providers.append({'id':pId,'logo':logo,'url':url})
        
        return providers
    
    def providers(self):
        """Returns a list of dicts with providers already
           filtered and populated"""
        available = self._availableProviders()
        providers = []
        param = {}
        param['title'] = self.context.Title()
        param['description'] = self.context.Description()
        param['url'] = self.context.absolute_url()
        for provider in available:
            provider['url'] = provider['url'] % param
            providers.append(provider)
        return providers
    
    def enabled(self):
        """Validates if the viewlet should be enabled 
           for this context"""
        context = self.context
        enabled_portal_types = self.enabled_portal_types
        return context.portal_type in enabled_portal_types
