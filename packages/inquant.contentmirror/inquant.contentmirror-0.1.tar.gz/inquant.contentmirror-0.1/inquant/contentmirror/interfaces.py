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
__revision__  = "$Revision: 56669 $"
__version__   = '$Revision: 56669 $'[11:-2]


from zope import interface

class IMirrorContentProvider(interface.Interface):
    """ marker interface for objects providing mirror content """

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

    def get(key, default=None):
        """ return the UID stored for key """

    def set(key, uid):
        """ store a uid for the given key """

    def remove(key):
        """ remove the key from the storage """

# vim: set ft=python ts=4 sw=4 expandtab :
