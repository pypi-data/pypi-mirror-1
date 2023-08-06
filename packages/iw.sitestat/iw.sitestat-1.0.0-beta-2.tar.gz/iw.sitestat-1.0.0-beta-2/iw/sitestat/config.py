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

# $Id: config.py 45 2008-09-30 16:23:05Z glenfant $
"""
iw.sitestat globals
"""
__author__  = 'Gilles Lenfant <gilles.lenfant@ingeniweb.com>'
__docformat__ = 'restructuredtext'

PRODUCTNAME = 'iw.sitestat'
I18N_DOMAIN = 'iw.sitestat'
ANNOTATIONS_KEY = 'iw.sitestat'
PROPERTYSHEET = 'iwsitestat_properties'

PDF_MIMETYPES = ('application/pdf', 'application/x-pdf')

BLACKLISTED_LABELS = (
    'agent', 'availscreen', 'colordepth', 'cookie', 'corporate', 'day', 'full_loading_time',
    'html_loading_time', 'HttpReferer', 'innersize', 'ip', 'java', 'lang', 'mimetypes',
    'name', 'newcookie', 'NewCookie', 'offset', 'or', 'outersize', 'p', 'pie', 'plugins',
    'referrer', 'screen', 'site', '_t', 'time', 'type', 'url', 'ver')

BLACKLISTED_CHARS = ' &=<>'

import os
PACKAGE_HOME = os.path.dirname(os.path.abspath(__file__))
del os

# Do not change ZOPETESTCASE here (see tests/base.py)
ZOPETESTCASE = False

###
## Third party components support
###

try:
    import Products.PloneArticle
except ImportError, e:
    HAVE_PLONEARTICLE = False
else:
    HAVE_PLONEARTICLE =True

try:
    import Products.Collage
except ImportError, e:
    HAVE_COLLAGE = False
else:
    HAVE_COLLAGE = True

try:
    import Products.SimpleAlias
except ImportError, e:
    HAVE_SIMPLEALIAS = False
else:
    HAVE_SIMPLEALIAS = True
