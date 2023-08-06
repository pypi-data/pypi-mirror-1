from setuptools import setup, find_packages
import os
from os.path import join

version = '1.2'

README = open(join('iw', 'thumbs', 'README.txt')).read()
README_PASTE = open(join('docs', 'README.txt')).read()
PASTE_CONF = open(join('docs', 'sample.ini')).readlines()
PASTE_CONF = ''.join(['  %s' % l for l in PASTE_CONF])
BLANK = '\n'*2

long_description= README + BLANK + README_PASTE + PASTE_CONF + BLANK

tests_require=['zope.testing', 'iw.email', 'zope.component']

setup(name='iw.thumbs',
      version=version,
      description="A wsgi middleware to generate and serve image thumbnails.",
      long_description=long_description,
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Development Status :: 5 - Production/Stable",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        ],
      keywords='wsgi imaging',
      author='Ingeniweb',
      author_email='support@ingeniweb.com',
      url='',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['iw'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Paste',
      ],
      tests_require=tests_require,
      extras_require=dict(test=tests_require),
      entry_points="""
      # -*- Entry points: -*-
      [paste.filter_app_factory]
      main = iw.thumbs.middleware:make_thumbs
      [paste.app_factory]
      main = iw.thumbs.application:make_thumbs_app
      """,
      )
