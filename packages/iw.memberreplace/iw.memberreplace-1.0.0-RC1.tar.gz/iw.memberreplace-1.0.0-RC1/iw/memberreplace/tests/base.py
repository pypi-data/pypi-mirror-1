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

# $Id: base.py 81892 2009-03-07 23:35:10Z glenfant $
"""
Common testing resources
"""
__author__  = 'Gilles Lenfant <gilles.lenfant@ingeniweb.com>'
__docformat__ = 'restructuredtext'

from Testing import ZopeTestCase
from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.Five.testbrowser import Browser
from Products.PloneTestCase import PloneTestCase
from Products.PloneTestCase.layer import onsetup
import iw.memberreplace
from iw.memberreplace.config import PRODUCTNAME


@onsetup
def setUpmemberreplace():
    fiveconfigure.debug_mode = True
    zcml.load_config('configure.zcml', iw.memberreplace)
    fiveconfigure.debug_mode = False
    ZopeTestCase.installPackage(PRODUCTNAME)
    return

setUpmemberreplace()

PloneTestCase.setupPloneSite(
    products=[PRODUCTNAME],
    extension_profiles=['%s:default' % PRODUCTNAME])

class memberreplaceTestCase(PloneTestCase.PloneTestCase):

    class Session(dict):
        def set(self, key, value):
            self[key] = value

    def _setup(self):
        PloneTestCase.PloneTestCase._setup(self)
        self.app.REQUEST['SESSION'] = self.Session()

class memberreplaceFunctionalTestCase(PloneTestCase.FunctionalTestCase):

    class Session(dict):
        def set(self, key, value):
            self[key] = value

    def _setup(self):
        PloneTestCase.FunctionalTestCase._setup(self)
        self.app.REQUEST['SESSION'] = self.Session()
        self.browser = Browser()
