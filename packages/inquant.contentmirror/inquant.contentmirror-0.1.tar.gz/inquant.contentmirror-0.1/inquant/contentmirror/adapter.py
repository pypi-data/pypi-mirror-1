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
__revision__  = "$Revision: 56669 $"
__version__   = '$Revision: 56669 $'[11:-2]

import logging

from zope import component
from zope import interface

from zope.annotation.interfaces import IAnnotations
from persistent.dict import PersistentDict

from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName

from inquant.contentmirror.interfaces import IMirrorContentLocator
from inquant.contentmirror.interfaces import IMirrorUIDManager

info = logging.getLogger().info

class AnnotationUIDManager(object):

    KEY="inquant.contentmirror.uidmanager"

    def __init__(self, context):
        self.context = context
        s = IAnnotations(context)
        self.storage = s.setdefault(self.KEY, PersistentDict())

    def set(self, key, uid):
        self.storage[key] = uid

    def get(self, key, default=None):
        return self.storage.get(key,default)

    def remove(self,key):
        del self.storage[key]

class UIDLocator(object):
    interface.implements(IMirrorContentLocator)

    def __init__(self,context):
        self.context = context
        self.uic = getToolByName(context, "uid_catalog")

    def locate(self, name):
        context = aq_inner(self.context)
        info("UIDTraverser: trying to locate %s (context %s)" % (name, self.context))
        manager = component.queryAdapter(context, IMirrorUIDManager)
        if not manager:
            info("UIDTraverser: no UID manager")
            return None

        uid = manager.get(name, None)
        if not uid:
            info("UIDTraverser: no UID found for '%s'" % name)
            return None

        info("UIDTraverser: UID: %s" % uid)

        # fetch the object via UID
        res = self.uic(UID=uid)
        if not len(res):
            info("UIDTraverser: UID lookup failed")
            return None

        for brain in res:
            obj = brain.getObject()
            if obj is not None:
                return obj


# vim: set ft=python ts=4 sw=4 expandtab :
