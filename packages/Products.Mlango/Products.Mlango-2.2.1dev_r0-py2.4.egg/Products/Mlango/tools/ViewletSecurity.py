# Copyright (C) 2008  Goldmund, Wyldebeast & Wunderliebe
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA
from Products.CMFCore.utils import getToolByName


""" Security for viewlets. The viewlet registry returns a list of
    viewlets. A viewlet kan have the dict key 'roles' with a list
    of roles that are required to show the viewlet.

    Use viewletSecurity as a decorator on a function that uses the 
    viewlet registry to get a list of viewlets and returns the same
    list of viewlets. Viewlet security checks if a user has the 
    appropriate role.
"""

def viewletSecurity(func):
    def secureViewletList(*args, **kwargs):
        """..resistance is futile"""
        context =  args[0]
        unsecureList = func(*args, **kwargs)
        secureList = []
        
        member = context.portal_membership.getAuthenticatedMember()
        memberRoles = member.getRoles()

        # add a viewlet if it has no role key
        secureList +=( [v for v in unsecureList if not context.getViewletInfo(v).get('roles') ] )
        # add a viewlet if the role key matches the users group
        for role in memberRoles:
            secureList +=( [v for v in unsecureList\
                 if context.getViewletInfo(v).get('roles')\
                    and role in context.getViewletInfo(v).get('roles')]  )
        return secureList

    return secureViewletList

