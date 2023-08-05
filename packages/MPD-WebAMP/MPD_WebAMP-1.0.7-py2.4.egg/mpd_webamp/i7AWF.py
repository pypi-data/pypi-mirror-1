import urllib2, urllib
from gzip import GzipFile
from StringIO import StringIO
from xml.dom import minidom

class i7AWF:
    """
    Retreive album artwork from the iTunes Music Store
    Adapted from Jesper Noehr's Perl script @ printf.dk
    Clint Ecker <me@clintecker.com>
    Jesper Noehr <jesper@noehr.org>
    Version 0.1 - Licensed under the Creative Commons share-alike license.
    
    Usage:
    
    from i7AWF import i7AWF
    i = i7AWF()
    i.artist = "Gnarls Barkley"
    i.album = "St. Elsewhere"
    url = i.payload()
    
    """
    itunes7_useragent = "iTunes/7.0 (Macintosh; U; PPC Mac OS X 10.4.7)"
    itunes7_url = "http://ax.phobos.apple.com.edgesuite.net/WebObjects/MZSearch.woa/wa/coverArtMatch?an=%s&pn=%s"
    itunes_ns = "http://www.apple.com/itms/"
    itunes7_store = 143457
    
    def __init__(self):
        self.artist = None
        self.album = None
    
    def payload(self):
        if self.artist and self.album:
            ## Quote our inputs
            self.artist = urllib.quote(self.artist)
            self.album = urllib.quote(self.album)

            ## Set up HTTP request
            url = self.itunes7_url % (self.artist, self.album)
            headers = {
              "X-Apple-Tz" : "7200",
        	  "X-Apple-Store-Front" : self.itunes7_store,
        	  "Accept-Language" : "en-us, en;q=0.50",
#        	  "X-Apple-Validation" : self.compseed(url, self.itunes7_useragent ),
        	  "Accept-Encoding" : "gzip, x-aes-cbc",
        	  "Connection" : "close",
        	  "Host" : "ax.phobos.apple.com.edgesuite.net"
            }
            
            ## Build Opener with Request
            request = urllib2.Request(url, None, headers)  
            opener = urllib2.build_opener()
            
            ## Spoof UA
            opener.addheaders = [('User-agent', self.itunes7_useragent)]      
            
            ## Get compressed XML file
            compressed = StringIO()    
            fp = opener.open(request)
            r = fp.read()
            while r:
                compressed.write(r)
                r = fp.read()
            compressed.seek(0,0)
            gz = GzipFile(fileobj = compressed)
            s = ''
            r = gz.read()
            while r:
                s += r
                r = gz.read()
            # close our utility files
            compressed.close()
            gz.close()

            ## Parse XML file
            url_start = s.find("<key>cover-art-url</key><string>") + 32
            url_end = s.find("</string>", url_start) - 1
            if ((url_end - url_start) > 1):
                my_url = s[url_start:url_end]
            else:
                my_url = ""
            return my_url
