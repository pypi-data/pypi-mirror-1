# -*- coding: utf-8 -*-
import os
import re
import sha
import stat
import shutil
from paste.fileapp import FileApp
from iw.thumbs.image import resize
from iw.thumbs.url import default_parser
from iw.thumbs.url import DEFAULT_PARSER
from iw.thumbs.image import default_fetcher

NoDefault = object()

def resolve_func(value):
    if callable(value):
        return value
    try:
        module, meth = value.split(':')
        module = __import__(module, globals(),locals(), True)
    except ImportError:
        raise ImportError("Can't resolve %s" % value)
    try:
        return getattr(module, meth)
    except AttributeError:
        raise AttributeError("Can't resolve %s" % value)

class Thumbs(object):

    def __init__(self, application,
                       url_parser=default_parser,
                       url_regexp=DEFAULT_PARSER,
                       image_fetcher=NoDefault,
                       image_dir=NoDefault,
                       cache_dir=NoDefault,
                       **kwargs):
        self.application = application

        self.debug = kwargs.pop('debug', False)

        if not isinstance(url_regexp, basestring):
            raise ValueError('url_regexp must be a string gat %r' % url_regexp)

        self.url_parser, self.url_regexp = resolve_func(url_parser)(url_regexp, **kwargs)

        if image_dir is not NoDefault:
            self.image_fetcher = default_fetcher(image_dir)
        else:
            self.image_fetcher = resolve_func(image_fetcher)

        if cache_dir is NoDefault:
            raise RuntimeError('No cache_dir provided')

        self.cache_dir = cache_dir
        if not os.path.isdir(cache_dir):
            os.makedirs(cache_dir)


    def get_app(self, environ):
        path_info = environ['PATH_INFO'] # need to add QS

        parsed = self.url_parser(path_info)

        if parsed:
            path, size = parsed
            dummy, ext = os.path.splitext(path)

            # make sure we got an image
            if ext.lower() not in ('.png', '.jpg', '.jpeg', '.gif'):
                return self.application

            # generate cached direname
            h = sha.new(path_info).hexdigest()
            d1, d2, d3 = h[0:3], h[3:6], h[:6]

            cached = os.path.join(self.cache_dir, d1, d2, d3)
            if not os.path.isdir(cached):
                os.makedirs(cached)

            filename = path_info.split('/')[-1]
            cached = os.path.join(cached, filename)

            image_path = self.image_fetcher(path)
            if os.path.isfile(cached):
                # remove cached file if the original has been modified
                qs = environ.get('QUERY_STRING', '').lower()
                if self.debug or 'purge' in qs:
                    os.remove(cached)
                else:
                    last_modified = os.stat(image_path)[stat.ST_MTIME]
                    last_cached = os.stat(cached)[stat.ST_MTIME]
                    if last_modified > last_cached:
                        os.remove(cached)

            # generate cached thumb if not yet done
            if not os.path.isfile(cached):
                resize(image_path, cached, size)

            # add cache header
            if self.debug:
                # add cache headers
                headers = None
            else:
                headers = None

            #return paste's FileApp
            return FileApp(cached, headers=headers)

        return self.application

    def __call__(self, environ, start_response):
        if environ['REQUEST_METHOD'] == 'GET':
            return self.get_app(environ)(environ, start_response)
        return self.application(environ, start_response)

def make_thumbs(application, global_config,
                url_regexp=NoDefault,
                url_parser=default_parser,
                image_dir=NoDefault,
                cache_dir=NoDefault, **kwargs):

    if 'sizes' in kwargs:
        sizes = [v.strip() for v in kwargs['sizes'].split('\n')]
        sizes = [v.split('=') for v in sizes if v]
        sizes = [(k.strip(), v.split('x')) for k, v in sizes]
        sizes = [(k, (int(v[0]), int(v[1]))) for k, v in sizes]
        kwargs['sizes'] = dict(sizes)

    return Thumbs(application,
                  url_regexp=url_regexp, url_parser=url_parser,
                  image_dir=image_dir, cache_dir=cache_dir, **kwargs)

