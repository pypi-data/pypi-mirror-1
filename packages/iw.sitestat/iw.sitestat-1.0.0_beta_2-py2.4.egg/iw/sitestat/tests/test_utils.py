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
Testing utilities
"""
__author__  = 'Gilles Lenfant <gilles.lenfant@ingeniweb.com>'
__docformat__ = 'restructuredtext'


from iw.sitestat.tests.base import sitestatTestCase
from iw.sitestat import utils

class UtilsTestCase(sitestatTestCase):
    """We test utilities"""

    def testGetSite(self):
        site = utils.getSite()
        self.failUnless(site.getPhysicalPath() == self.portal.getPhysicalPath())
        return

    def testValidateSitestatName(self):
        tests = [
            # (potential name, valid),
            ('xxx', True),
            ('xx-x', True),
            ('xx_xx', True),
            ('xx%yy', False),
            ('\xfexx', False),
            ('_xxx', False),
            ('xxx_', False),
            ('-xxx', False),
            ('xxx-', False)
            ]
        for label, valid in tests:
            self.failUnlessEqual(utils.validateSitestatName(label), valid)
        return

    def testSitestatifyTitle(self):
        tests = [
            ('Ascii', 'Ascii'),
            ('\xc3\xa7on', 'con'),
            ('the clone', 'the-clone'),
            ('x<>&=y', 'x----y')
            ]
        for original, expected in tests:
            got = utils.sitestatifyTitle(original, charset='utf-8')
            self.failUnlessEqual(got, expected)
        return

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(UtilsTestCase))
    return suite
