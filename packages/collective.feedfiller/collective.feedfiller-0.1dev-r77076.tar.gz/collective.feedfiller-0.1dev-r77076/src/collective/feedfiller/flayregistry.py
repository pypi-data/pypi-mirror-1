# -*- coding: utf-8 -*-
import urlparse
import flay

class FlayRegistry:
    """
    A singleton registry to lookup the current class/id/path
    matching criteria for a screen scraper, by URL.
    
    The returned results are sufficient to scrape out the body of the page
    using Beautiful Soup.
    
    We need this over a zope.component registry due to the specificity
    of the lookup within a host.
    
    Let's demo/test
    >>> from collective.feedfiller.flayregistry import FlayRegistry
    >>> reg = FlayRegistry()
    
    Ordinary lookups, first for a site that we crack by CSS class.
    >>> path, flayer = reg.lookup('http://news.bbc.co.uk/1/hi/uk/7648664.stm')
    >>> print path, flayer.__name__
    None FlayBBCNews

    
    Test aliases - both should work - with or without www
    >>> ua='http://www.ft.com/cms/s/0/41f6c75e-90a0-11dd-8abb-0000779fd18c.html'
    >>> fta = reg.lookup(ua)
    >>> ub='http://ft.com/cms/s/0/41f6c75e-90a0-11dd-8abb-0000779fd18c.html'    
    >>> ftb = reg.lookup(ub)
    >>> fta == ftb
    True
    >>> fta
    (None, <class 'collective.feedfiller.flay.FlayFTDotCom'>)
    
    Try a subpath, under which we find a special flayer
    >>> from collective.feedfiller import flay
    >>> class newflayer(flay.FlayBase):
    ...     root='news.bbc.co.uk/NONEWS/IS/GOOD/NEWS'
    ...
    >>> reg.add(newflayer)
    >>> path, flayer = reg.lookup('http://news.bbc.co.uk/NONEWS/IS/GOOD/NEWS/hi/uk/7648664.stm')
    >>> print flayer.__name__
    newflayer
    
    
    And if we are not under that subpath we still get the normal flayer
    >>> print reg.lookup('http://news.bbc.co.uk/1/hi/uk/7648664.stm')
    (None, <class 'collective.feedfiller.flay.FlayBBCNews'>)
    
    A match can be updated by adding again
    >>> class newflayer2(flay.FlayBase):
    ...     root='news.bbc.co.uk/NONEWS/IS/GOOD/NEWS'
    ...
    >>> reg.add(newflayer2)
    >>> path, flayer = reg.lookup('http://news.bbc.co.uk/NONEWS/IS/GOOD/NEWS/hi/uk/7648664.stm')
    >>> print flayer.__name__
    newflayer2
    
    The longest match is returned
    >>> class newflayer3(flay.FlayBase):
    ...     root='news.bbc.co.uk/NONEWS/IS/GOOD/NEWS'
    ...
    >>> reg.add(newflayer3)
    >>> path, flayer = reg.lookup('http://news.bbc.co.uk/NONEWS/IS/GOOD/hi/uk/7648664.stm')
    >>> print  path, flayer 
    None <class 'collective.feedfiller.flay.FlayBBCNews'>

    >>> path, flayer =  reg.lookup('http://news.bbc.co.uk/NONEWS/IS/GOOD/NEWS/hi/uk/7648664.stm')
    >>> print  path, flayer 
    /NONEWS/IS/GOOD/NEWS <class 'newflayer3'>
    
    >>> path, flayer =  reg.lookup('http://news.bbc.co.uk/NONEWS/IS/GOOD/hi/uk/7648664.stm')
    >>> print  path, flayer 
    None <class 'collective.feedfiller.flay.FlayBBCNews'>
        
    """
    sites = {}

    #KLASS   = 0
    #ID      = 1
    PATHSEG = 0
    
    @classmethod
    def lookup(cls, url, default=False):
        """    
        returns the path and a flayer    
        """
        parsed = urlparse.urlparse(url)
        host, path = parsed[1:3]
        if default:
            host=''
        matches = cls.sites.get(host, None)
        if matches is None: 
            # This host has no entries so get a default for the protocol
            host = ''
            matches = cls.sites.get(host, None)
        
        # Host has entries. See if it has matching subpaths
        # and return the longest matching
        pathmatches = [m for m in matches if m[cls.PATHSEG] and path.startswith(m[cls.PATHSEG]) ]
        if pathmatches:
            if len(pathmatches) > 0:
                def cmp_pathseg_len(x,y):
                    #we want longest first
                    return cmp(len(y[cls.PATHSEG]), len(x[cls.PATHSEG]))
                pathmatches.sort(cmp_pathseg_len)
            match = pathmatches[0]
            return match[0:2]
            
        #We should not see more than one pathless match for a site
        match = matches[0]
        return match[0:2]
            
    @classmethod    
    def add(cls, flayer):
        """
        def add(cls, host, klass=None, id=None, pathseg=None):
        
        """
        #adapt to the old ways...
        host=flayer.get_root()
        
        #standardise input 
        if '//' not in host:
            host = 'http://%s' % host
        
        # remove any http:// or feed:// and get pathseg
        parsed = urlparse.urlparse(host)
        host = parsed[1]
        pathseg = parsed[2]
        if not pathseg:
            pathseg = None

        # ensure a site is there
        v = (pathseg, flayer)
        site = cls.sites.setdefault(host, [])
        
        #delete any existing match with same pathseg
        matches = [match for match in site if match[cls.PATHSEG] == pathseg]
        for item in matches:
            site.remove(item)
        
        site.append(v)
        
        #register the aliases we already know about
        for alias in flayer.get_aliases():
            cls.addAlias(host, alias)
        
    @classmethod    
    def addAlias(cls, host, *aliases):
        """        
        """
        
        #standardise input 
        if '//' not in host:
            host = 'http://%s' % host
        
        # remove any http:// or feed:// and get pathseg
        parsed = urlparse.urlparse(host)
        host = parsed[1]
        
        for a in aliases:
            v = cls.sites.setdefault(host, [])
            cls.sites[a] = v
        
from flay import flayers
for flayer in flayers:
    FlayRegistry.add(flayer)
    

if __name__ == "__main__":
    import urllib2
    import logging
    logging.basicConfig()
    log = logging.getLogger('Feedfiller.SiteReg')
    log.setLevel(logging.DEBUG)
    log.debug('starting')
    
    from flay import flayers
    for flayer in flayers:
        FlayRegistry.add(flayer)
    
    # and try one.
    link = 'http://www.expressandstar.com/2008/11/29/two-men-killed-in-collisions/'
    log.info( "expanding from %s" % (link,) )
    try:
        (subpath, flayer) = FlayRegistry.lookup(link)
        flayer = flayer(link)
        results = flayer()
        log.debug('results:: %s' % results)
        log.info( "item expanded from %s" % link )
    except urllib2.HTTPError:
        log.warning( "Handler: 404 grabbing for %s " % link )
    except:
        log.exception( "Handler: Exception grabbing for %s " % link )


