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


from Products.CMFCore import permissions
from Products.Archetypes.public import listTypes
from Products.CMFCore import utils as cmfutils
from Products.Archetypes.public import *

from ifSearchMonitorTool import ifSearchMonitorTool

from Products.ifSearchMonitor.config import PROJECTNAME, TOOLNAME, SKINS_DIR, GLOBALS
from Products.CMFCore.DirectoryView import registerDirectory

registerDirectory(SKINS_DIR, GLOBALS)

tools = (ifSearchMonitorTool,)

def initialize(context):
    import ifSearchMonitorTool

    cmfutils.ToolInit(TOOLNAME, tools=tools,
                   product_name=PROJECTNAME, icon='tool.gif',
                   ).initialize(context)
