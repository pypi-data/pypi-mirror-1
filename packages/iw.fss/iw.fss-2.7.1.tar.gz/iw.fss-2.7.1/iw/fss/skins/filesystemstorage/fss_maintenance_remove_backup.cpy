## Controller Python Script "fss_maintenance_remove_backup"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=days=0
##title= Remove backups
# Copyright (c) Ingeniweb 2007
# $Id: fss_maintenance_remove_backup.cpy 60005 2008-03-05 12:25:20Z glenfant $

from iw.fss.utils import FSSMessageFactory as _

from Products.CMFCore.utils import getToolByName

fss_tool = getToolByName(context, 'portal_fss')

# Remove backups
fss_tool.removeBackups(days)

context.plone_utils.addPortalMessage(_(u'message_backups_removed', default=u"Backups removed"))
return state.set(status='success')


