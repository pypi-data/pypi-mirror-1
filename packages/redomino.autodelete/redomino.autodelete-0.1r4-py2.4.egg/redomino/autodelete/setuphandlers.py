# -*- coding: utf-8 -*-
#
# File: setuphandlers.py
#
# Copyright (c) 2008 by []
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
__author__ = """Davide Moro <davide.moro@redomino.com>"""
__docformat__ = 'plaintext'

from Products.CMFCore.utils import getToolByName
from Products.ExternalMethod.ExternalMethod import manage_addExternalMethod
from redomino.autodelete.config import PROJECTNAME

def setupVarious(context):
    
    # Ordinarily, GenericSetup handlers check for the existence of XML files.
    # Here, we are not parsing an XML file, but we use this text file as a 
    # flag to check that we actually meant for this import step to be run.
    # The file is found in profiles/default.
    
    if context.readDataFile('redomino.autodelete_various.txt') is None:
        return
        
    # additional setup code
    setup_maintenance(context)

def setup_maintenance(context):
    """ Adds the redomino.autodelete setup scripts, if PloneMaintenance is available """
    portal = context.getSite()
    portal_maintenance = getToolByName(portal, 'portal_maintenance', None)

    if portal_maintenance:
        scriptsholder = getattr(portal_maintenance, 'scripts', None)
    
        # redomino.autodelete maintenance script
        if not scriptsholder.hasObject('runAutodelete'):
            manage_addExternalMethod(scriptsholder,
                                     'runAutodelete',
                                     'Delete the expired content',
                                     PROJECTNAME+'.maintenance_utils',
                                     'runAutodelete')
        else:
            # reload of existing external method
            ext_method = getattr(scriptsholder, 'runAutodelete')
            ext_method.reloadIfChanged()
        
