# -*- coding: utf-8 -*-
"""
Class hierarchy for flaying various news provider sites.
If overriding flay(), duplicate the __call__ line, also.

First part of a root is canonical, others aliases

"""     
import urllib,urllib2, urlparse
from BeautifulSoup import BeautifulSoup, Comment
from openanything import fetch
from interfaces import IPageFlayer
from zope import interface

from time import time
import re

import logging
log = logging.getLogger('Feedfiller.Flay')

# registers which hosts already have openers installed, to save
# the effort of doing it over.
opener_installed={}

# Many UK local papers use google news feeds, which specifically 
#  403 urllib* requests. Bugger that!
userAgent = 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.5; en-US; rv:1.9.0.4) Gecko/2008102920 Firefox/3.0.4'

class FlayBase(object):
    """
    The abstract flayer providing common services, behaviour, and 
    default methods

     >>> from zope.interface.verify import verifyClass
     >>> from collective.feedfiller.interfaces import IPageFlayer
     >>> from collective.feedfiller.flay import FlayBase
     >>> verifyClass(IPageFlayer, FlayBase)
     True

    """
    interface.implements(IPageFlayer)
    
    def __init__(self, url):
        log.debug('Base. URL: %s' % url)        
        try:
            link=self.condition_url(url)
            self.link=link
            log.debug('conditioned : %s' % link)
            self._register_login_credentials(link)
            if not hasattr(self, 'results'):
                self.results={}
            if not self.results.get('original'):
                self.f=fetch(link, agent=userAgent )
                self.results['original'] = self.f['data']  # development aid...
                self.results['url']=self.f.get('url', link)
                self.results['status']=self.f.get('status')
            else:
                # we are retrying the Flay and don't need to fetch.
                # the status will remain unchanged
                # the data are in results['original']
                pass
                
            self.soup = BeautifulSoup(self.results['original'])
        except urllib2.HTTPError:
            log.warning( "FlayBase: 404 for %s " % url )
        except Exception:
            log.exception("Net error: %s" % url)
            raise
            
    @classmethod
    def set_root(cls, root):
        cls.root = root
    
    def _register_login_credentials(self, link): pass
    def _add(self,**kwargs):
        self.results.update(kwargs)
    def _extract_paired_comment(self, soup, start, end):
        # start and end are identifying contents of the comment
        startcomment = soup.find(text=re.compile(start))
        if startcomment is None: return None
        extracted = ''
        while extracted != end:
            extracted = startcomment.nextSibling.extract()
        startcomment.extract()
        return True
    def _extract_element_by_class(self, soup, HTMLelname, cssClass):
        el = soup.find(HTMLelname, {'class':cssClass})
        if el is None: return None
        return el.extract()
    def _extract_element_by_id(self, soup, cssId):
        el = soup.find(id=cssId)
        if el is None: return None
        return el.extract()
    def _extract_elements_by_type(self, soup, HTMLelname):
        [el.extract() for el in soup.findAll(HTMLelname)]
    def _extract_comment_and_next_element(self, soup, comment_text):
        startcomment = soup.find(text=re.compile(comment_text))
        startcomment.next.next.extract()
        startcomment.extract()
    def _extract_comments(self, soup):
        comments = soup.findAll(text=lambda text:isinstance(text, Comment))
        [comment.extract() for comment in comments]
    def _common_extractions(self, soup):
        """Removes all the items that we never want. Call it late."""
        self._extract_elements_by_type(soup, 'script')
        self._extract_elements_by_type(soup, 'form')
        self._extract_elements_by_type(soup, 'img')
        self._extract_elements_by_type(soup, 'iframe')
        self._extract_elements_by_type(soup, 'object')
        self._extract_elements_by_type(soup, 'embed')
        self._extract_comments(soup)
        return soup
    def _tidy_and_return_in_common_body_format(self, body):
        """This is the final method to call on a body"""
        body = self._common_extractions(body)
        body=unicode(' '.join([unicode(i) for i in body.contents]))
        self._add(body=body)  
    def _check_results(self):
        """ensure only strings or ints are returned - No soup dregs!"""
        res=self.results
        ok=[str,unicode, int]
        bad=[(k,type(res[k])) for k in res.keys() if not type(res[k]) in ok ]
        for i in bad:
            log.warning( "err key: %s, type: %s" % i )
    def _final_cleanup(self):
        del self.soup
        
    @classmethod
    def test(klass):
        log.info('testing: %s' % klass.__name__)
        link=klass.example
        res = klass(link)()
        def check(klass, res, attrname):
            attr=res.get(attrname)
            if attr:
                testname=attrname+'_test'
                try:
                    sample = klass.__dict__[testname]
                except KeyError:
                    rr = (klass.__name__, testname, attr)
                    log.warning('Class: %s missing test "%s". Attr: %s' % rr)
                    return # give up
                  
                if not sample in attr:
                    rr = (klass.__name__, sample, attr)
                    log.warning('Class: %s result %s missing from "%s"' % rr)
        check(klass, res, 'body')
        check(klass, res, 'author')
        check(klass, res, 'copyright')
        log.info('tested: %s' % klass.__name__)
    @classmethod
    def get_root(cls):
        return cls.root.split()[0]     
    @classmethod
    def get_aliases(cls):
        return cls.root.split()[1:]     
    def snip_author(self):    pass
    def snip_body(self):      pass
    def snip_copyright(self): pass
    def condition_url(self, url): return str(url)
    def flay(self):
        assert hasattr(self,'root')
        assert hasattr(self,'example')
        link = self.link
        try: self.snip_author()
        except: log.exception('snip_author in %s', self.link )
        try: self.snip_body()
        except: log.exception('snip_body in %s', self.link )
        try: self.snip_copyright()
        except: log.exception('snip_copyright in %s', self.link )
        self._check_results()
        self._final_cleanup
        return self.results
    __call__ = flay

