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

# $Id: __init__.py 36 2008-09-07 09:08:55Z glenfant $
"""
Acces to all links finders
"""
__author__  = 'Gilles Lenfant <gilles.lenfant@ingeniweb.com>'
__docformat__ = 'restructuredtext'

from iw.sitestat.config import HAVE_PLONEARTICLE, HAVE_COLLAGE, HAVE_SIMPLEALIAS
from iw.sitestat import LOG

from standard import ATTypeLinksFinder, ATCTFileLinksFinder

if HAVE_PLONEARTICLE:
    LOG("Activating support for PloneArticle")
    from thirdparty.plonearticle import PloneArticleFileLinksFinder

if HAVE_COLLAGE:
    LOG("Activating support for Collage")
    from thirdparty.collage import CollageFileLinksFinder

if HAVE_SIMPLEALIAS:
    LOG("Activating support for SimpleAlias")
    from thirdparty.simplealias import SimpleAliasFileLinksFinder


