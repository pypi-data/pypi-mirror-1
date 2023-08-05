## -*- coding: utf-8 -*-
## Copyright (C) 2008 Ingeniweb

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

# $Id: zcml.py 57859 2008-01-29 11:21:22Z glenfant $
"""
ZCML fss namespace handling, see meta.zcml
"""
__author__  = 'glenfant <gilles.lenfant@ingeniweb.com>'
__docformat__ = 'restructuredtext'

from zope.interface import Interface
from zope.configuration.fields import GlobalObject, Tokens, PythonIdentifier
from utils import LOG
from FileSystemStorage import FileSystemStorage


class ITypeWithFSSDirective(Interface):
    """Schema for fss:typeWithFSS directive"""

    class_ = GlobalObject(
        title=u'Class',
        description=u'Dotted name of class of AT based content type using FSS',
        required=True)

    fields = Tokens(
        title=u'Fields',
        description=u'Field name or space(s) separated field names',
        value_type=PythonIdentifier(),
        required=True)


def typeWithFSS(_context, class_, fields):
    """Register our monkey patch"""

    _context.action(
        discriminator=None,
        callable=patchATType,
        args=(class_, fields)
        )


def patchATType(class_, fields):
    """Processing the type patch"""

    for fieldname in fields:
        field = class_.schema[fieldname]
        field.storage = FileSystemStorage()
        field.registerLayer('storage', field.storage)
        LOG("Field '%s' of %s is stored in file system.", fieldname, class_.meta_type)
    return