def AddCookieProcessor(link, username, password):
    host=urlparse.urlparse(link)[2]
    time_installed=opener_installed.get(host)
    if time_installed:
        rr = (host,time_installed,)
        log.debug("opener already installed. host: %s time: %s" % rr)
        return
    params = urllib.urlencode(dict(username=username, password=password))
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
    urllib2.install_opener(opener)
    opener_installed[host]=time()
    
class FlayAlternet(FlayBase):
    """
     >>> from zope.interface.verify import verifyClass
     >>> from collective.feedfiller.interfaces import IPageFlayer
     >>> from collective.feedfiller.flay import FlayAlternet
     >>> verifyClass(IPageFlayer, FlayAlternet)
     True
     
    This site has a default splitPage:
    http://www.alternet.org/workplace/108622/while_some_of_us_are_hoping_for_change%2C_others_are_literally_starving_for_it/
    http://www.alternet.org/workplace/108622/while_some_of_us_are_hoping_for_change%2C_others_are_literally_starving_for_it/?page=entire
    """
    root='http://www.alternet.org alternet.org'
    example='http://www.alternet.org/workplace/108622/while_some_of_us_are_hoping_for_change%2C_others_are_literally_starving_for_it/'
    body_test='Crisis Ministry'
    author_test='Chris Hedges'
    copyright_test='&copy;'
    def __init__(self, stream):
        FlayBase.__init__(self, stream)
    def condition_url(self,url):
        entireflag='?page=entire'
        if url.endswith(entireflag):
            return url
        return url+entireflag
    def snip_body(self):
        """snip the el with cssId storycontainer
        1. remove
            <!-- extra digg icon -->
            <p>
             <a href="http://digg.com/submit?phase=2&amp;url=http://www.alternet.org/workplace/108622&amp;title=While Some of Us Are Hoping for Change, Others Are Literally Starving for It&amp;topic=politics" rel="external" title="Digg it!" target="_blank">
              <img src="/images/social/85x10-digg-link.gif" width="85" height="10" alt="Digg!" border="0" />
             </a>
            </p>
        
        2. remove
            <!-- if tagged posts -->
            <p class="smalltitle">
             See more stories tagged with:
             <b>
              <a href="/tags/poverty/">
               poverty
              </a>
              ,
              <a href="/tags/food banks/">
               food banks
              </a>
             </b>
            </p>
        """
        cssId='storycontainer'
        body = self.soup.find(id=cssId)
        self._extract_comment_and_next_element(body, 'extra digg icon')
        self._extract_comment_and_next_element(body, 'if tagged posts')
        self._tidy_and_return_in_common_body_format(body)
    def snip_author(self):
        """snip the p with class storybyline. get the contents of the next
        anchor.
        ...
        <p class="storybyline">
            <b>By <a title="View all stories by Chris Hedges" href="/authors/5769/">Chris Hedges</a> , 
                <a href="http://www.truthdig.com/">Truthdig</a> . 
            Posted 
              <a title="View all stories published on November 27, 2008" 
              href="/ts/archives/?date[F]=11&amp;date[Y]=2008&amp;date[d]=27&amp;act=Go/">November 27, 2008</a> .
            </b>
        </p>
        """
        byline = self.soup.find('', { "class" : 'storybyline' })
        author = unicode(byline.a.contents[0])
        self._add(author=author)
    def snip_copyright(self):
        """
        <div id="footer">
        <ul>
        </ul>
        <p>
        Reproduction of material from any AlterNet pages without written permission is strictly prohibited.
        <br/>
        © 2008 Independent Media Institute. All rights reserved.
        </p>
        </div>        """
        cssId="footer"
        cblock = self.soup.find(id=cssId)
        cright = cblock.prettify().split('<br />')[1].replace('\n','').replace('</p>','').strip()
        self._add(copyright=cright)

