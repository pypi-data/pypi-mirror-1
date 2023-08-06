# -*- coding: utf-8 -*-
from cStringIO import StringIO
import PIL.Image
import os

def resize(src, dst, size, mode='r'):
    """resize an image to size
    """
    image = PIL.Image.open(src, mode)
    image.thumbnail(size, PIL.Image.ANTIALIAS)
    image.save(dst)
    return dst

def default_fetcher(root):
    def fetcher(path):
        if path.startswith('/'):
            path = path[1:]
        path .replace('/', os.sep)
        return os.path.join(root, path)
    return fetcher

