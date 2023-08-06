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

# $Id: base.py 36 2008-09-07 09:08:55Z glenfant $
"""
Common testing resources
"""
__author__  = 'Gilles Lenfant <gilles.lenfant@ingeniweb.com>'
__docformat__ = 'restructuredtext'

from Testing import ZopeTestCase
from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase
from Products.PloneTestCase.layer import onsetup
import iw.sitestat.config
from iw.sitestat.config import (
    PRODUCTNAME, HAVE_COLLAGE, HAVE_PLONEARTICLE, HAVE_SIMPLEALIAS)
import iw.sitestat
if HAVE_COLLAGE:
    import Products.Collage
if HAVE_PLONEARTICLE:
    import Products.PloneArticle

iw.sitestat.config.ZOPETESTCASE = True

@onsetup
def setUpsitestat():
    fiveconfigure.debug_mode = True
    zcml.load_config('configure.zcml', iw.sitestat)
    fiveconfigure.debug_mode = False
    ZopeTestCase.installPackage(PRODUCTNAME)
    return

setUpsitestat()


def baseSetup(component, name):
    fiveconfigure.debug_mode = True
    zcml.load_config('configure.zcml', component)
    fiveconfigure.debug_mode = False
    ZopeTestCase.installProduct(name)
    return

if HAVE_COLLAGE:
    @onsetup
    def setUpCollage():
        baseSetup(Products.Collage, 'Collage')
        return

    setUpCollage()

if HAVE_PLONEARTICLE:
    @onsetup
    def setUpPloneArticle():
        baseSetup(Products.PloneArticle, 'PloneArticle')
        return

    setUpPloneArticle()

if HAVE_SIMPLEALIAS:
    @onsetup
    def setupSimpleAlias():
        baseSetup(Products.SimpleAlias, 'SimpleAlias')
        return

    setupSimpleAlias()

products = [PRODUCTNAME]
extension_profiles = ['%s:default' % PRODUCTNAME]

if HAVE_COLLAGE:
    products.append('Collage')
    extension_profiles.append('Products.Collage:default')

if HAVE_PLONEARTICLE:
    products.append('PloneArticle')
    extension_profiles.append('Products.PloneArticle:default')

if HAVE_SIMPLEALIAS:
    products.append('SimpleAlias')
    extension_profiles.append('Products.SimpleAlias:default')

PloneTestCase.setupPloneSite(
    products=products,
    extension_profiles=extension_profiles)

class sitestatTestCase(PloneTestCase.PloneTestCase):

    class Session(dict):
        def set(self, key, value):
            self[key] = value

    def _setup(self):
        PloneTestCase.PloneTestCase._setup(self)
        self.app.REQUEST['SESSION'] = self.Session()

class sitestatFunctionalTestCase(PloneTestCase.FunctionalTestCase):

    class Session(dict):
        def set(self, key, value):
            self[key] = value

    def _setup(self):
        PloneTestCase.FunctionalTestCase._setup(self)
        self.app.REQUEST['SESSION'] = self.Session()
