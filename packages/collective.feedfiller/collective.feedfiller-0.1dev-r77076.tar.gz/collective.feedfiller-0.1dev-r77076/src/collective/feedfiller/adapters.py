# -*- coding: utf-8 -*-

from zope import interface
from interfaces import IExpandedFeedItem
from utils import get_storage
import logging
log = logging.getLogger('Feedfiller.Adapters')



class FeedItemExpanderAdapter(object):
   """
   An adapter for a feedfeeder item

    >>> from zope.interface.verify import verifyClass
    >>> from collective.feedfiller.interfaces import IExpandedFeedItem
    >>> from collective.feedfiller.adapters import FeedItemExpanderAdapter
    >>> verifyClass(IExpandedFeedItem, FeedItemExpanderAdapter)
    True

   """
   interface.implements(IExpandedFeedItem)

   def __init__(self, context):
       self.context = context

   def set_expanded_body(self, filleted):
       assert type(filleted) == unicode
       self.context.expanded_body = filleted

   def get_expanded_body(self):
       return self.context.get('expanded_body',u'')



   def set_expanded_author(self, author):
       assert type(author) == unicode
       self.context.expanded_author = author

   def get_expanded_author(self):
       return self.context.get('expanded_author', u'')



   def set_expanded_copyright(self, cright):
       assert type(cright) == unicode
       self.context.expanded_copyright = cright

   def get_expanded_copyright(self):
       return self.context.get('expanded_copyright', u'')



   def set_expanded_status(self, status):
#       assert type(status) == int
       self.context.expanded_status = status

   def get_expanded_status(self):
       return self.context.get('expanded_status', None)



   def set_expanded_proxy_url(self, url):
       self.context.expanded_proxy_url = url

   def get_expanded_proxy_url(self):
       return self.context.get('expanded_proxy_url', u'')



   def update(self, dic):
       # rekey the url item
       if dic.get('url'):
           dic['proxy_url']=dic['url']
           del dic['url']
       #set the attr with matching name
       for k in dic.keys():
           name = 'set_expanded_%s' % k
           if hasattr(self, name):
               meth = self.__getattribute__(name)
               meth(dic[k])
           else:
               log.warning('No such method %s for attr %s' % (name, k))


