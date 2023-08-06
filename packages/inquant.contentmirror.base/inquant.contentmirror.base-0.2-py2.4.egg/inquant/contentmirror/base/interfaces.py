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
__revision__  = "$Revision: 62293 $"
__version__   = '$Revision: 62293 $'[11:-2]


from zope import interface

from zope.component.interfaces import IObjectEvent

class IMirrorContentProvider(interface.Interface):
    """ marker interface for objects providing mirror content """

class IMirroredContent(interface.Interface):
    """ marker interface for content which is in fact mirrored somewhere """

class IMirroredContentManager(interface.Interface):
    """ manager which mirrors content """

    def addMirror(obj, container):
        """ add a mirror object to a container """

    def removeMirror(obj, container):
        """ remove the object mirror form the container
            returns True if mirror was removed.
            returns False if object was not mirrored here.
        """

class IMirrorReferenceManager(interface.Interface):
    """ manages references of mirrors of a object """

    def add(obj, container):
        """ record a reference of the object to the container """

    def remove(obj, container):
        """ record the fact that 'obj' is no longer mirrored in 'container' """

    def initialize(original):
        """ set information about the original object """

    def update(original):
        """ update information about the original object """

    def deinitialize(original):
        """ content no longer mirrored, record the fact """

    def getOriginal():
        """ return the original object """

    def isMirror(obj, container):
        """ return True if obj is a mirror in container """

    def items():
        """ return a iterable of dicts { container_uid, container_path } which
            record the places this object is mirrored to. """

class IContentMirroredEvent(IObjectEvent):
    pass

class IContentNoLongerMirroredEvent(IObjectEvent):
    pass

class IMirrorWillBeAddedEvent(IObjectEvent):
    container = interface.Attribute(u"the container the mirror is added to")
    object    = interface.Attribute(u"the object to be mirrored")

class IMirrorAddedEvent(IObjectEvent):
    container = interface.Attribute(u"the container the mirror is added to")
    object    = interface.Attribute(u"the object to be mirrored")

class IMirrorWillBeRemovedEvent(IObjectEvent):
    container = interface.Attribute(u"the container the mirror is removed from")
    object    = interface.Attribute(u"the mirrored object")

class IMirrorRemovedEvent(IObjectEvent):
    container = interface.Attribute(u"the container the mirror is removed from")
    object    = interface.Attribute(u"the mirrored object")

class IMirrorContentLocator(interface.Interface):
    """ an adapter which is able to lookup and return a content
        object.
        rhe content object returned will be inserted (mirrored) at the
        adapter's context. """

    def locate(name):
        """ locate a content object identified by the key "name"  and
            return it """

class IMirrorUIDManager(interface.Interface):
    """
    Storage for key->UID mappings.
    """

    # XXX: this should behave like a mapping.

    def keys(self):
        """ """

    def get(key, default=None):
        """ return the UID stored for key """

    def set(key, uid):
        """ store a uid for the given key """

    def remove(key):
        """ remove the key from the storage """

# vim: set ft=python ts=4 sw=4 expandtab :
