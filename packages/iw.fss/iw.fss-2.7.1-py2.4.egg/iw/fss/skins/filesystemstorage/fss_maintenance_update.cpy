## Controller Python Script "fss_maintenance_update"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title= Update FileSystem storage
# Copyright (c) Ingeniweb 2007
# $Id: fss_maintenance_update.cpy 60005 2008-03-05 12:25:20Z glenfant $

from iw.fss.utils import FSSMessageFactory as _

from Products.CMFCore.utils import getToolByName

fss_tool = getToolByName(context, 'portal_fss')

# Update filesystem storage
fss_tool.updateFSS()

context.plone_utils.addPortalMessage(_(u'message_filesystem_storage_updated', default=u"FileSystemStorage updated"))
return state.set(status='success')
