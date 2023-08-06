# -*- coding: utf-8 -*-
## Copyright (C) 2009 Ingeniweb - all rights reserved    

## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program; see the file COPYING. If not, write to the
## Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import base_hasattr

def importFinalSteps(context):
    """Import steps that are not handled by GS import/export handlers
    """

    portal = context.getSite()
    setupGroupDataDelegation(portal)      
    
    
def setupGroupDataDelegation(context):
    """
    Property added in portal_groupdata for Group Delegation
    """    
    gd_tool = getToolByName(context, 'portal_groupdata')
    if not base_hasattr(gd_tool, 'delegated_group_member_managers'):
        gd_tool._setProperty('delegated_group_member_managers', (), 'lines')
