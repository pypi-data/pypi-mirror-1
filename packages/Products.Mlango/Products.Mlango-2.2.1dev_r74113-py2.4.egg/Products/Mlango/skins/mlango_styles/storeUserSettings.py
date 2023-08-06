## Script (Python) "storeUserSettings"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Store user settings
##

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

tool = context.portal_mlangotool
user_id = context.portal_membership.getAuthenticatedMember().getId()

if not user_id:
  return

data = {}
minmax = {}
dashboard = ""
for p in context.REQUEST.keys():

  if p.find("col_") != -1:
    data[p] = context.REQUEST.get(p)
  if p.find("min") != -1:
    minmax[p] = context.REQUEST.get(p)
  if p.find("dashboard_id") != -1:
    dashboard_id = context.REQUEST.get(p)

print data

tool.updateUserSettings(user_id, dashboard_id, data)
tool.updateUserSettings(user_id, dashboard_id, minmax)

context.REQUEST.RESPONSE.setHeader('Content-type','text/xml')

print '<xml>stored: %s</xml>' % (data)
print '<xml>stored: %s</xml>' % (minmax)

return printed
