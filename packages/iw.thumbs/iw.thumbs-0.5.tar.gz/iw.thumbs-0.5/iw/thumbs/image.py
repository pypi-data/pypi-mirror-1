# -*- coding: utf-8 -*-
from cStringIO import StringIO
import PIL.Image

def resize(src, dst, size, mode='r'):
    """resize an image to size
    """
    image = PIL.Image.open(src, mode)
    image.thumbnail(size)
    image.save(dst)
    return dst

def default_fetcher(path):
    return path

