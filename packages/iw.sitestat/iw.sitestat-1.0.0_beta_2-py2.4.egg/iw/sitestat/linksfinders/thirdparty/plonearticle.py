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

# $Id: plonearticle.py 36 2008-09-07 09:08:55Z glenfant $
"""
Links finder for a PloneArticle content
"""

__author__  = 'Gilles Lenfant <gilles.lenfant@ingeniweb.com>'
__docformat__ = 'restructuredtext'

from zope.interface import implements
from zope.component import adapts
from OFS.Image import File as OFSFile

from iw.sitestat.interfaces import IFileLinksFinder
from iw.sitestat.config import PDF_MIMETYPES

from Products.PloneArticle.interfaces import IPloneArticle

class PloneArticleFileLinksFinder(object):
    implements(IFileLinksFinder)
    adapts(IPloneArticle)

    def __init__(self, context):
        self.context = context
        self.file_urls = []
        self.pdf_file_urls = []
        self._buildLinks()

    def fileURLs(self):
        return self.file_urls

    def pdfFileURLs(self):
        return self.pdf_file_urls

    def _buildLinks(self):
        filesfield = self.context.getField('files')
        proxies = filesfield.get(self.context)
        for proxy in proxies:
            url = proxy.absolute_url()
            ffield = proxy.getPrimaryField()
            # AT is sometimes ugly, we need to get the file content in memory
            # to get its MIME type :(
            accessor = ffield.getAccessor(proxy)
            data = accessor()
            content_type = data.getContentType()
            if content_type in PDF_MIMETYPES:
                self.pdf_file_urls.append(url)
            else:
                self.file_urls.append(url)
        return
