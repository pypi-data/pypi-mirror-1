# Copyright (c) 2006 by BlueDynamics Tyrol - Klein und Partner KEG, Austria
#
# GNU General Public License (GPL)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
#
__author__ = """Jens Klein <jens@bluedynamics.com>, 
                Robert Niederreiter <robertn@bluedynamics.com>"""
__docformat__ = 'plaintext'

import logging
logger = logging.getLogger('PASGroupsFromLDAP')
logger.info('Installing Product')

from Globals import InitializeClass
from AccessControl.Permissions import add_user_folders
from Products.CMFCore import DirectoryView
from Products.PluggableAuthService import registerMultiPlugin
from Products.PASGroupsFromLDAP._plugin import GroupsFromLDAPMultiPlugin
from Products.PASGroupsFromLDAP._plugin import \
    manage_addGroupsFromLDAPMultiPluginForm
from Products.PASGroupsFromLDAP._plugin import addGroupsFromLDAPMultiPlugin

def initialize(context):
    registerMultiPlugin(GroupsFromLDAPMultiPlugin.meta_type)

    context.registerClass(
        GroupsFromLDAPMultiPlugin,
        permission = add_user_folders,
        icon="www/ldap.gif",
        constructors = (
            manage_addGroupsFromLDAPMultiPluginForm,
            addGroupsFromLDAPMultiPlugin,
        ),
        visibility = None
    )



