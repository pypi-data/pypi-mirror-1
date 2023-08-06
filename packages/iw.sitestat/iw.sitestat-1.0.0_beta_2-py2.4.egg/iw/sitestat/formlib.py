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
Some formlib adds
"""
__author__  = 'Gilles Lenfant <gilles.lenfant@ingeniweb.com>'
__docformat__ = 'restructuredtext'

from zope.interface import implements
from zope.schema.interfaces import IURI, InvalidURI
from zope.schema import URI
from zope.app.form.browser import ASCIIWidget

###
## A field for an URL and its widget
## Binding is in configure.zcml
###

class IURLLine(IURI):
    pass

class URLLine(URI):
    implements(IURLLine)

    def _validate(self, value):
        if len(value) == 0:
            # Value is optional
            return
        super(URLLine, self)._validate(value)
        if not value.startswith('http'):
            raise InvalidURI(value)
        return

class URLWidget(ASCIIWidget):
    displayWidth = 80
