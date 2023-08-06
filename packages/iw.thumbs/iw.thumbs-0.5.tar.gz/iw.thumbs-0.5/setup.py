from setuptools import setup, find_packages
import os
from os.path import join

version = '0.5'

long_description=open(join('iw', 'thumbs', 'README.txt')).read()

tests_require=['zope.testing', 'iw.email', 'zope.component']

setup(name='iw.thumbs',
      version=version,
      description="A wsgi middleware to generate and serve image thumbnails.",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
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
          # -*- Extra requirements: -*-
          'Paste',
      ],
      tests_require=tests_require,
      extras_require=dict(test=tests_require),
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
