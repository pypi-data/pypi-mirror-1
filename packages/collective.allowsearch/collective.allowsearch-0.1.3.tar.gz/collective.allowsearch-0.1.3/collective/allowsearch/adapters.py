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
__revision__  = "$Revision: 52347 $"
__version__   = '$Revision: 52347 $'[11:-2]

from zope import component
from zope import interface

from collective.allowsearch.interfaces import IAllowedRolesAndUsers
from collective.allowsearch.interfaces import IAllowAnonymousSearchMarker

class AllowAnonSearch(object):
    """ adapter to which checks for an interface on its context
        to determine if 'Anonymous' users are to view catalog
        brains for the given object. """
    interface.implements(IAllowedRolesAndUsers)

    ROLE = "Anonymous"

    def __init__(self, context):
        self.context = context

    def __call__(self, obj, portal, **kw):
        allowed = component.getUtility(IAllowedRolesAndUsers,u"collective.allowsearch.default")(obj,portal,**kw)
        if IAllowAnonymousSearchMarker.providedBy(obj):
            if self.ROLE not in allowed:
                allowed.append(self.ROLE)
        return allowed

# vim: set ft=python ts=4 sw=4 expandtab :
