from zope import interface
try:
    from zope.lifecycleevent import ObjectModifiedEvent
    ObjectModifiedEvent # pyflakes
except ImportError:
    # BBB for Zope 2.9
    from zope.app.event.objectevent import ObjectModifiedEvent
from collective.feedfiller.interfaces import IFeedItemExpandedEvent


class FeedItemExpandedEvent(ObjectModifiedEvent):
    """Fired when a feed item has been successfully consumed.
    """

    interface.implements(IFeedItemExpandedEvent)