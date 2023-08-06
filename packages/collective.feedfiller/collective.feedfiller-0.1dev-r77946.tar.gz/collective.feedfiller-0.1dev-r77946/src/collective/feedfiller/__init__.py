from zope.i18nmessageid import MessageFactory

FeedfillerMessageFactory = MessageFactory('collective.feedfiller')

def initialize(context):
    """Initializer called when used as a Zope 2 product."""
