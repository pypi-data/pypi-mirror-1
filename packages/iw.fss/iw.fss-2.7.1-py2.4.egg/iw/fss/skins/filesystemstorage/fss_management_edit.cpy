## Controller Python Script "fss_management_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=rdf_enabled=0, rdf_script=''
##title= Manage FileSystem storage
# Copyright (c) Ingeniweb 2007
# $Id: fss_management_edit.cpy 60005 2008-03-05 12:25:20Z glenfant $

from iw.fss.utils import FSSMessageFactory as _

from Products.CMFCore.utils import getToolByName

fss_tool = getToolByName(context, 'portal_fss')

# Save properties
fss_tool.enableRDF(rdf_enabled)
fss_tool.setRDFScript(rdf_script)

context.plone_utils.addPortalMessage(_(u'message_properties_saved', default=u"Properties saved"))
return state.set(status='success')
