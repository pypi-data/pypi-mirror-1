import address
import urllib
import urllib2

class Location:
    """
    generic class for locations
    """

    def __init__(self, baseurl=""):
        self.baseurl = baseurl

    def url(self, query):
        return self.baseurl + self.process(query)

    def process(self, query):
        return query

    def test(self, query):
        return True


class URL(Location):
    """a straight URL"""

    def process(self, query):
        if '://' in query:
            return query
        return 'http://' + query

    def test(self, query):
        """try to open the url"""

        if ' ' in query or '\n' in query:
            return False

        try:
            site = urllib.urlopen(self.process(query))
        except IOError:
            return False
        return True

class GoogleMaps(Location):
    """try to google-maps the address"""

    def __init__(self):
        gmapsurl='http://maps.google.com/maps?f=q&hl=en&q='
        Location.__init__(self, gmapsurl)

    def process(self, query):
        theaddress = address.normalizeaddress(query)
        if not theaddress:
            return theaddress
        return urllib.quote_plus(theaddress)

    def test(self, query):
        return bool(self.process(query))

class Trac(Location):
    def __init__(self, baseurl):
        baseurl = baseurl.strip('/') + '/'
        Location.__init__(self, baseurl)

    def process(self, query):
        if query[0] == 'r':
            if query[1:].isdigit():
                return 'changeset/' + str(query[1:])
        if query[0] == '#':
            if query[1:].isdigit():
                return 'ticket/' + str(query[1:])

    def test(self, query):
        return bool(self.process(query))
        

class Wikipedia(Location):
    """try to open the query in wikipedia"""
    def __init__(self):        
        wikiurl = 'http://en.wikipedia.org/wiki/'
        Location.__init__(self, wikiurl)

    def process(self, query):
        return urllib.quote_plus('_'.join(query.split()))
        
    def test(self, query):
        'test to see if the article exists'

        # need a phony user agent so wikipedia won't know we're a bot
        headers = {}
        headers['User-Agent'] = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.0.4) Gecko/20060508 Firefox/1.5.0.4'

        request = urllib2.Request(self.url(query), None, headers)
        try:
            f = urllib2.urlopen(request).read()
        except urllib2.HTTPError, e:
            return False

        if 'Wikipedia does not have an article with this exact name' in f:
            return False
        return True

class Google(Location):
    def __init__(self):        
        googleurl = 'http://www.google.com/search?hl=en&q='
        Location.__init__(self, googleurl)
        
    def process(self, query):
        return urllib.quote_plus(query)
