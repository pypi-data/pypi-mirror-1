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

__author__ = """Robert Niederreiter <robertn@bluedynamics.com>"""
__docformat__ = 'plaintext'

from Products.PluggableAuthService.interfaces.plugins import IGroupsPlugin
from Products.PluggableAuthService.interfaces.plugins import \
    IGroupEnumerationPlugin
from Products.PluggableAuthService.interfaces.plugins import IPropertiesPlugin
from Products.PlonePAS.plugins.group import IGroupIntrospection

PLUGINID = 'groups_from_ldap'

def isNotThisProfile(context):
    return context.readDataFile("pasgroupsfromldap_marker.txt") is None

def setupPlugin(context):
    if isNotThisProfile(context):
        return 
    portal = context.getSite()
    pas = portal.acl_users
    registry = pas.plugins
    groupplugins = [id for id, pi in registry.listPlugins(IGroupsPlugin)]
    if PLUGINID not in groupplugins:
        factories = pas.manage_addProduct['PASGroupsFromLDAP']    
        factories.manage_addGroupsFromLDAPMultiPlugin(PLUGINID,
                                                      'Plone groups from LDAP',
                                                      '127.0.0.1',
                                                      '389',
                                                      'cn=admin,dc=domain,dc=com',
                                                      'secret',
                                                      'ou=groups,dc=domain,dc=com',
                                                      'SUBTREE',
                                                      'posixGroup',
                                                      'no',
                                                      'groupid',
                                                      'groupid',
                                                      'uid',
                                                      REQUEST=None)
        registry.activatePlugin(IGroupsPlugin, PLUGINID )
        registry.activatePlugin(IGroupEnumerationPlugin, PLUGINID )
        registry.activatePlugin(IGroupIntrospection, PLUGINID )
        registry.activatePlugin(IPropertiesPlugin, PLUGINID )
