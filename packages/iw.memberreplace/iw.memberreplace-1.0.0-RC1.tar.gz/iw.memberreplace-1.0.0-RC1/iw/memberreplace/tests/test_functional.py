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

# $Id: test_functional.py 81892 2009-03-07 23:35:10Z glenfant $

__author__  = 'Gilles Lenfant <gilles.lenfant@ingeniweb.com>'
__docformat__ = 'restructuredtext'

import os
import glob
from unittest import TestSuite
from zope.testing import doctest
from Testing.ZopeTestCase import FunctionalDocFileSuite
from iw.memberreplace.tests.base import memberreplaceFunctionalTestCase

OPTIONFLAGS = (doctest.REPORT_ONLY_FIRST_FAILURE |
               doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)

def tests_list():
    this_dir = os.path.dirname(os.path.abspath(__file__))
    return glob.glob1(this_dir, 'test*.txt')

def test_suite():
    suite = TestSuite()
    for test in tests_list():
        suite.addTest(FunctionalDocFileSuite(test,
            optionflags=OPTIONFLAGS,
            package="iw.memberreplace.tests",
            test_class=memberreplaceFunctionalTestCase))
    return suite
