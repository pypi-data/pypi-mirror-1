# -*- coding: utf-8 -*-

import re

from zoembed.consumer.exceptions import InvalidResponse
from zoembed.workarounds import *


class Response(object):
    def __init__(self, url, status, headers, raw_data):
        self.url = url
        self.status = status
        self.headers = headers
        self.raw_data = raw_data
        self._process()
    
    def __repr__(self):
        return '<Response(%r) at %s>' % (self.url, hex(id(self)),)
    
    def __getattribute__(self, attribute):
        try:
            return object.__getattribute__(self, attribute)
        except AttributeError:
            if attribute in self.data:
                return self.data[attribute]
            raise
    
    def _process(self):
        if 'json' in self.headers['Content-Type']:
            self.format = 'json'
            self.data = json.loads(self.raw_data)
        elif 'xml' in self.headers['Content-Type']:
            self.format = 'xml'
            self.data = {}
            elem = etree.fromstring(self.raw_data)
            if elem.tag != 'oembed':
                raise InvalidResponse('Illegal element tag')
            for child in elem:
                if child.tag == 'html':
                    self.data[child.tag] = get_inner_html(child)
                else:
                    self.data[child.tag] = child.text
        try:
            self._validate()
        except AssertionError, exc:
            raise InvalidResponse(*exc.args)
    
    def _assert_has(self, key):
        assert key in self.data, 'Response missing attribute %r' % (key,)
    
    def _assert_match(self, key, pattern):
        self._assert_has(key)
        assert re.match(pattern, str(self.data[key])), (
            'Response attribute %r does not match regex %r.' % (key, pattern))
        
    def _make_wrappers(self, *keys):
        for key in keys:
            setattr(self, key, self.data[key])
    
    def _wrap_width_and_height(self):
        self._assert_match('width', r'^[\d]+$')
        self._assert_match('height', r'^[\d]+$')
        self.width = int(self.data['width'])
        self.height = int(self.data['height'])
        
    def _validate(self):
        self._assert_has('type')
        self._make_wrappers('type')
        self._assert_match('version', r'^1\.0$')
        # Check for additional validation.
        if hasattr(self, '_validate_' + self.type):
            getattr(self, '_validate_' + self.type)()
    
    def _validate_photo(self):
        self._assert_has('url')
        self._make_wrappers('url')
        self._wrap_width_and_height()
    
    def _validate_video(self):
        self._assert_has('html')
        self._make_wrappers('html')
        self._wrap_width_and_height()
    
    def _validate_rich(self):
        self._assert_has('html')
        self._make_wrappers('html')
        self._wrap_width_and_height()
    
    def _validate_tinyurl(self):
        self._assert_has('location')
        self._make_wrappers('location')
    
    def __getitem__(self, key):
        return self.data[key]


def get_inner_html(tree):
    html_out = tree.text or u''
    for child in tree:
        html_out += etree.tostring(child)
    return html_out