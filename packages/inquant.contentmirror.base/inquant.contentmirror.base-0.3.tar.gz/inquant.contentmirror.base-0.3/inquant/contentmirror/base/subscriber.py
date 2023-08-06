# -*- coding: utf-8 -*-
#
# File: .py
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
__revision__  = "$Revision: 65383 $"
__version__   = '$Revision: 65383 $'[11:-2]

from zope.component import adapter

from zope.app.component.hooks import getSite
from zope.app.container.interfaces import IObjectRemovedEvent, IObjectMovedEvent

from inquant.contentmirror.base.interfaces import IMirroredContent
from inquant.contentmirror.base.interfaces import IContentMirroredEvent, IContentNoLongerMirroredEvent
from inquant.contentmirror.base.interfaces import IMirrorAddedEvent, IMirrorRemovedEvent
from inquant.contentmirror.base.interfaces import IMirrorWillBeAddedEvent, IMirrorWillBeRemovedEvent
from inquant.contentmirror.base.interfaces import IMirrorReferenceManager

from inquant.contentmirror.base.utils import give_new_context
from inquant.contentmirror.base.utils import info, debug

from Products.CMFCore.utils import getToolByName
from Products.Archetypes.interfaces import IObjectEditedEvent

def unindex_object(site, obj):
    pc = getToolByName(site, "portal_catalog")
    pc.unindexObject(obj)

@adapter(IMirroredContent, IObjectMovedEvent)
def ObjectMoved(obj, event):
    info("EVENT ObjectMoved: %s" % event.object.absolute_url())
    IMirrorReferenceManager(event.object).update(event.object)

@adapter(IContentMirroredEvent)
def ContentMirrored(event):
    info("EVENT ContentMirrored: %s" % event.object.absolute_url())
    IMirrorReferenceManager(event.object).initialize(event.object)

@adapter(IContentNoLongerMirroredEvent)
def ContentNoLongerMirrored(event):
    info("EVENT ContentNoLongerMirrored: %s" % event.object.absolute_url())
    IMirrorReferenceManager(event.object).deinitialize(event.object)


@adapter(IMirroredContent, IObjectRemovedEvent)
def ObjectRemoved(obj, event):
    """ An object is going to be removed which happens to be mirrored. If the object is
    not a mirror, remove its mirrors """
    debug("Mirror Object removed: %s" % (obj.absolute_url()))
    refmgr = IMirrorReferenceManager(event.object)
    site = getSite()
    if not refmgr.isMirror(event.object, event.oldParent):
        # we're deleting the original. Delete all mirrors, too.
        for path, mi in refmgr.items():
            container = site.restrictedTraverse(mi["container_path"])
            mirror = give_new_context(obj, container)
            unindex_object(site, mirror)
            debug("Mirror Object removed: removed mirror: %s" % mirror.absolute_url())

@adapter(IMirroredContent, IObjectEditedEvent)
def ObjectEdited(obj, event):
    refmgr = IMirrorReferenceManager(event.object)
    site = getSite()
    path = "/".join(obj.getPhysicalPath())
    if refmgr.opath != path:
        info("Mirror Object EDITED: %s" % (event.object.absolute_url()))
        unindex_object(site, event.object)

@adapter(IMirrorWillBeRemovedEvent)
def MirrorRemoved(event):
    """ An mirrored content is about to be removed. Clean up the catalog. """
    debug("Mirror will be removed: event=%s container=%s object=%s" % (
        event,
        event.container.absolute_url(),
        event.object.absolute_url()
        ))
    refmgr = IMirrorReferenceManager(event.object)
    if refmgr.isMirror(event.object, event.container):
        unindex_object(getSite(), event.object)
        debug("Mirror removed: uncataloged object %s" % (event.object.absolute_url()))

# vim: set ft=python ts=4 sw=4 expandtab :
