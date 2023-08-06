from collective.feedfiller.events import FeedItemExpandedEvent
from collective.feedfiller.flayregistry import FlayRegistry
from collective.feedfiller.adapters import FeedItemExpanderAdapter
from zope import event
import urllib2
import transaction
import logging
log = logging.getLogger('Feedfiller.Filler')


class Filler(object):
    def fill(self, item):
        """
        fills an adapted item by looking up a flayer for the item's
        link url, and inserting flayer results in the original item.
        If it can't find a body, then it assumes the page has changed
        so it gets the default flay
        Returns True if success.
        """
        text = item.getText()
        if text:
            log.warning( "item already filled by feed %s" % item )
            
        link = item.link
        if not link:
            log.warning( "item has no link - cannot expand %s" % item )
            return False
        
        log.info( "expanding %s from %s" % (item, link) )
        
        try:
            
            (subpath, flayer) = FlayRegistry.lookup(link)
            results = flayer(link)()
            
            
            if not results.get('body'):
                # our existing registry is now failing us.
                # The body was not parseable - do a default flay since
                # style has changed, or content is now gated (e.g. NYT).
                log.warning( "Falling Back - no body from %s" % flayer.__name__ )
                (subpath, flayer) = FlayRegistry.lookup(link, default=True)
                results = flayer(link)()
                
            expanded = FeedItemExpanderAdapter(item)
            expanded.update(results)
            if results.get('url') and results['status'] in [301, 302]:
                expanded.set_expanded_proxy_url(item.link)
                item.link=results['url']
            expanded.set_expanded_status(results['status'])
            item.indexObject()
            event.notify(FeedItemExpandedEvent(item))
            transaction.savepoint() 
            log.info( "item expanded %s from %s" % (item, link) )
            return True
            
        except urllib2.HTTPError:
            log.warning( "Handler: 404 grabbing for %s " % item )

        except:
            log.exception( "Handler: Exception grabbing for %s " % item )
