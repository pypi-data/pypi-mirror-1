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

# $Id: test_doctests.py 38 2008-09-07 09:56:32Z glenfant $
"""
Running doctests
"""
__author__  = 'Gilles Lenfant <gilles.lenfant@ingeniweb.com>'
__docformat__ = 'restructuredtext'

import os
import glob
import doctest
import unittest
from Testing.ZopeTestCase import FunctionalDocFileSuite as Suite
from iw.sitestat.tests.base import sitestatFunctionalTestCase
from iw.sitestat.config import PRODUCTNAME, HAVE_COLLAGE, HAVE_PLONEARTICLE, HAVE_SIMPLEALIAS

OPTIONFLAGS = (doctest.REPORT_ONLY_FIRST_FAILURE |
               doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)

def list_doctests():
    this_dir = os.path.dirname(os.path.abspath(__file__))
    filenames = [filename for filename in glob.glob(os.path.join(this_dir, 'test*.txt'))]
    for haveit, doctestfile in [
        (HAVE_COLLAGE, 'test_collage_linksfinder.txt'),
        (HAVE_PLONEARTICLE,'test_plonearticle_linksfinder.txt'),
        (HAVE_SIMPLEALIAS, 'test_simplealias_linksfinder.txt')]:
        if not haveit:
            filenames = [filename for filename in filenames
                         if not filename.endswith(doctestfile)]
    return filenames

def test_suite():
    return unittest.TestSuite(
        [Suite(os.path.basename(filename),
               optionflags=OPTIONFLAGS,
               package=PRODUCTNAME + '.tests',
               test_class=sitestatFunctionalTestCase)
         for filename in list_doctests()]
        )
