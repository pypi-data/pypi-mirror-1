# -*- coding: utf-8 -*-
## Copyright (C) 2008 Ingeniweb

## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program; see the file LICENSE.txt. If not, write to the
## Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

# $Id: test_testutils.py 36 2008-09-07 09:08:55Z glenfant $
"""
Testing... the test framework
"""
__author__  = 'Gilles Lenfant <gilles.lenfant@ingeniweb.com>'
__docformat__ = 'restructuredtext'


from iw.sitestat.tests.base import sitestatTestCase
from iw.sitestat.tests import utils as in_utils
from iw.sitestat.config import HAVE_COLLAGE, HAVE_PLONEARTICLE, HAVE_SIMPLEALIAS

class UtilsTestCase(sitestatTestCase):
    """We test utilities for testcases"""

    def testTestRequest(self):
        request = in_utils.TestRequest()
        request.set('dummy', 'stuff')
        self.failUnlessEqual(request.get('dummy'), 'stuff')
        return

    def testAddFile(self):
        self.loginAsPortalOwner()
        foo_file = in_utils.addFile(self.portal, 'foo', 'Foo')
        self.failUnlessEqual(foo_file.title_or_id(), 'Foo')
        return

    def testAddCollage(self):
        if HAVE_COLLAGE:
            self.loginAsPortalOwner()
            foo_collage = in_utils.addCollage(self.portal, 'col', 'Collage')
            self.failUnlessEqual(foo_collage.title_or_id(), 'Collage')
        return

    def testAddPloneArticle(self):
        if HAVE_PLONEARTICLE:
            self.loginAsPortalOwner()
            foo_article = in_utils.addPloneArticle(self.portal, 'art', 'Article')
            self.failUnlessEqual(foo_article.title_or_id(), 'Article')
        return

    def testAddSimpleAlias(self):
        if HAVE_SIMPLEALIAS:
            self.loginAsPortalOwner()
            foo_alias = in_utils.addSimpleAlias(self.portal, 'alias', 'Alias')
            self.failUnlessEqual(foo_alias.title_or_id(), 'Alias not set')


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(UtilsTestCase))
    return suite
