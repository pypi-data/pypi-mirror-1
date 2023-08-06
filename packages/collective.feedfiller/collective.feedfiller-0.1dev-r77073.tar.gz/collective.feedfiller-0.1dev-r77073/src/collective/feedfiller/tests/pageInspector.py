import re
import urllib2, httplib
from BeautifulSoup import BeautifulSoup
from openanything import fetch

httplib.HTTPConnection.debuglevel = 1
link='http://news.bbc.co.uk/1/hi/business/7751714.stm'
link='http://news.google.co.uk/news/url?sa=T&ct=uk/9-0&fd=R&url=http://www.worcesternews.co.uk/news/3865376.Royal_Worcester___all_stock_must_go/&cid=0&ei=Zlc0Sd2pM6XEwAGX4ZmdDg&usg=AFQjCNGoJPPna5rShA9HErrM9RAUYbtnmg'
link=u'http://news.google.co.uk/news/url?sa=T&ct=uk/9-0&fd=R&url=http://www.worcesternews.co.uk/news/3865376.Royal_Worcester___all_stock_must_go/&cid=0&ei=Zlc0Sd2pM6XEwAGX4ZmdDg&usg=AFQjCNGoJPPna5rShA9HErrM9RAUYbtnmg'
userAgent = 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.5; en-US; rv:1.9.0.4) Gecko/2008102920 Firefox/3.0.4'

f=fetch(link, agent=userAgent )
#print f['url']
#print f['status']
soup = BeautifulSoup(f['data'])
print str(soup)