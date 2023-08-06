# -*- coding: utf-8 -*-
#
# File: test_doctests.py
#
# Copyright (c) InQuant GmbH
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

__author__    = """Stefan Eletzhofer <stefan.eletzhofer@inquant.de>"""
__docformat__ = 'plaintext'
__revision__  = "$Revision: 57037 $"
__version__   = '$Revision: 57037 $'[11:-2]

import unittest
import doctest

from Testing import ZopeTestCase as ztc

from inquant.contentmirror.base.tests import base

doctests = "README.rst".split()

def test_suite():
    return unittest.TestSuite(

        [ ztc.ZopeDocFileSuite(
            dtfile, package='inquant.contentmirror.base',
            test_class=base.CMFunctionalTestCase,
            optionflags=(doctest.ELLIPSIS | 
                         doctest.NORMALIZE_WHITESPACE))

            for dtfile in doctests ]
        )

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

# vim: set ft=python ts=4 sw=4 expandtab :
