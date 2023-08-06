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

# $Id: collage.py 36 2008-09-07 09:08:55Z glenfant $
"""
Links finder for a Collage content
"""
__author__  = 'Gilles Lenfant <gilles.lenfant@ingeniweb.com>'
__docformat__ = 'restructuredtext'

from zope.interface import implements
from zope.component import adapts
from Products.CMFCore.permissions import View as ViewPermission
from Products.Collage.interfaces import ICollage
from Products.ATContentTypes.interface.file import IATFile

from iw.sitestat.interfaces import IFileLinksFinder
from iw.sitestat.linksfinders import ATTypeLinksFinder
from iw.sitestat.utils import getSite

# Note that, as this date, for types that provide file download
# within a Collage, only ATFile has dedicated views. All these
# views use the standard AT FileWidget to show the link to the
# file, that why we don't use the standard adapter lookup but
# we force the adapter that follows the FileWidget rules to build
# The URLs.
# Developers who write custome content views for Collage and
# content types that publish download links may override
# this adapter with a custom one.

class CollageFileLinksFinder(object):
    implements(IFileLinksFinder)
    adapts(ICollage)

    def __init__(self, context):
        self.context = context
        self.file_urls = []
        self.pdf_files_urls = []
        self._buildLinks()
        return

    def fileURLs(self):
        return self.file_urls

    def pdfFileURLs(self):
        return self.pdf_files_urls

    def _buildLinks(self):
        """We gather URLs from all relevant subcontents"""
        for content in self._findFiles():
            finder = ATTypeLinksFinder(content)
            self.file_urls.extend(finder.fileURLs())
            self.pdf_files_urls.extend(finder.pdfFileURLs())

    def _findFiles(self):
        """Generator over relevant subobjects"""
        atfiles = []
        mtool = getSite().portal_membership
        for row in self.context.objectValues(spec='CollageRow'):
            for column in row.objectValues(spec='CollageColumn'):
                for content in column.objectValues():
                    if not mtool.checkPermission(ViewPermission, content):
                        continue
                    if IATFile.providedBy(content):
                        atfiles.append(content)
        return atfiles

#        FIXME: we get the same objects through the catalog like below
#               but their absolute_url() whoes (its the path from the Zope root
#               and *not* an URL. A bug in xx.absolute_url()?

#        path = '/'.join(self.context.getPhysicalPath())
#        catalog = getSite().portal_catalog
#        brains = catalog.searchResults(path=path, object_provides=IATFile.__identifier__)
#        return [b.getObject() for b in brains]

