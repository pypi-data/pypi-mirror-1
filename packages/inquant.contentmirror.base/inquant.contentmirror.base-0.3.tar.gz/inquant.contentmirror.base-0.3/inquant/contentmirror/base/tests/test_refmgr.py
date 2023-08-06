# -*- coding: utf-8 -*-
#
# File: test_refmgr.py
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
__revision__  = "$Revision: 62293 $"
__version__   = '$Revision: 62293 $'[11:-2]

import unittest

from zope import component
from zope import interface

from zope.app.testing import ztapi

from inquant.contentmirror.base.interfaces import IMirroredContentManager
from inquant.contentmirror.base.interfaces import IMirrorContentLocator
from inquant.contentmirror.base.interfaces import IMirrorReferenceManager
from inquant.contentmirror.base.manager import DefaultReferenceManager
from inquant.contentmirror.base.traverser import MirrorObjectTraverser
from inquant.contentmirror.base.tests import base

class TestRefmgr(base.CMTestCase):
    def afterSetUp(self):
        self.setRoles(('Manager',))
        self.folder.invokeFactory("Folder", "f1")
        self.folder.invokeFactory("Folder", "f2")
        self.f1 = self.folder.f1
        self.f2 = self.folder.f2
        self.f1.invokeFactory("Document", "doc", title="Muh")

        component.provideAdapter(MirrorObjectTraverser)
        component.provideAdapter(DefaultReferenceManager)

        # mirror "doc" which is originally in f1 only to f2 also
        manager = component.getUtility(IMirroredContentManager)
        manager.addMirror(self.f1.doc, self.f2)

        self.original = self.f1.doc
        self.mirror = IMirrorContentLocator(self.f2).locate("doc")

    def testRefMgrLookup(self):
        self.failUnless(IMirrorReferenceManager(self.original))
        self.failUnless(IMirrorReferenceManager(self.mirror))

    def testRefMgrKeys(self):
        rm = IMirrorReferenceManager(self.mirror)
        self.assertEqual(len(rm.storage.keys()), 1)
        self.assertEqual(rm.storage.keys(), ['/plone/Members/test_user_1_/f2/doc',])

    def testIsMirror(self):
        rm = IMirrorReferenceManager(self.mirror)
        self.failUnless(rm.isMirror(self.mirror, self.f2))

        rm = IMirrorReferenceManager(self.original)
        self.failUnless(rm.isMirror(self.mirror, self.f2))

    def testGetOriginal(self):
        rm = IMirrorReferenceManager(self.mirror)
        self.assertEqual(self.original.getPhysicalPath(), rm.getOriginal().getPhysicalPath())


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestRefmgr))
    return suite

# vim: set ft=python ts=4 sw=4 expandtab :

