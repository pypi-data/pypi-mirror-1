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

# $Id: simplealias.py 36 2008-09-07 09:08:55Z glenfant $
"""
Links finder for a SimpleAlias content
"""

__author__  = 'Gilles Lenfant <gilles.lenfant@ingeniweb.com>'
__docformat__ = 'restructuredtext'

from zope.interface import implements
from zope.component import adapts, queryAdapter
from iw.sitestat.interfaces import IFileLinksFinder
from Products.SimpleAlias.interfaces import IAlias

class SimpleAliasFileLinksFinder(object):
    implements(IFileLinksFinder)
    adapts(IAlias)

    def __init__(self, context):
        target = context.getAlias()
        if target:
            # We use the adapter for the alias target
            self.links_finder = queryAdapter(target, IFileLinksFinder)
        else:
            self.links_finder = None
        return

    def fileURLs(self):
        if self.links_finder:
            return self.links_finder.fileURLs()
        else:
            return []


    def pdfFileURLs(self):
        if self.links_finder:
            return self.links_finder.pdfFileURLs()
        else:
            return []
