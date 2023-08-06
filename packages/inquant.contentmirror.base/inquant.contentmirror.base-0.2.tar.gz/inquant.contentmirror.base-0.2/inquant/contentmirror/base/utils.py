# -*- coding: utf-8 -*-
#
# File: utils.py
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
__revision__  = "$Revision: 62284 $"
__version__   = '$Revision: 62284 $'[11:-2]

import logging
from Acquisition import aq_base

info = logging.getLogger("contentmirror").info
debug = logging.getLogger("contentmirror").debug
error = logging.getLogger("contentmirror").error

def give_new_context(obj, context):
    obj = aq_base(obj)
    obj = obj.__of__(context)
    return obj


# vim: set ft=python ts=4 sw=4 expandtab :
