# -*- coding: utf-8 -*-

import urllib2

from zoembed.consumer.schema import URLScheme
from zoembed.consumer.response import Response
from zoembed.consumer.request import Request, TINYURL_OPENER
from zoembed.workarounds import *


class Provider(object):
    
    def match(self, url):
        return any(scheme.match(url) for scheme in self.schema)
    
    def __repr__(self):
        return '<%s(%s)>' % (self.__class__.__name__, self.name)
    
    def get_params(self, format='json', width=None, height=None):
        params = {}
        if width:
            params['maxwidth'] = width
        if height:
            params['maxheight'] = height
        params['format'] = getattr(self, 'format', format) or format
        return params
    
    @property
    def Request(self):
        name = self.name + 'Request'
        attrs = {'__module__': type(self).__module__, 'provider': self}
        return type(name, (Request,), attrs)
    
    @property
    def Response(self):
        name = self.name + 'Response'
        attrs = {'__module__': type(self).__module__, 'provider': self}
        return type(name, (Response,), attrs)
    
    @classmethod
    def from_yaml(cls, yaml_obj):
        name = yaml_obj.pop('type').title() + 'Provider'
        subcls = globals()[name]
        
        new_cls = type(name, (subcls, cls), {})
        return new_cls(**yaml_obj)


class RemoteProvider(Provider):
    
    def __init__(self, name='', scheme='', schema='', endpoint='', format=None):
        self.name = name
        self.schema = []
        if schema:
            self.schema = map(URLScheme, schema)
        if scheme:
            self.schema.append(URLScheme(scheme))
        self.endpoint = endpoint
        self.format = format
    
    def get_response(self, url, retry_on_not_impl=True, **params):
        req = self.Request(self.endpoint)
        req.query.update(params)
        req.query['url'] = url
        
        try:
            conn = req.open()
            status = conn.code
            headers = conn.headers
            data = conn.read()
        except urllib2.HTTPError, exc:
            if exc.code == 404: # Not Found
                return None
            
            elif exc.code == 501: # Not Implemented
                if not retry_on_impl:
                    raise
                
                this_format = params.get('format', 'json')
                if this_format == 'json':
                    params['format'] = 'xml'
                else:
                    params['format'] = 'json'
                
                return self.get_response(url, retry_on_not_impl=False, **params)
            
            elif exc.code == 401: # Unauthorized
                status = 501
                headers = exc.headers
                headers['content-type'] = 'application/json'
                data = json.dumps({'type': 'link', 'version': '1.0'})
        return self.Response(url, status, headers, data)


class TinyurlProvider(Provider):
    
    def __init__(self, name='', root_url='', root_urls=''):
        self.name = name
        self.schema = []
        if root_urls:
            self.schema = [URLScheme(url.rstrip('/') + '/{([\w]+)}')
                           for url in root_urls]
        if root_url:
            self.schema.append(URLScheme(root_url.rstrip('/') + '/{([\w]+)}'))
    
    def get_response(self, url, **params):
        req = self.Request(url, http_method='HEAD')
        try:
            conn = TINYURL_OPENER.open(url)
        except urllib2.HTTPError, exc:
            if exc.code not in [301, 302]:
                raise
            headers = exc.headers
            headers['content-type'] = 'application/json'
            data = json.dumps({'type': 'tinyurl', 'version': '1.0',
                               'location': headers['location']})
            return self.Response(url, 200, headers, data)
