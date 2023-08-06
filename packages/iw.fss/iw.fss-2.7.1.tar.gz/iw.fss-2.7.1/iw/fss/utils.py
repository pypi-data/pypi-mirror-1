## -*- coding: utf-8 -*-
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
$Id: utils.py 60006 2008-03-05 12:26:33Z glenfant $
"""

__author__  = ''
__docformat__ = 'restructuredtext'

import logging

from AccessControl import ModuleSecurityInfo
from zope.i18nmessageid import MessageFactory

# Archetypes imports
from Products.Archetypes.Field import ImageField
from FileSystemStorage import FileSystemStorage

import config

def getFieldValue(self, name):
    """Returns field value of an object

    @param name: Name of the field
    """

    field = self.getField(name)
    if not field:
        # Get Image fields
        # Check for scales
        found = False
        fields = [x for x in self.Schema().fields() if isinstance(x, ImageField)]
        for field in fields:
            field_name = field.getName()
            names = ['%s_%s' % (field_name, x) for x in field.getAvailableSizes(self).keys()]
            if name in names:
                obj = field.getStorage(self).get(name, self)
                found = True
                break
        if not found:
            raise AttributeError(name)
        return obj.__of__(self)

    # Standard field
    accessor = field.getAccessor(self)

    if accessor is None:
        return None

    return accessor()

logger = logging.getLogger(config.PROJECTNAME)
LOG = logger.info

def patchATType(class_, fields):
    """Processing the type patch"""
    global patchedTypesRegistry

    for fieldname in fields:
        field = class_.schema[fieldname]
        former_storage = field.storage
        field.storage = FileSystemStorage()
        field.registerLayer('storage', field.storage)
        if patchedTypesRegistry.has_key(class_):
            patchedTypesRegistry[class_][fieldname] = former_storage
        else:
            patchedTypesRegistry[class_] = {fieldname: former_storage}
        LOG("Field '%s' of %s is stored in file system.", fieldname, class_.meta_type)
    return

# We register here the types that have been patched for migration purpose
patchedTypesRegistry = {
    # {content class : {field name: storage, ...}, ...}
    }

FSSMessageFactory = MessageFactory(config.I18N_DOMAIN)
ModuleSecurityInfo('iw.fss.utils').declarePublic('FSSMessageFactory')
