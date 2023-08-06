## Written by Matias Bordese <matiasb@except.com.ar>
## (c) 2007 ifPeople http://ifpeople.net/

# This file is part of ifSearchMonitor.
#
#     ifSearchMonitor is free software; you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation; either version 2 of the License, or
#     (at your option) any later version.
#
#     ifSearchMonitor is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with ifSearchMonitor; if not, write to the Free Software
#     Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

from Products.Archetypes.public import listTypes
from Products.Archetypes.Extensions.utils import installTypes, install_subskin
from Products.CMFCore.utils import getToolByName
from Products.ifSearchMonitor.config import PROJECTNAME, TOOLNAME, GLOBALS

from StringIO import StringIO

catalog_indexes = (
    { 'name':'SuggestedCriteria',
      'type':'KeywordIndex'
      },)


def install(self,portal):
    out = StringIO()
    install_subskin(self, out, GLOBALS)
    ct = getToolByName(self, 'portal_catalog')
    for idx in catalog_indexes:
        if idx['name'] in ct.indexes():
            out.write("Found the '%s' index in the catalog, nothing changed.\n" % idx['name'])
        else:
            ct.addIndex(**idx)
            ct.manage_reindexIndex(ids=(idx['name'],))
            out.write("Added '%s' (%s) to the catalog.\n" % (idx['name'], idx['type']))
    #from Products.ifSearchMonitor.config import JAVASCRIPTS
    JAVASCRIPTS = [{'id':'recommend.js'}]
    try:
        portal_javascripts = getToolByName(portal, 'portal_javascripts')
        for javascript in JAVASCRIPTS:
            try:
                portal_javascripts.unregisterResource(javascript['id'])
            except:
                pass
            defaults = {'id': ''}
            defaults.update(javascript)
            portal_javascripts.registerScript(**defaults)
    except:
        # No portal_javascripts registry
        pass
    setupTool(self, out)
    registerConfiguration(self, out)
    out.write("Successfully installed %s." % PROJECTNAME)
    return out.getvalue()

def uninstall(self):
    out = StringIO()
    portal_conf = getToolByName(self,'portal_controlpanel')
    portal_conf.unregisterConfiglet(PROJECTNAME)
    return out.getvalue()

def setupTool(portal, out):
    """
    adds the tool to the portal root folder
    """
    try:
        ctool = getToolByName(portal, 'ifSearchMonitor_tool')
    except AttributeError:
        ctool = None

    stats = None
    if ctool is not None:
        stats = ctool._searchStatistics
        portal.manage_delObjects(['ifSearchMonitor_tool'])
        out.write('Deleting old tool')

    addTool = portal.manage_addProduct[PROJECTNAME].manage_addTool
    addTool('ifSearchMonitorTool', None)
    ctool = getToolByName(portal, 'ifSearchMonitor_tool')
    if stats:
        ctool._searchStatistics = stats
    out.write("\nAdded the tool to the portal root folder.\n")

def registerConfiguration(portal, out):
    portal_conf = getToolByName(portal, 'portal_controlpanel')
    portal_conf.registerConfiglet(PROJECTNAME
                                   , PROJECTNAME
                                   , 'string:${portal_url}/ifSearchMonitor_tool/ifSearchMonitor_stats'
                                   , ''                   # a condition   
                                   , 'Manage portal'      # access permission
                                   , 'Products'           # section to which the configlet should be added: 
                                   , 1                    # visibility
                                   , PROJECTNAME                                  
                                   , 'tool.gif' # icon in control_panel
                                   , 'Search statistics'
                                   , None
                                   )