class FlayBBCNews(FlayBase):
    """
    >>> from zope.interface.verify import verifyClass
    >>> from collective.feedfiller.interfaces import IPageFlayer
    >>> from collective.feedfiller.flay import FlayBBCNews
    >>> verifyClass(IPageFlayer, FlayBBCNews)
    True
    
    """
    root='http://news.bbc.co.uk'
    example='http://news.bbc.co.uk/1/hi/business/7751714.stm'
    body_test='Woolworths'
    copyright_test='MM'
    def __init__(self, stream):
        FlayBase.__init__(self, stream)
    def snip_body(self):
        """
        1. snip the td with class storybody
        2. remove all
                <!-- Inline Embbeded Media -->
                <!--  This is the embedded player component -->
                <div class="videoInStoryC">
                <!-- END of Inline Embedded Media -->
                
        3. remove all
                <!-- S IBOX -->
                <table cellspacing="0" align="right" width="231" border="0" cellpadding="0">
                <tr>
                        <td width="5"><img src="http://newsimg.bbc.co.uk/shared/img/o.gif" width="5" height="1" alt="" border="0" vspace="0" hspace="0"></td>
                        <td class="sibtbg">

                                    <div class="sih">
                                        WHAT IS ADMINISTRATION?
                                    </div>
                ...
                                <div class="miiib"><!-- S ILIN --><div class="arr"><a class="" href="/1/hi/business/7570795.stm">What administration means for you</a></div><!-- E ILIN --><!-- S ILIN --><div class="arr"><a class="" href="/1/hi/magazine/7642138.stm">Credit crisis glossary</a></div><!-- E ILIN --><!-- S ILIN --><div class="arr"><a class="" href="http://www.bbc.co.uk/blogs/thereporters/robertpeston/2008/11/weep_for_woolies.html">Read Robert Peston's blog</a></div><!-- E ILIN --></div>

                        </td>
                    </tr>
                </table>

                <!-- E IBOX -->
        4. remove all         
                <!-- S IANC -->
                <a name="back"></a>
                <!-- E IANC -->
        5. remove all 
                <!-- S IIMA -->
                <div>
                <img src="http://newsimg.bbc.co.uk/media/images/45243000/gif/_45243931_woolworths_gr466.gif" width="466" height="211" alt="Woolworths share price graphic" border="0" vspace="0" hspace="0">
                </div>
                <br clear="all" />
                <!-- E IIMA -->
        6. remove all 
            <!-- S ILIN --><div class="arrdo"><a class="bodl" href="#shares">
            See how Woolworths' shares plunged during the past year</a></div>
            <!-- E ILIN -->
        7. unwrap from the <td class="storybody">
        8. remove
            <div id="socialBookMarks" class="sharesb">
        
        
        finally         ''.join(soup.findAll(text=True))
        
        """
        cssClass='storybody'
        body = self.soup.find('', { "class" : cssClass })
        while self._extract_paired_comment(body, 'S IBOX', ' E IBOX '): pass
        while self._extract_paired_comment(body, 'S IANC', ' E IANC '): pass
        while self._extract_paired_comment(body, 'S IIMA', ' E IIMA '): pass
        while self._extract_paired_comment(body, 'S ILIN', ' E ILIN '): pass
        while self._extract_element_by_class(body, 'div', 'videoInStoryA'): pass
        while self._extract_element_by_class(body, 'div', 'videoInStoryB'): pass
        while self._extract_element_by_class(body, 'div', 'videoInStoryC'): pass
        while self._extract_element_by_class(body, 'div', 'videoInStoryD'): pass
        while self._extract_element_by_class(body, 'div', 'videoInStoryE'): pass
        while self._extract_element_by_class(body, 'div', 'mvtb'): pass
        while self._extract_element_by_id(body, 'socialBookMarks'): pass
        self._tidy_and_return_in_common_body_format(body)
    def snip_copyright(self):
        """
        <p id="blq-copyright">
        <img height="21" width="68" alt="BBC" src="/shared/img/v4/footer_blocks_grey.gif"/>
        © MMVIII
        </p>
        """
        # cblock = self.soup.find(id="blq-copyright")
        # cright = cblock.contents[1]
        # self._add(copyright=str(cright).strip())
        cright = ''.join(self.soup.find(id='blq-copyright').findAll(text=True))
        self._add(copyright=unicode(u'BBC'+ cright))
   

