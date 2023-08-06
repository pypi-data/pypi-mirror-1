# -*- coding: utf-8 -*-

from collections import deque
from cStringIO import StringIO

import yaml

from zoembed.consumer.exceptions import EndpointNotFound
from zoembed.consumer.providers import Provider


class Resolver(object):
    
    def __init__(self, initial=[]):
        self.providers = deque(initial[:])
    
    def __repr__(self):
        return '<Resolver() at %s>' % (hex(id(self)),)
    
    def add_provider(self, provider):
        provider.resolver = self
        self.providers.appendleft(provider)
    
    def resolve(self, url):
        for provider in self.providers:
            if provider.match(url):
                return provider
        raise EndpointNotFound(url)
    
    def get_response(self, url):
        return self.resolve(url).get_response(url)
    
    @property
    def Provider(self):
        name = 'Provider'
        attrs = {'__module__': self.__class__.__module__, 'resolver': self}
        return type(name, (Provider,), attrs)
    
    @classmethod
    def parse(cls, stream):
        resolver = cls()
        stream = isinstance(stream, basestring) and StringIO(stream) or stream
        
        # Load the definitions.
        try:
            rules = yaml.load(stream)
        finally:
            stream.close()
        
        for ruleset in rules:
            enabled = ruleset.pop('enabled', not ruleset.pop('disabled', False))
            if not enabled:
                continue            
            resolver.add_provider(resolver.Provider.from_yaml(ruleset))
        
        return resolver
