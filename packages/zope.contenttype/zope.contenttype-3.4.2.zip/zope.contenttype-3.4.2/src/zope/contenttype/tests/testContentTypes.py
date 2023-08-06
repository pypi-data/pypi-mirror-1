##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Tests of the contenttypes extension mechanism.

$Id: testContentTypes.py 100501 2009-05-28 10:29:48Z rogerineichen $
"""

import mimetypes
import os.path
import sys
import unittest

from zope import contenttype

try:
    __file__
except NameError:
    __file__ = os.path.realpath(sys.argv[0])

here = os.path.dirname(os.path.abspath(__file__))
MIME_TYPES_1 = os.path.join(here, "mime.types-1")
MIME_TYPES_2 = os.path.join(here, "mime.types-2")

class ContentTypesTestCase(unittest.TestCase):

    def setUp(self):
        mimetypes.init()
        self._old_state = mimetypes.__dict__.copy()

    def tearDown(self):
        mimetypes.__dict__.update(self._old_state)

    def check_types_count(self, delta):
        self.assertEqual(len(mimetypes.types_map),
                         len(self._old_state["types_map"]) + delta)

    def test_add_one_file(self):
        ntypes = len(mimetypes.types_map)
        contenttype.add_files([MIME_TYPES_1])
        ctype, encoding = contenttype.guess_content_type("foo.ztmt-1")
        self.assert_(encoding is None)
        self.assertEqual(ctype, "text/x-vnd.zope.test-mime-type-1")
        ctype, encoding = contenttype.guess_content_type("foo.ztmt-1.gz")
        self.assertEqual(encoding, "gzip")
        self.assertEqual(ctype, "text/x-vnd.zope.test-mime-type-1")
        self.check_types_count(1)

    def test_add_two_files(self):
        ntypes = len(mimetypes.types_map)
        contenttype.add_files([MIME_TYPES_1, MIME_TYPES_2])
        ctype, encoding = contenttype.guess_content_type("foo.ztmt-1")
        self.assert_(encoding is None)
        self.assertEqual(ctype, "text/x-vnd.zope.test-mime-type-1")
        ctype, encoding = contenttype.guess_content_type("foo.ztmt-2")
        self.assert_(encoding is None)
        self.assertEqual(ctype, "text/x-vnd.zope.test-mime-type-2")
        self.check_types_count(2)

    def test_text_type(self):
        t = contenttype.text_type
        self.assertEqual(t('<HtmL><body>hello world</body></html>'), 
                         'text/html')
        self.assertEqual(t('<?xml version="1.0"><foo/>'), 'text/xml')
        self.assertEqual(t('<?XML version="1.0"><foo/>'), 'text/plain')
        self.assertEqual(t('foo bar'), 'text/plain')
        self.assertEqual(t('<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"' +
                           ' "http://www.w3.org/TR/html4/loose.dtd">'),
                           'text/html')


def test_suite():
    return unittest.makeSuite(ContentTypesTestCase)

if __name__ == '__main__':
    unittest.main()
