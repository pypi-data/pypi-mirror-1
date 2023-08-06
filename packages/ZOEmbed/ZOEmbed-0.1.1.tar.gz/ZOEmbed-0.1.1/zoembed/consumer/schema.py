# -*- coding: utf-8 -*-

from urlparse import urlparse
import re

from zoembed.consumer.exceptions import InvalidURLScheme


class URLScheme(object):
    
    def __init__(self, urlpattern):
        
        self.urlpattern = urlpattern
        scheme, domain, path, _, _, _ = urlparse(self.urlpattern)
        
        # Scheme stuff
        if scheme not in ['http', 'https']:
            raise InvalidURLScheme(urlpattern)
        self.scheme = scheme
        
        # Domain stuff
        domain_pattern = filter(None, domain.split('.'))
        if '*' in domain_pattern[-2:]:
            raise InvalidURLScheme(urlpattern)
        self.domain_pattern = domain_pattern
        
        # Path stuff
        self.path_pattern = filter(None, path.split('/'))
    
    def __repr__(self):
        return '<URLScheme(%r)>' % (self.urlpattern,)
    
    def match(self, url):
        scheme, domain, path, _, _, _ = urlparse(url)
        if scheme != self.scheme:
            return False
        domain_match = match_list(self.domain_pattern,
                                  filter(None, domain.split('.')))
        path_match = match_list(self.path_pattern,
                                filter(None, path.split('/')),
                                one_token_per_wildcard=True)
        return (domain_match and path_match)


def match_list(pattern, argument, one_token_per_wildcard=False):
    
    if one_token_per_wildcard:
        args = list(argument) + ([None] * (len(pattern) - len(argument)))
        for pat, arg in zip(pattern, args):
            if not match_token(arg, pat):
                return False
        return True
    
    i = j = 0
    while (i < len(argument)) and (j < len(pattern)):
        
        if match_token(argument[i], pattern[j]):
            i += 1
            j += 1
        
        elif pattern[j] == '*' and (j == (len(pattern) - 1)):
            return True
        
        elif pattern[j] == '*' and (j < (len(pattern) - 1)):
            if argument[i] == pattern[j + 1]:
                j += 1
            else:
                i += 1
        
        else:
            return False
    
    if i == len(argument) and j == len(pattern):
        return True
    
    return False


def match_token(argument, pattern):
    if argument is None:
        return False
    elif pattern == '*':
        return bool(argument)
    elif pattern.startswith('{') and pattern.endswith('}'):
        return bool(re.compile(pattern[1:-1]).match(argument))
    return argument == pattern