class FlayFTDotCom(FlayBase):
    """
    >>> from zope.interface.verify import verifyClass
    >>> from collective.feedfiller.interfaces import IPageFlayer
    >>> from collective.feedfiller.flay import FlayFTDotCom
    >>> verifyClass(IPageFlayer, FlayFTDotCom)
    True
    
    """
    
    root='http://www.ft.com ft.com ft.org traxfer.ft.com'
    example='http://www.ft.com/cms/s/0/a73d8696-bc58-11dd-9efc-0000779fd18c.html'
    body_test='moderate pace in November'
    author_test='Norma Cohen'
    copyright_test='The Financial Times'
    def __init__(self, stream):
        FlayBase.__init__(self, stream)
    def _register_login_credentials(self, link): 
        AddCookieProcessor(link, 'gjgjgjgj', 'legion')
    def snip_body(self):
        """snip the td with class storybody"""
        body = self.soup.find('div', { "class" : 'ft-story-body' })
        self._tidy_and_return_in_common_body_format(body)
    def snip_author(self):
        """snip the div with class ft-story-header. get the contents of the next
        p.
        ...
        <div class="ft-story-header">
        <h2>House price falls slow but swift recovery ruled out</h2>
        <p>By Norma Cohen </p>
        <p>Published: November 27 2008 08:18 | Last updated: November 27 2008 08:18</p>
        </div>
        """
        byline = self.soup.find('div', { "class" : 'ft-story-header' })
        author = byline.p.contents[0].split('By ')[1]
        self._add(author=unicode(author).strip())
    def snip_copyright(self):
        """
        <p class="copyright">
        <a href="http://www.ft.com/servicestools/help/copyright">Copyright</a>
        The Financial Times Limited 2008
        </p>
        XXX TEMPORARY VALUE BELOW - SITE IN FLUX 
        """
        self._add(copyright=u'The Financial Times Ltd')


