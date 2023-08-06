from zope import interface

from Products.feedfeeder.interfaces.consumer import IFeedConsumer
from Products.feedfeeder.interfaces.item import IFeedItem
from Products.feedfeeder.interfaces.container import IFeedsContainer

from Products.CMFCore.utils import getToolByName
from collective.feedfiller.filler import Filler

import logging
log = logging.getLogger('Feedfiller.Browser')

filler = Filler()

class IsFeedItem(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def is_feeditem(self):
        return IFeedItem.providedBy(self.context)


class IRefillFeedItem(interface.Interface):

    def update():
        pass

class RefillFeedItem(object):
    """A view for refilling the feed items in a feed folder.
    """

    interface.implements(IRefillFeedItem)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def refill(self):                    
        item=self.context                    
        self.success = filler.fill(item)  
            
    def __call__(self):
        
        self.refill()
        
        self.request.response.redirect(
            self.context.absolute_url()
            +"?portal_status_message=Feed+item+refilled")

class IRefillFeedItems(interface.Interface):

    def update():
        pass

class RefillFeedItems(object):
    """A view for refilling the feed items in a feed folder.
    """

    interface.implements(IRefillFeedItems)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def refill(self):
        listing = self.context.getFolderContents
        items = listing({'sort_on': 'getFeedItemUpdated',
                           'sort_order': 'descending',
                           'portal_type': 'FeedFeederItem'})
        success = [0,0]
        
        for item in items:
            
            item=item.getObject()
            
            if filler.fill(item): 
                success[0] += 1
            else: 
                success[1] += 1
            
        self.success=tuple(success)

    def __call__(self):
        
        self.refill()
        
        self.request.response.redirect(
            self.context.absolute_url()
            +"?portal_status_message=%s+Feed+items+refilled. %s failed" % self.success)

class IUpdateAllFeeds(interface.Interface):

    def update():
        pass

class FeedUpdater(object):
    """Triggers update from the feed source for all feeds"""
    
    interface.implements(IUpdateAllFeeds)

    def __init__(self, context, request):
        self.context = context
        self.request = request
    
    def update(self):
        log.info("updating all feeds")
        pc = getToolByName(self.context, "portal_catalog")
        brains = pc(portal_type="FeedfeederFolder")
        success=[0,0]
        for brain in brains:
            f = brain.getObject()
            view = f.restrictedTraverse("update_feed_items")
            try:
                log.debug("updating feed %s" % (view.context.Title()))
                view.update()
                log.info("updated feed %s" % (view.context.Title()))
                success[0]+=1
            except:
                success[1]+=1
                log.warning("ERROR updating feed %s" % (view.context.Title()))
        self.success=tuple(success)
        log.info("updated feeds. %s succeeded, %s failed" % self.success)
                
    def __call__(self):
        self.update()
        self.request.response.redirect(
            self.context.absolute_url()
            +"?portal_status_message=%s+Feeds+updated++%s+Feeds+failed" % self.success)


class IRefillAllFeeds(interface.Interface):

    def update():
        pass

class FeedRefiller(object):
    """Triggers update from the feed source for all feeds"""
    
    interface.implements(IRefillAllFeeds)

    def __init__(self, context, request):
        self.context = context
        self.request = request
    
    def refill_all(self):
        log.info("refilling all feeds")
        pc = getToolByName(self.context, "portal_catalog")
        brains = pc(portal_type="FeedfeederFolder")
        success=[0,0]
        for brain in brains:
            f = brain.getObject()
            view = f.restrictedTraverse("refill_feed_items")
            try:
                log.debug("refilling feed %s" % (view.context.Title()))
                view.refill()
                log.info("refilled feed %s" % (view.context.Title()))
                success[0]+=1
            except:
                success[1]+=1
                log.warning("ERROR refilling feed %s" % (view.context.Title()))
        self.success=tuple(success)
        log.info("refilled feeds. %s succeeded, %s failed" % self.success)
                
    def __call__(self):
        self.refill_all()
        self.request.response.redirect(
            self.context.absolute_url()
            +"?portal_status_message=%s+Feeds+refilled++%s+Feeds+failed" % self.success)
