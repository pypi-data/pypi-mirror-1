# -*- coding: utf-8 -*-
import re
import os

DEFAULT_PARSER = '^/+thumbs/+(?P<width>[0-9]{2,3})x(?P<height>[0-9]{2,3})/{0,1}(?P<path>/.+)'

def default_parser(regexp=DEFAULT_PARSER, **kwargs):
    regexp = re.compile(regexp)
    def parser(url):
        m = regexp.match(url)
        if m:
            w = m.group('width')
            h = m.group('height')
            path = m.group('path')
            path = path.replace('/', os.sep)
            return path, (int(w), int(h))
        return None
    return parser, regexp

SIZE_PARSER = '^/+thumbs/(?P<size>%s)/{0,1}(?P<path>/.+)'

DEFAULT_SIZES = {
    'small':(50, 50),
    'thumb':(100, 100),
    'medium':(300, 300),
    'large':(500, 500),
    'xlarge':(800, 800),
    }

def size_parser(regexp=SIZE_PARSER, sizes=DEFAULT_SIZES, **kwargs):
    regexp = regexp % '|'.join(sizes.keys())
    regexp = re.compile(regexp)
    def parser(url):
        m = regexp.match(url)
        if m:
            size = m.group('size')
            w,h = sizes[size]
            path = m.group('path')
            path = path.replace('/', os.sep)
            return path, (w, h)
        return None
    return parser, regexp

