# -*- coding: utf-8 -*-
## Copyright (C) 2006 Ingeniweb

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
"""
The FileSystemStorage package
$Id: __init__.py 60004 2008-03-05 12:24:00Z glenfant $
"""

__author__  = ''
__docformat__ = 'restructuredtext'

# Python imports
import os
import sys
from Globals import package_home

# CMF imports
from Products.CMFCore.utils import ContentInit, ToolInit
from Products.CMFCore import permissions as CMFCorePermissions

# Archetypes imports
from Products.Archetypes.public import process_types, listTypes

# Products imports
from iw.fss.config import \
    SKINS_DIR, \
    GLOBALS, \
    PROJECTNAME, \
    DEBUG, \
    INSTALL_EXAMPLE_TYPES_ENVIRONMENT_VARIABLE, \
    PLONE_VERSION


from iw.fss import patches

def initialize(context):
    install_types = DEBUG or \
        os.environ.get(INSTALL_EXAMPLE_TYPES_ENVIRONMENT_VARIABLE)

    if install_types:
        # Import example types
        from iw.fss.examples import FSSItem
        content_types, constructors, ftis = process_types(listTypes(PROJECTNAME),
                                                          PROJECTNAME)
        ContentInit('%s Content' % PROJECTNAME,
                    content_types = content_types,
                    permission = CMFCorePermissions.AddPortalContent,
                    extra_constructors = constructors,
                    fti = ftis,
                    ).initialize(context)

    # Import tool
    from iw.fss.FSSTool import FSSTool
    ToolInit(
        '%s Tool' % PROJECTNAME,
        tools=(FSSTool,),
        product_name=PROJECTNAME,
        icon='tool.gif').initialize(context)

    # setup module aliases to bind all Zope2 products
    import modulealiases
