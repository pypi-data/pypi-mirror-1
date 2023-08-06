# -*- coding: utf-8 -*-

import pkg_resources

from zoembed import consumer
from zoembed import formatter


global RESOLVER
RESOLVER = consumer.resolvers.Resolver.parse(
    pkg_resources.resource_string('zoembed', 'providers.yaml'))


def get_response(url):
    return RESOLVER.get_response(url)

def resolve(url):
    return RESOLVER.resolve(url)

def format_html(original_url, response):
    formatter_cls = getattr(formatter, response.type.title() + 'Formatter')
    formatter_instance = formatter_cls(original_url, response)
    return formatter_instance.html()

def format(url):
    return format_html(url, get_response(url))