class FlayNYTDotCom(FlayBase):
    """
    >>> from zope.interface.verify import verifyClass
    >>> from collective.feedfiller.interfaces import IPageFlayer
    >>> from collective.feedfiller.flay import FlayNYTDotCom
    >>> verifyClass(IPageFlayer, FlayNYTDotCom)
    True
    
    """
    root='http://www.nytimes.com/'
    example='http://www.nytimes.com/2008/11/28/business/worldbusiness/28tunnel.html'
    body_test='like living in a submarine'
    author_test='JULIA WERDIGIER'
    copyright_test='The New York Times'
    def __init__(self, stream):
        FlayBase.__init__(self, stream)
    def condition_url(self,url):
        entireflag='?pagewanted=all'
        if url.endswith(entireflag):
            return url
        return url+entireflag
    def _register_login_credentials(self, link): 
        AddCookieProcessor(link, 'russf@topia.com', 'go1lucky')
    def snip_body(self):
        """
        <div id="articleBody">
        
        remove
            <div id="portfolioInline" class="inlineLeft">
        remove
            <div class="nextArticleLink clearfix">
            <a onclick="s_code_linktrack('Article-MoreArticlesBottom');" href="http://www.nytimes.com/pages/business/index.html">More Articles in 
                                            Business &#x00bb;</a>
            <span>A version of this article appeared in print on November 28, 2008, on page B3 of the New York edition.</span>
            </div>
        """
        body = self.soup.find(id='articleBody')
        self._extract_element_by_class(body, 'div', 'inlineLeft')
        self._extract_element_by_class(body, 'div', 'nextArticleLink')
        self._tidy_and_return_in_common_body_format(body)
    def snip_author(self):
        """
        <nyt_byline type=" " version="1.0">
        <div class="byline">
        By
        <a title="More Articles by Julia Werdigier" href="http://topics.nytimes.com/top/reference/timestopics/people/w/julia_werdigier/index.html?inline=nyt-per">JULIA WERDIGIER</a>
        </div>
        </nyt_byline>
        """
        cssClass='byline'
        byline = self.soup.find('div', { "class" : cssClass })
        author = unicode(byline.a.contents[0])
        self._add(author=author.strip())
    def snip_copyright(self):
        """
        MESSY
        <nyt_footer>
        <nyt_copyright>
            <div id="footer">
                <div class="footerRow">
                    <a href="http://www.nytimes.com/">Home</a>
                    <ul>
                    <li>
                    <a href="http://www.nytimes.com/pages/world/index.html">World</a>
                    </li>
                   ...
                    </li>
                    </ul>
                </div>
                <a href="http://www.nytimes.com/ref/membercenter/help/copyright.html">Copyright 2008</a>
                <a href="http://www.nytco.com/">The New York Times Company</a>
                <ul>
                </ul>
            </div>
        </nyt_copyright>
        </nyt_footer>        """
        footer = self.soup.find(id='footer')
        footer.div.extract()
        c1=footer.a.contents[0]
        footer.a.extract()
        c2=footer.a.contents[0]
        copyright=' '.join((c1,c2,)).strip()
        self._add(copyright=copyright)

class FlayWolverhamptonEandStar(FlayBase):
    """
    Flay Wolverhampton express and Star
    >>> from zope.interface.verify import verifyClass
    >>> from collective.feedfiller.interfaces import IPageFlayer
    >>> from collective.feedfiller.flay import FlayWolverhamptonEandStar
    >>> verifyClass(IPageFlayer, FlayWolverhamptonEandStar)
    True
    
    """
    root='http://www.expressandstar.com/'
    example='http://www.expressandstar.com/2008/11/29/grandfather-tried-to-smother-wife/'
    body_test='Life without him has been traumatic for her.'
    author_test=''
    copyright_test=''
    def __init__(self, stream):
        FlayBase.__init__(self, stream)
    def snip_body(self):
        """
        <div class="entry-content">
        """
        body = self.soup.find('div', {'class':"entry-content"})
        self._tidy_and_return_in_common_body_format(body)
    def snip_copyright(self):
       """
        <div id="footer">
            <p>
                <span id="privacy">yadda
                </span> 
                <span id="copyright">
                 © 2008 -
                <a href="/"> The Express & Star Newspaper </a>
                , Wolverhampton, West Midlands, UK - all rights reserved
                </span>
            </p>
        </div>
       """
       copyright = ''.join(self.soup.find(id='copyright').findAll(text=True))
       self._add(copyright=copyright)
        
        
        
        
