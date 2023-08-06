# -*- coding: utf-8 -*-

import cgi
import urllib
import urllib2
import urlparse

from zoembed.workarounds import *


class Request(object):
    
    def __init__(self, url, http_method=None, data=None):
        super(Request, self).__init__()
        
        self.url = url
        self.http_method = (http_method and http_method or
                            (data and 'POST' or 'GET'))
        self.data = data
        self.headers = {}
    
    @property
    def url(self):
        parsed_url = (self.scheme, self.netloc, self.path, self.parameters,
                      urllib.urlencode(self.query), self.fragment)
        return urlparse.urlunparse(parsed_url)
    
    @url.setter
    def url(self, url):
        parsed_url = urlparse.urlparse(url)
        self.scheme = parsed_url[0]
        self.netloc = parsed_url[1]
        self.path = parsed_url[2]
        self.parameters = parsed_url[3]
        
        self.query = cgi.parse_qs(parsed_url[4])
        for key in self.query.keys():
            self.query[key] = self.query[key][-1]
        
        self.fragment = parsed_url[5]
    
    def build_request(self):
        req = urllib2.Request(self.url)
        req.get_method = lambda: self.http_method
        req.data = self.data
        req.headers.update(self.headers)
        return req
    
    def open(self):
        return urllib2.urlopen(self.build_request())


TINYURL_OPENER = urllib2.OpenerDirector()

if not urllib2._opener:
    urllib2._opener = urllib2.build_opener()

for handler in urllib2._opener.handlers:
    if not isinstance(handler, urllib2.HTTPRedirectHandler):
        TINYURL_OPENER.add_handler(handler)