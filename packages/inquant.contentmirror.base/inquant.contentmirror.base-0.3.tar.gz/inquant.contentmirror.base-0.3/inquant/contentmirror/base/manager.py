# -*- coding: utf-8 -*-
#
# File: manager.py
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

from zope import component
from zope import interface

from zope.annotation.interfaces import IAnnotations, IAttributeAnnotatable
from zope.app.component.hooks import getSite
from zope.event import notify

from persistent.dict import PersistentDict
from Acquisition import aq_inner

from inquant.contentmirror.base.interfaces import IContentMirroredEvent, IContentNoLongerMirroredEvent
from inquant.contentmirror.base.interfaces import IMirrorAddedEvent, IMirrorRemovedEvent
from inquant.contentmirror.base.interfaces import IMirrorWillBeAddedEvent, IMirrorWillBeRemovedEvent
from inquant.contentmirror.base.interfaces import IMirroredContent
from inquant.contentmirror.base.interfaces import IMirrorReferenceManager
from inquant.contentmirror.base.interfaces import IMirrorUIDManager
from inquant.contentmirror.base.interfaces import IMirrorContentProvider
from inquant.contentmirror.base.interfaces import IMirroredContentManager

from inquant.contentmirror.base.utils import give_new_context, info, debug

class ContentMirrored(object):
    interface.implements(IContentMirroredEvent)
    def __init__(self, obj):
        self.object = obj

class ContentNoLongerMirrored(object):
    interface.implements(IContentNoLongerMirroredEvent)
    def __init__(self, obj):
        self.object = obj

class MirrorAdded(object):
    interface.implements(IMirrorAddedEvent)
    def __init__(self, obj, container):
        self.object = obj
        self.container = container

class MirrorRemoved(MirrorAdded):
    interface.implements(IMirrorRemovedEvent)

class MirrorWillBeAdded(MirrorAdded):
    interface.implements(IMirrorWillBeAddedEvent)

class MirrorWillBeRemoved(MirrorRemoved):
    interface.implements(IMirrorWillBeRemovedEvent)

class AnnotationUIDManager(object):

    KEY="inquant.contentmirror.uidmanager"

    interface.implements(IMirrorUIDManager)
    component.adapts(IAttributeAnnotatable)

    def __init__(self, context):
        self.context = context
        s = IAnnotations(context)
        self.storage = s.setdefault(self.KEY, PersistentDict())

    def items(self):
        return self.storage.items()

    def keys(self):
        return self.storage.keys()

    def set(self, key, uid):
        self.storage[key] = uid

    def get(self, key, default=None):
        return self.storage.get(key,default)

    def remove(self,key):
        del self.storage[key]

class DefaultReferenceManager(object):
    """ this default implementation stores information on where a content is
    mirrored on the conten itself using annotations """

    component.adapts(IMirroredContent)
    interface.implements(IMirrorReferenceManager)

    KEY="inquant.contentmirror.refmanager.mirrors"
    KEY_OPATH="inquant.contentmirror.refmanager.original"

    def __init__(self, context):
        self.context = aq_inner(context)

    def _make_key(self, obj, container):
        return "%s/%s" % ("/".join(container.getPhysicalPath()), obj.getId())

    @property
    def storage(self):
        s = IAnnotations(self.context)
        return s[self.KEY]

    @property
    def opath(self):
        s = IAnnotations(self.context)
        return s[self.KEY_OPATH]

    def initialize(self, original):
        s = IAnnotations(self.context)
        s[self.KEY] = PersistentDict()
        s[self.KEY_OPATH] = "/".join(original.getPhysicalPath())

    def deinitialize(self, original):
        s = IAnnotations(self.context)
        del s[self.KEY]
        del s[self.KEY_OPATH]

    def update(self, original):
        info("update: old %s" % self.opath )
        s = IAnnotations(self.context)
        s[self.KEY_OPATH] = "/".join(original.getPhysicalPath())
        info("update: new %s" % self.opath )

    def add(self, obj, container):
        notify(MirrorWillBeAdded(obj,container))
        key = self._make_key(obj,container)
        d = dict(
                container_uid  = container.UID(),
                container_path = "/".join(container.getPhysicalPath()),
        )
        self.storage[key] = d
        notify(MirrorAdded(obj,container))
        info("DefaultReferenceManager: added %s: %s" % (key, d))

    def remove(self, obj, container):
        notify(MirrorWillBeRemoved(obj,container))
        key = self._make_key(obj,container)
        del self.storage[key]
        debug("DefaultReferenceManager: removed %s" % key)
        notify(MirrorRemoved(obj,container))

        # inform caller if this was the last mirror
        if not len(self.storage.keys()):
            return True
        else:
            return False

    def isMirror(self, obj, container):
        """ return True if the object given is a mirror """
        key = self._make_key(obj,container)
        return key == self.opath

    def getOriginal(self):
        site = getSite()
        return site.restrictedTraverse(self.opath)

    def items(self):
        return self.storage.items()



class DefaultMirrorManager(object):
    interface.implements(IMirroredContentManager)

    def addMirror(self, obj, container):
        # mark the container if not already marked
        if not IMirrorContentProvider.providedBy(container):
            interface.alsoProvides(container,IMirrorContentProvider)

        # add the UID of the object to be mirrored to the UID manager
        uid_manager = IMirrorUIDManager(container)
        if uid_manager.get(obj.getId()) == obj.UID():
            # already mirrored here
            return
        uid_manager.set(obj.getId(), obj.UID())

        # give obj a new context
        new_obj = give_new_context(obj, container)

        if not IMirroredContent.providedBy(obj):
            # content is not mirrored already. Mark it.
            interface.alsoProvides(obj, IMirroredContent)
            notify(ContentMirrored(obj))

        # get a ref manager and add a reference
        refmgr = IMirrorReferenceManager(obj)
        refmgr.add(new_obj, container)

        # reindex object
        # new_obj.reindexObject()

        info("DefaultMirrorManager: added mirror of %s to %s" % ( new_obj.absolute_url(), container.absolute_url()))

    def removeMirror(self, obj, container):
        if not IMirrorContentProvider.providedBy(container):
            return False

        if not IMirroredContent.providedBy(obj):
            return False

        # remove obj's UID form the manager
        uid_manager = IMirrorUIDManager(container)
        if not uid_manager.get(obj.getId()):
            return False

        # adjust acquisition chain
        new_obj = give_new_context(obj, container)

        uid_manager.remove(obj.getId())

        # get a ref manager and add a reference
        refmgr = IMirrorReferenceManager(obj)
        if refmgr.remove(new_obj, container):
            # last mirror removed, notify and unmark **OBJECT**.
            original = refmgr.getOriginal()
            notify(ContentNoLongerMirrored(original))
            interface.noLongerProvides(original, IMirroredContent)

        # if no more mirrors available, unmark **CONTAINER**
        if not uid_manager.keys():
            interface.noLongerProvides(container, IMirrorContentProvider)

        info("DefaultMirrorManager: removed mirror of %s in %s" % (new_obj.absolute_url(), container.absolute_url()))
        return True

# vim: set ft=python ts=4 sw=4 expandtab :