class FlayDefaultHTTP(FlayBase):
    """Matches all feeds and http pages"""
    root='http:// feed://'
    example='http://news.bbc.co.uk/1/hi/business/7751714.stm'
    body_test='Woolies will not be the last casualty'
    author_test=''
    copyright_test=''
    def __init__(self, stream):
        FlayBase.__init__(self, stream)
        if __name__ != '__main__':
            log.warning('Fall back to FlayDefaultHTTP for %s', stream)
    def snip_body(self):
        """
        """
        body = self.soup.find('body')
        body = self._common_extractions(body)
        self._tidy_and_return_in_common_body_format(body)

flayers = (
        FlayNYTDotCom,
        FlayWolverhamptonEandStar,
        FlayAlternet, 
        FlayBBCNews, 
        FlayFTDotCom,
        FlayDefaultHTTP,
        )
if __name__ == '__main__':
    
    logging.basicConfig()
    log = logging.getLogger('Feedfiller.Flay')
    log.setLevel(logging.INFO)
    log.debug('starting')
    
    for flayer in flayers:
        flayer.test()
    
"""
Coming soon...
feed://80211b.weblogger.com/xml/scriptingNews2.xml
feed://feeds.fool.com/usmf/foolwatch
feed://rss.businessweek.com/bw_rss/topstories
feed://rss.cnn.com/rss/edition.rss
feed://www.electronics.ca/presscenter/articlerss.php
feed://www.feedzilla.com/rss/business/business-africa-news
feed://www.feedzilla.com/rss/top-news/business
feed://www.feedzilla.com/rss/top-news/technology
feed://www.ibtimes.com/rss/feed/hightech.rss
feed://www.marketingweek.co.uk/include/qbe/rss_latest_news.xml
feed://www.renewableenergyworld.com/rss/renews.rss
http://extfeeds.worldbank.org/extfeedbuilder/feed/ECA_full_rss.xml
http://feeds.feedburner.com/time/business
http://feeds.marketwatch.com/marketwatch/topstories
http://feeds.washingtonpost.com/wp-dyn/rss/business/index_xml
http://newsrss.bbc.co.uk/rss/newsonline_uk_edition/world/europe/country_profiles/rss.xml
http://www.economist.com/rss/at_a_glance_rss.xml
http://www.guardian.co.uk/rssfeed/0,,24,00.xml
http://www.iht.com/atom/ap_business.xml
http://www.nytimes.com/services/xml/rss/userland/Business.xml
http://www.telegraph.co.uk/finance/rss
http://www.timesonline.co.uk/tol/feeds/rss/business.xml

russ's notes...
BBC links here sometimes...
http://www.bbc.co.uk/blogs/thereporters/robertpeston/
note the single page trick...
http://www.newscientist.com/article/mg20026841.900-whatever-happened-to-the-hydrogen-economy.html?full=true
http://www.newscientist.com/article/mg20026841.900-whatever-happened-to-the-hydrogen-economy.html

http://www.ft.com/rss/world/uk/economy
http://www.ft.com/rss/world/
http://www.ft.com/rss/companies/oil-gas
http://www.ft.com/rss/companies/aerospace-defence
http://www.ft.com/rss/companies/banks
http://www.ft.com/rss/companies/europe

http://newsrss.bbc.co.uk/rss/newsonline_uk_edition/world/rss.xml
http://newsrss.bbc.co.uk/rss/newsonline_uk_edition/business/rss.xml
http://newsrss.bbc.co.uk/rss/newsplayer_uk_edition/uk/rss.xml
http://newsrss.bbc.co.uk/rss/newsplayer_uk_edition/health/rss.xml

http://www.marketwatch.com/news/story/story.aspx?guid=%7BD91443E1%2D2A28%2D4032%2DBA89%2DFB49605AE8E1%7D&siteid=rss
"""    
