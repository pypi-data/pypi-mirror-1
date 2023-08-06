# -*- coding: utf-8 -*-
#
# File: base.py
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

from Products.Five import zcml
from Products.Five import fiveconfigure

from Testing import ZopeTestCase as ztc

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

@onsetup
def setup_contentmirror():
    """Set up the additional products
    """

    fiveconfigure.debug_mode = True
    import inquant.contentmirror.base
    zcml.load_config('configure.zcml', inquant.contentmirror.base)
    fiveconfigure.debug_mode = False

    ztc.installPackage('inquant.contentmirror.base')

setup_contentmirror()
ptc.setupPloneSite(products=['inquant.contentmirror.base'])


class CMTestCase(ptc.PloneTestCase):
    """Base class used for test cases
    """
    def create(self, context, what, name):
        context.invokeFactory(what, name, title=name)
        object = context.get(name)
        object.processForm()
        return object

class CMFunctionalTestCase(ptc.FunctionalTestCase):
    """Test case class used for functional (doc-)tests
    """

# vim: set ft=python ts=4 sw=4 expandtab :


