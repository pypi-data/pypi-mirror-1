# -*- coding: utf-8 -*-

from markdown import etree

import zoembed


class Element(object):
        
    def __init__(self, tag_name, attributes=None, contents=None,
                 *args, **kwargs):
        self.tag_name = tag_name
        self.attributes = attributes or {}
        self.contents = contents or []
        if kwargs:
            if 'class_' in kwargs:
                self.attributes['class'] = kwargs.pop('class_')
            elif 'klass' in kwargs:
                self.attributes['class'] = kwargs.pop('klass')
            self.attributes.update(kwargs)
        if args:
            self.contents.extend(args)
    
    def __repr__(self):
        return '<Element(%r) at %s>' % (self.tag_name, hex(id(self)),)
    
    def __getattribute__(self, attribute):
        if attribute not in ['tag_name', 'attributes', 'contents']:
            if attribute in self.attributes:
                return self.attributes[attribute]
            return object.__getattribute__(self, attribute)
        return object.__getattribute__(self, attribute)
    
    def __setattr__(self, attribute, value):
        if attribute not in ['tag_name', 'attributes', 'contents']:
            self.attributes[attribute] = value
        object.__setattr__(self, attribute, value)
    
    def __delattr__(self, attribute):
        if attribute not in ['tag_name', 'attributes', 'contents']:
            if attribute in self.attributes:
                del self.attributes[attribute]
            object.__delattr__(self, attribute)
        object.__delattr__(self, attribute)
    
    def to_etree(self):
        tree = etree.Element(self.tag_name, self.attributes)
        for i, element in enumerate(self.contents):
            if i == 0 and isinstance(element, basestring):
                tree.text = element
            elif isinstance(element, Element):
                tree.append(element.to_etree())
            elif isinstance(element, basestring):
                if not tree:
                    tree.text += element
                else:
                    tree[-1].tail = tree[-1].tail or ''
                    tree[-1].tail += element
        return tree
    
    def __unicode__(self):
        return etree.tostring(self.to_etree())
    
    def __str__(self):
        return unicode(self).encode('utf-8')


class Formatter(object):
    
    def __init__(self, original_url, response):
        self.original_url = original_url
        self.response = response
    
    def html(self):
        return self.response.html


class LinkFormatter(Formatter):
    
    def html(self):
        if getattr(self.response, 'html', '').strip():
            return self.response.html
                
        link = Element('a', href=self.response.url, rel=u'nofollow')
        link.contents = [self.response.url]
        if hasattr(self.response, 'title'):
            link.title = self.response.title
            link.contents = [self.response.title]
        return unicode(link)


class PhotoFormatter(Formatter):
    
    def html(self):
        if getattr(self.response, 'html', '').strip():
            return self.response.html
        
        link = Element('a', href=self.original_url)
        image = Element('img', src=self.response.url,
                        height=str(self.response.height),
                        width=str(self.response.width))
        if hasattr(self.response, 'title'):
            link.title = self.response.title
            image.title = self.response.title
        if hasattr(self.response, 'alt'):
            image.alt = self.response.alt
        elif hasattr(self.response, 'title'):
            if hasattr(self.response, 'author_name'):
                image.alt = u'%s, by %s' % (self.response.title,
                                            self.response.author_name)
            else:
                image.alt = self.response.title
        else:
            if hasattr(self.response, 'author_name'):
                image.alt = u'Untitled image, by %s' % (
                    self.response.author_name,)
            else:
                image.alt = u'Untitled image'
        link.contents = [image]
        return unicode(link)


class TinyurlFormatter(Formatter):
    
    def html(self):
        try:
            provider = self.response.provider.resolver.resolve(
                self.response.location)
            provider = zoembed.resolve(self.response.location)
            if isinstance(provider, zoembed.consumer.providers.TinyurlProvider):
                raise zoembed.consumer.exceptions.OEmbedError()
            new_response = provider.get_response(self.response.location)
        except zoembed.consumer.exceptions.OEmbedError:
            pass
        else:
            return zoembed.format_html(self.response.location, new_response)
        
        self.response.url = self.response.location
        return LinkFormatter(self.response.location, self.response).html()


class VideoFormatter(Formatter):
    pass


class RichFormatter(Formatter):
    pass