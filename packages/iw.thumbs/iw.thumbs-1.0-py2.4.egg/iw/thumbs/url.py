# -*- coding: utf-8 -*-
import re
import os

_default_parser = re.compile(
        '^/+thumbs/+(?P<width>[0-9]+)x(?P<height>[0-9]+)/{0,1}(?P<path>/.+)')

def default_parser(url, regexp=_default_parser):
    m = regexp.match(url)
    if m:
        w = m.group('width')
        h = m.group('height')
        path = m.group('path')
        path = path.replace('/', os.sep)
        return path, (int(w), int(h))
    return None

