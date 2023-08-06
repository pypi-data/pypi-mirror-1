.. contents::

Description
-----------

ìw.thumbs` is used to serve image thumbnail. The thumbnail is cached in a
directory and served with `paste.fileapp` so correct headers (ETag,
If-Modified, etc.) are returned.

`iw.thumbs` is highly configurable but if you use `Paste` to serve your
application you probably only need to read the last part of this documentation.

Usage
-----

The `Thumb` middleware take four arguments:

- application: the wsgi application to wrap.

- url_parser: a callable to retrieve the size of the thumbnail and the
  attending size as a tuple (width, height)
  Default: `iw.thumbs.url.url_parser`
  The default value match urls like `/thumbs/100x100/path/to/image.png` and
  return ('/path/to/image.png', (100, 100))

- url_regexp: a regexp passed as argument to the default url_parser. The regexp
  must have groups named path, width and height.
  Default: '^/+thumbs/+(?P<width>[0-9]{2,3})x(?P<height>[0-9]{2,3})/{0,1}(?P<path>/.+)'

- image_fetcher: a callable to retrieve the real image path
  Default: `iw.thumbs.image_fetcher`
  The default value return the `PATH_INFO` so you may override it. This callable
  is used to retrieve image from file system but you can also use it to retrieve
  image from other location like proxy, ftp, etc.

- image_dir: a directory where images are stored. Used by `image_fetcher` if
  the default one is used.

- cache_dir: a path to the directory used to cache thumbnails (required)

- debug: debug mode. Default: False  

Example
-------

Write a method to retrieve your image path from the `PATH_INFO`::

  >>> def image_fetcher(path_info):
  ...     return os.path.join(package_dir, *path_info.split('/')[1:])

Wrap your application with the middleware::

  >>> from iw.thumbs.middleware import Thumbs
  >>> app = Thumbs(test_app, image_fetcher=image_fetcher, cache_dir=cache_dir)

Then ask for an image::

  >>> environ = {'REQUEST_METHOD':'GET',
  ...            'PATH_INFO':'/thumbs/50x50/tests/logo.png'}
  >>> print app.get_app(environ)
  <paste.fileapp.FileApp object at ...>

Override the default url regexp::

  >>> regexp = '^/my_thumbs/(?P<width>[0-9]+)x(?P<height>[0-9]+)(?P<path>/.+)'
  >>> app = Thumbs(test_app, image_fetcher=image_fetcher, cache_dir=cache_dir,
  ...              url_regexp=regexp)

  >>> environ = {'REQUEST_METHOD':'GET', 'PATH_INFO':'/my_thumbs/50x50/tests/logo.png'}
  >>> print app.get_app(environ)
  <paste.fileapp.FileApp object at ...>

If the path does not match an image, the `test_app` is served::  

  >>> environ = {'REQUEST_METHOD':'GET', 'PATH_INFO':'/index.html'}
  >>> print app.get_app(environ)
  <function test_app at ...>

Using sizes names
-----------------

You can use size names::

  >>> app = Thumbs(test_app, image_fetcher=image_fetcher, cache_dir=cache_dir,
  ...              url_regexp='/thumbs/(?P<size>%s)(?P<path>/.*)',
  ...              url_parser='iw.thumbs.url:size_parser',
  ...              sizes={'thumb': (100,100), 'large': (600,600)})

  >>> environ = {'REQUEST_METHOD':'GET', 'PATH_INFO':'/thumbs/large/tests/logo.png'}
  >>> print app.get_app(environ)
  <paste.fileapp.FileApp object at ...>

Implementing your own parser
----------------------------

You need a callable who return a callable and the compiled regexp.

Let's define our strategy with a regexp::

  >>> re_thumb = '^/thumbs(?P<path>/.*)'

Then implement it with a parser::

  >>> import re
  >>> def custom_parser(regexp, **kwargs):
  ...     regexp = re.compile(regexp)
  ...     def parser(url):
  ...         m = regexp.match(url)
  ...         if m:
  ...             path = m.group('path')
  ...             return path, (100, 100)
  ...     return parser, regexp

Check this work::

  >>> app = Thumbs(test_app, image_fetcher=image_fetcher, cache_dir=cache_dir,
  ...              url_regexp=re_thumb, url_parser=custom_parser)

  >>> environ = {'REQUEST_METHOD':'GET', 'PATH_INFO':'/thumbs/tests/logo.png'}
  >>> print app.get_app(environ)
  <paste.fileapp.FileApp object at ...>

Utils
-----

Resize an image file to the specified destination at `size`::

  >>> from iw.thumbs.image import resize
  >>> thumbnail = os.path.join(cache_dir, 'thumb.png')
  >>> print resize(image_path, thumbnail, size=(50, 50))
  /..._cache/thumb.png
  >>> os.path.isfile(thumbnail)
  True

