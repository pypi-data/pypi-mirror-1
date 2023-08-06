# -*- coding: utf-8 -*-
#
# File: adapter.py
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
__revision__  = "$Revision: 63530 $"
__version__   = '$Revision: 63530 $'[11:-2]

import logging

from zope import component
from zope import interface

from zope.annotation.interfaces import IAnnotations, IAttributeAnnotatable
from persistent.dict import PersistentDict

from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName

from inquant.contentmirror.base.interfaces import IMirrorContentProvider
from inquant.contentmirror.base.interfaces import IMirrorContentLocator
from inquant.contentmirror.base.interfaces import IMirrorUIDManager

from inquant.contentmirror.base.utils import info, debug, error


class UIDLocator(object):
    interface.implements(IMirrorContentLocator)

    def __init__(self,context):
        self.context = context
        self.uic = getToolByName(context, "uid_catalog")

    def locate(self, name):
        context = aq_inner(self.context)
        debug("UIDTraverser: trying to locate %s (context %s)" % (name, self.context))
        manager = component.queryAdapter(context, IMirrorUIDManager)
        if not manager:
            error("UIDTraverser: no UID manager")
            return None

        uid = manager.get(name, None)
        if not uid:
            error("UIDTraverser: no UID found for '%s'" % name)
            return None

        debug("UIDTraverser: UID: %s" % uid)

        # fetch the object via UID
        res = self.uic(UID=uid)
        if not len(res):
            debug("UIDTraverser: UID lookup failed")
            return None

        for brain in res:
            obj = brain.getObject()
            if obj is not None:
                return obj


# vim: set ft=python ts=4 sw=4 expandtab :
