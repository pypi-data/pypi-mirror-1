# -*- coding: utf-8 -*-
#
# File: skeleton.py
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
__revision__  = "$Revision: 56670 $"
__version__   = '$Revision: 56670 $'[11:-2]

import unittest

from zope import component
from zope import interface
from zope.publisher.browser import TestRequest
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces.http import IHTTPRequest

from zope.app.testing import ztapi

from zope.traversing.interfaces import ITraversable, TraversalError

from inquant.contentmirror.interfaces import IMirrorUIDManager
from inquant.contentmirror.interfaces import IMirrorContentProvider
from inquant.contentmirror.traverse import MirrorObjectTraverser
from inquant.contentmirror.adapter import UIDLocator
from inquant.contentmirror.tests import base

class TestUIDManager(base.CMTestCase):
    def testAdapterLookup(self):
        self.failUnless(component.queryAdapter(self.folder, IMirrorUIDManager))

    def testUidManager(self):
        manager = IMirrorUIDManager(self.folder)
        manager.set("muh", "17")
        self.assertEqual(manager.get("muh"), "17")

        manager.remove("muh")
        self.failUnless("muh" not in manager.storage.keys())

class TestLocator(base.CMTestCase):
    def afterSetUp(self):
        self.setRoles(('Manager',))
        self.folder.invokeFactory("Folder", "f1")
        self.folder.invokeFactory("Folder", "f2")
        self.f1 = self.folder.f1
        self.f2 = self.folder.f2
        self.f1.invokeFactory("Document", "doc", title="Muh")

        # mirror "doc" which is originally in f1 only to f2 also
        manager = IMirrorUIDManager(self.f2)
        manager.set("doc", self.f1.doc.UID())

    def testLocator(self):
        adapter = UIDLocator(self.f2)
        self.failUnless(adapter.locate("doc"))

class TestTraverser(base.CMTestCase):
    def afterSetUp(self):
        self.setRoles(('Manager',))
        self.folder.invokeFactory("Folder", "f1")
        self.folder.invokeFactory("Folder", "f2")
        self.f1 = self.folder.f1
        self.f2 = self.folder.f2
        self.f1.invokeFactory("Document", "doc", title="Muh")

        # mirror "doc" which is originally in f1 only to f2 also
        manager = IMirrorUIDManager(self.f2)
        manager.set("doc", self.f1.doc.UID())

    def testTraversalAdapterLookupNoMirrorProvider(self):
        request = TestRequest()
        self.assertRaises(
                component.interfaces.ComponentLookupError,
                component.getMultiAdapter((self.f2,request),
                IPublishTraverse)
                )

    def testTraversalAdapterLookup(self):
        request = TestRequest()
        interface.alsoProvides(self.f2,IMirrorContentProvider)
        self.failUnless(
                component.getMultiAdapter((self.f2,request),
                IPublishTraverse)
                )
        interface.noLongerProvides(self.f2,IMirrorContentProvider)

    def testTraversal(self):
        request = TestRequest()
        gsm = component.getGlobalSiteManager()
        interface.alsoProvides(self.f2,IMirrorContentProvider)
        adapter = component.getMultiAdapter((self.f2,request), IPublishTraverse)
        self.failUnless(adapter.publishTraverse(request, "doc"))
        interface.noLongerProvides(self.f2,IMirrorContentProvider)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestUIDManager))
    suite.addTest(unittest.makeSuite(TestLocator))
    suite.addTest(unittest.makeSuite(TestTraverser))
    return suite

# vim: set ft=python ts=4 sw=4 expandtab :

