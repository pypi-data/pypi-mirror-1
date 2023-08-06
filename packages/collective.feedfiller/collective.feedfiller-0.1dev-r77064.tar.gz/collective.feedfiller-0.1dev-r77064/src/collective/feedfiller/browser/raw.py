
from Acquisition import aq_inner

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.memoize.instance import memoize

from collective.feedfiller.interfaces import IExpandedFeedItem


class RawView(BrowserView):
    """Raw view of a FeedItem's collected target data
    """
    
    __call__ = ViewPageTemplateFile('raw.pt')
            
    @memoize
    def body(self):
        context = aq_inner(self.context)
        return IExpandedFeedItem(context).get_expanded_body
        
    @memoize
    def author(self):
        context = aq_inner(self.context)
        return IExpandedFeedItem(context).get_expanded_author
        
    @memoize
    def copyright(self):
        context = aq_inner(self.context)
        return IExpandedFeedItem(context).get_expanded_copyright
        
    @memoize
    def original_url(self):
        context = aq_inner(self.context)
        return context.link
        