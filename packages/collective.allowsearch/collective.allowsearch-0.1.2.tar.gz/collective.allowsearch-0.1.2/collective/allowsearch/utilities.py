# -*- coding: utf-8 -*-
#
# File: utilities.py
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
__revision__  = "$Revision: 52344 $"
__version__   = '$Revision: 52344 $'[11:-2]

from zope import interface
from collective.allowsearch.interfaces import IAllowedRolesAndUsers

from Products.CMFPlone.CatalogTool import allowedRolesAndUsers

class DefaultAllowedRolesAndUsers(object):
    interface.implements(IAllowedRolesAndUsers)

    def __call__(self, obj, portal, **kwargs):
        return allowedRolesAndUsers(obj, portal, **kwargs)

default_allowed_roles_and_users = DefaultAllowedRolesAndUsers()


# vim: set ft=python ts=4 sw=4 expandtab :
