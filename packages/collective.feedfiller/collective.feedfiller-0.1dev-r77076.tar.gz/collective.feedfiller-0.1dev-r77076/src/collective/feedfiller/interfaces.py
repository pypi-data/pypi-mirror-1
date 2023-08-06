# -*- coding: utf-8 -*-

from zope import interface

class IPageFlayer(interface.Interface):
    '''Takes the skin off a page, and accesses the vital organs...'''

    root = interface.Attribute("Root")

    example = interface.Attribute("Example")

    body_test = interface.Attribute("Body Test String - will be present to pass")

    author_test = interface.Attribute("Author Test String - will be present to pass")

    copyright_test = interface.Attribute("Copyright Test String - present to pass")

    def condition_url(url):
        """process the url so that it can ask for all content on 1 page"""
    def snip_body(): 
        """return the body of the page as unicode"""
    def snip_author():
        """return the author as unicode"""
    def snip_copyright():   
        """return the copyright as unicode"""

class IExpandedFeedItem(interface.Interface):
    ''' A feed item that has added content'''

    def set_expanded_original(raw):
        '''attach raw data from the target page as unicode'''

    def get_expanded_original():
        '''return raw data from the target page'''
 
        
    def set_expanded_body(filleted):
        '''attach filleted data from the target page as unicode'''

    def get_expanded_body():
        '''return filleted data from the target page'''
 
        
    def set_expanded_author(author):
        '''sets author as clean unicode from target page'''
        
    def get_expanded_author():
        '''return the author as clean unicode from target page'''
 
        
    def set_expanded_copyright(cright):
        '''sets the copyright as clean unicode from target page'''
        
    def get_expanded_copyright():
        '''return the copyright as clean unicode from target page'''
 
   
    def set_expanded_status(HTTPstatus):
       '''store the status of the fetch'''

    def get_expanded_status():
       ''''''


    def set_expanded_proxy_url(url):
       '''store the url we had before we arrived at the target'''

    def get_expanded_proxy_url():
       ''''''

        
    def update(dic):
        '''updates matching attrs from dic'''

try:
    from zope.lifecycleevent import IObjectModifiedEvent
except ImportError:
    # BBB for Zope 2.9
    from zope.app.event.interfaces import IObjectModifiedEvent

class IFeedItemExpandedEvent(IObjectModifiedEvent):
    '''Intended to be fired after a new feed item has been successfully
    expanded.
    '''        