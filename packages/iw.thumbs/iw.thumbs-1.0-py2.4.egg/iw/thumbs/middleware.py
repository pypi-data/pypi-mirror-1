# -*- coding: utf-8 -*-
import os
import re
import sha
import stat
import shutil
from paste.fileapp import FileApp
from iw.thumbs.image import resize
from iw.thumbs.url import default_parser
from iw.thumbs.image import default_fetcher

NoDefault = object()

class Thumbs(object):

    def __init__(self, application,
                       url_parser=default_parser,
                       url_regexp=NoDefault,
                       image_fetcher=NoDefault,
                       image_dir=NoDefault,
                       cache_dir=NoDefault,
                       debug=False):
        self.application = application

        if callable(url_parser):
            self.url_parser = url_parser
        else:
            # TODO retrieve entry point
            raise NotImplementedError('url_parser must be callable')

        if isinstance(url_regexp, basestring):
            url_regexp = re.compile(url_regexp)
        self.url_regexp = url_regexp

        if image_dir is not NoDefault:
            self.image_fetcher = default_fetcher(image_dir)
        elif callable(image_fetcher):
            self.image_fetcher = image_fetcher
        else:
            # TODO retrieve entry point
            raise NotImplementedError('image_fetcher must be callable')

        if cache_dir is NoDefault:
            raise RuntimeError('No cache_dir provided')

        self.cache_dir = cache_dir
        if not os.path.isdir(cache_dir):
            os.makedirs(cache_dir)

        self.debug = debug

    def get_app(self, environ):
        path_info = environ['PATH_INFO'] # need to add QS

        if self.url_regexp is NoDefault:
            parsed = self.url_parser(path_info)
        else:
            parsed = self.url_parser(path_info, regexp=self.url_regexp)

        if parsed:
            path, size = parsed
            dummy, ext = os.path.splitext(path)

            # make sure we got an image
            if ext.lower() not in ('.png', '.jpg', '.jpeg', '.gif'):
                return self.application

            # generate cached filename
            filename = sha.new(path_info).hexdigest() + ext
            cached = os.path.join(self.cache_dir, filename)

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
                image_dir=NoDefault,
                cache_dir=NoDefault):
    return Thumbs(application, url_regexp=url_regexp,
                  image_dir=image_dir, cache_dir=cache_dir)

