import urllib,urllib2

params = urllib.urlencode(dict(username='gjgjgjgj', password='legion'))
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
urllib2.install_opener(opener)
flob = urllib2.urlopen('https://registration.ft.com/registration/barrier/login', params)
print flob.code, flob.info
for line in flob.readlines():
    print line
flob.close()
print '*'*80

flob = urllib2.urlopen('http://www.ft.com/cms/s/0/a963b316-bc5b-11dd-9efc-0000779fd18c.html')
print flob.code, flob.info
for line in flob.readlines():
    print line
flob.close()
print '*'*80

flob = urllib2.urlopen('http://www.ft.com/cms/s/0/89e4a4d4-bcb3-11dd-af5a-0000779fd18c.html')
print flob.code, flob.info
for line in flob.readlines():
    print line
flob.close()

