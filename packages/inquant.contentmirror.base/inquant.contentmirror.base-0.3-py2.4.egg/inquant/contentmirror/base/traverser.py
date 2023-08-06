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
__revision__  = "$Revision: 63520 $"
__version__   = '$Revision: 63520 $'[11:-2]

from zope import component
from zope import interface

from zope.publisher.interfaces import NotFound
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.http import IHTTPRequest

from ZPublisher.BaseRequest import DefaultPublishTraverse

from Acquisition import aq_inner, aq_base
from Products.CMFCore.utils import getToolByName

from inquant.contentmirror.base.interfaces import IMirrorContentLocator
from inquant.contentmirror.base.utils import give_new_context
from inquant.contentmirror.base.utils import info, debug

class MirrorObjectTraverser(object):
    """
    A traverser which tries to locate mirrored objects. If such a object can be
    located (by querying the IMirrorObjectLocator), then the object returned by
    the locator is inserted into the context's acquisition chain.
    """
    interface.implements(IPublishTraverse)
    def __init__(self,context,request):
        self.locator = IMirrorContentLocator(context)
        self.default = DefaultPublishTraverse(context,request)
        self.context = context
        self.request = request

    def publishTraverse(self, request, name):
        try:
            obj = self.default.publishTraverse(request, name)
            return obj
        except (NotFound, AttributeError), e:
            context = aq_inner(self.context)
            info("MirrorObjectTraverser: default traverser returned NotFound. %s -> %s" % (self.context,name))

            obj = self.locator.locate(name)
            if obj is None:
                raise e

            obj = give_new_context(obj, context)
            info("MirrorObjectTraverser: ctx %s, name %s -> %s" % (context,name,obj))
            return obj


# vim: set ft=python ts=4 sw=4 expandtab :
