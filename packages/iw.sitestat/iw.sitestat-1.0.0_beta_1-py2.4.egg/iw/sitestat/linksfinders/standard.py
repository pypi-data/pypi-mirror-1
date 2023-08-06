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

# $Id: standard.py 36 2008-09-07 09:08:55Z glenfant $
"""
Link finders for various content types
"""
__author__  = 'Gilles Lenfant <gilles.lenfant@ingeniweb.com>'
__docformat__ = 'restructuredtext'

from zope.interface import implements
from zope.component import adapts
from iw.sitestat.interfaces import IFileLinksFinder
from iw.sitestat.config import PDF_MIMETYPES

###
## Custom AT based type with custom schema
###

from Products.Archetypes.interfaces import IBaseObject

class ATTypeLinksFinder(object):
    """Find links for most AT based types"""
    implements(IFileLinksFinder)
    adapts(IBaseObject)

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
        context = self.context
        base_url = context.absolute_url()
        file_fields = [f for f in context.Schema().fields() if f.type == 'file']
        for field in file_fields:
            if field.get_size(context) == 0:
                # Ignore empty ones
                continue
            url = base_url + '/at_download/' + field.getName()
            if field.getContentType(context) in PDF_MIMETYPES:
                self.pdf_files_urls.append(url)
            else:
                self.file_urls.append(url)
        return

###
## ATCT File type
###

from Products.ATContentTypes.interface.file import IATFile

class ATCTFileLinksFinder(object):
    """Find link in the File ATCT standard view"""

    implements(IFileLinksFinder)
    adapts(IATFile)

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
        context = self.context
        # AT File provides its file on its own URL
        url = context.absolute_url()
        field = context.Schema().getField('file')
        urls = [url, url + '/at_download/file']
        if field.getContentType(context) in PDF_MIMETYPES:
            self.pdf_files_urls = urls
        else:
            self.file_urls = urls
        return
