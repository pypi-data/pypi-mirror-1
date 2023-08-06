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

# $Id: linksfinder.py 36 2008-09-07 09:08:55Z glenfant $
"""
Interfaces for finding file links on content objects.
"""
__author__  = 'Gilles Lenfant <gilles.lenfant@ingeniweb.com>'
__docformat__ = 'restructuredtext'

from zope.interface import Interface

class IFileLinksFinder(Interface):
    """Interface for adapters that find URLs for files in the context
    view. Developers that implement me should not worry too much
    providing too many URLs: The ones that don't show in the page are
    ignored."""

    def fileURLs():
        """Sequence of URLs to files (PDF excluded) published by the
        context object in its view"""

    def pdfFileURLs():
        """Sequence of URLs to PDF files published by the context
        object in its view"""
