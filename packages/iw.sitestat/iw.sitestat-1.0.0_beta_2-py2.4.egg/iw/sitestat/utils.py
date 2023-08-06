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

# $Id: utils.py 45 2008-09-30 16:23:05Z glenfant $
"""
Misc utilities
"""
__author__  = 'Gilles Lenfant <gilles.lenfant@ingeniweb.com>'
__docformat__ = 'restructuredtext'

###
## Getting the Plone site
###

from zope.component import getUtility
from Products.CMFCore.interfaces import ISiteRoot

def getSite():
    return getUtility(ISiteRoot)

###
## Multi purpose validator
###

import string

def validateSitestatName(text):
    """A Sitestat name has only ASCII chars and may contain '-' and '_'"""
    valid_letters = string.ascii_lowercase + '-_'
    if text[0] not in string.ascii_lowercase:
        return False
    if text[-1] not in string.ascii_lowercase:
        return False
    for char in text[1:-1]:
        if char not in valid_letters:
            return False
    return True

###
## Makes a title Sitestat counter compatible
###

import unicodedata
from Products.CMFPlone.utils import getSiteEncoding
from iw.sitestat.config import BLACKLISTED_CHARS

_counterstrings_translator = string.maketrans(BLACKLISTED_CHARS, '-' * len(BLACKLISTED_CHARS))

def sitestatifyTitle(title, charset=None):
    if charset is None:
        charset = getSiteEncoding(getSite())
    utext = title.decode(charset, 'replace')
    ntext = unicodedata.normalize('NFKD', utext)
    atext = ntext.encode('ascii', 'ignore')
    atext = atext.translate(_counterstrings_translator)
    return atext

###
## Version of this egg
## (stolen from Products.CMFPlone.utils)
###

from iw.sitestat.config import PACKAGE_HOME
from Products.CMFPlone.utils import versionTupleFromString

def getFSVersionTuple():
    """Reads version.txt and returns version tuple"""
    vfile = "%s/version.txt" % PACKAGE_HOME
    v_str = open(vfile, 'r').read().lower().strip()
    return versionTupleFromString(v_str)

