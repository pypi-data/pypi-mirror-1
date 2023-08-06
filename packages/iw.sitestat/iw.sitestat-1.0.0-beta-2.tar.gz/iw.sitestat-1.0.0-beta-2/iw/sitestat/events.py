## -*- coding: utf-8 -*-
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

# $Id$
"""
Events handlers. See configure.zcml for bindings
"""
__author__  = 'Gilles Lenfant <gilles.lenfant@ingeniweb.com>'
__docformat__ = 'restructuredtext'

from zope.component import queryAdapter, getAdapter
from iw.sitestat.interfaces import IContentOptions, ISitestatConfigSchema
from iw.sitestat.utils import getSite
from iw.sitestat.browser.contentoptions import compileClickinPaths
from iw.sitestat.config import PRODUCTNAME

###
## We don't need to keep clickin paths/UIDs of deleted objects
###

def removeFromClickinsOnDelete(item, event):
    """Handles content removal if targetted by clickins"""

    qi = getSite().portal_quickinstaller
    if not qi.isProductInstalled(PRODUCTNAME):
        return

    options = queryAdapter(item, IContentOptions)
    if options is None:
        return
    if options.is_clickin_target:
        global_config = getAdapter(getSite(), ISitestatConfigSchema)
        clickin_uids = list(global_config.clickin_uids)
        clickin_uids.remove(item.UID())
        global_config.clickin_uids = clickin_uids
        compileClickinPaths()
    return

###
## Update clickin paths when a ckickin target is moved
###

def updateClickinsOnMove(item, event):
    """Handles moves of clickin targetted items"""

    qi = getSite().portal_quickinstaller
    if not qi.isProductInstalled(PRODUCTNAME):
        return

    options = queryAdapter(item, IContentOptions)
    if options is None:
        return
    if options.is_clickin_target:
        compileClickinPaths()
