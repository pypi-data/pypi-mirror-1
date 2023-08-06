#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup


setup(
    name='ZOEmbed',
    version='0.1.1',
    description="Zack's OEmbed client library.",
    author='Zachary Voase',
    author_email='disturbyte@gmail.com',
    url='http://github.com/disturbyte/zoembed',
    packages=['zoembed', 'zoembed.consumer'],
    package_data={'zoembed': ['providers.yaml']},
)
