## Script (Python) "isBibliographyExportable"
##title=Formats the history diff
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=obj=None

from Products.CMFCore.utils import getToolByName

#template = context.REQUEST.PUBLISHED
#template_id = template.getId()
iface = getToolByName(context, 'portal_interface')

#return template_id in ('bibliography_view', 'bibliography_search') or \
return iface.objectImplements(obj, 'Products.CMFBibliographyAT.interfaces.IBibliographyExport') 
