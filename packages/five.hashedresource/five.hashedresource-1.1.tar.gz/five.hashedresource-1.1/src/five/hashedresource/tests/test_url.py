##############################################################################
#
# Copyright (c) 2009 Zope Corporation and Contributors.
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
"""tests

$Id: test_url.py 102333 2009-07-27 11:11:25Z sweh $
"""
from five.hashedresource import testing
import os.path
import unittest
import zope.component
import zope.traversing.browser.interfaces


class HashingURLTest(testing.FunctionalTestCase):

    def test_directory_url_should_contain_hash(self):
        directory_url = str(zope.component.getMultiAdapter(
                (self.directory, self.request),
                zope.traversing.browser.interfaces.IAbsoluteURL))
        self.assertMatches(
            r'http://nohost/\+\+noop\+\+[^/]*/\+\+resource\+\+%s' %
            'myresource', directory_url)

    def test_file_url_should_contain_hash(self):
        file = self.app.aq_inner.restrictedTraverse('++resource++test.txt')
        file_url = str(zope.component.getMultiAdapter((file, self.request),
                zope.traversing.browser.interfaces.IAbsoluteURL))
        self.assertMatches(
            'http://nohost/\+\+noop\+\+[^/]*/\+\+resource\+\+test.txt',
            file_url)

    def test_different_files_hashes_should_differ(self):
        open(os.path.join(self.fixture, 'example.txt'), 'w').write('foo')
        file_ = self.app.aq_inner.restrictedTraverse('++resource++example.txt')
        file1_url = str(zope.component.getMultiAdapter((file_, self.request),
                zope.traversing.browser.interfaces.IAbsoluteURL))
        open(os.path.join(self.fixture, 'example.txt'), 'w').write('bar')
        file2_url = str(zope.component.getMultiAdapter((file_, self.request),
                zope.traversing.browser.interfaces.IAbsoluteURL))
        self.assertNotEqual(self._hash(file1_url), self._hash(file2_url))

    def test_directory_contents_changed_hash_should_change(self):
        before = str(zope.component.getMultiAdapter(
                (self.directory, self.request),
                zope.traversing.browser.interfaces.IAbsoluteURL))
        f = open(os.path.join(self.fixture, 'example.txt'), 'w')
        f.write('foo')
        f.close()
        after = str(zope.component.getMultiAdapter(
                (self.directory, self.request),
                zope.traversing.browser.interfaces.IAbsoluteURL))
        self.assertNotEqual(self._hash(before), self._hash(after))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(HashingURLTest))
    return suite
