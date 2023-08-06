# -*- coding: utf-8 -*-
__docformat__ = 'restructuredtext'

import os
import shutil
import tempfile
import unittest

from zope.testing import doctest, renormalizing

optionflags = (doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE |
               doctest.REPORT_ONLY_FIRST_FAILURE)


dirname = os.path.dirname(os.path.abspath(__file__))
package_dir = os.path.split(dirname)[0]

def test_app(environ, start_response):
    return ['Hello']

def start_response(*args, **kwargs):
    pass

def setUp(test):

    test.globs['os'] = os
    test.globs['test_app'] = test_app
    test.globs['start_response'] = start_response
    test.globs['image_path'] = os.path.join(dirname, 'logo.png')
    test.globs['image_path'] = os.path.join(dirname, 'logo.png')
    test.globs['cache_dir'] = tempfile.mkdtemp('_cache', 'iw.thumbs_')
    test.globs['package_dir'] = package_dir

def tearDown(test):
    shutil.rmtree(test.globs['cache_dir'])

def test_suite():
    suite = unittest.TestSuite((
            doctest.DocFileSuite(
                '../README.txt',
                setUp=setUp,
                tearDown=tearDown,
                optionflags=optionflags,
                ),
            doctest.DocFileSuite(
                '../url.txt',
                setUp=setUp,
                tearDown=tearDown,
                optionflags=optionflags,
                ),
            ))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
