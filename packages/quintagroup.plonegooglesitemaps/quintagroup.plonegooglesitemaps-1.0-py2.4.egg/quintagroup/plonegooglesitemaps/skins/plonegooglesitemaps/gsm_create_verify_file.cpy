## Script (Python) "create_verify_file"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=verify_filename
##title=Create file for verification
##

from Products.CMFCore.utils import getToolByName
from quintagroup.plonegooglesitemaps.utils import BadRequestException
portal = getToolByName(context, 'portal_url').getPortalObject()
try:
    portal.manage_addFile(verify_filename,title='Verification File')
    portal[verify_filename].manage_addProperty('CreatedBy','quintagroupt.plonegooglesitemaps','string')
except BadRequestException:
    pass
else:
    props = getToolByName(context,'portal_properties').googlesitemap_properties
    vfiles = list(props.getProperty('verification_filenames',[]))
    vfiles.append(verify_filename)
    props.manage_changeProperties(verification_filenames = vfiles)

return state.set(portal_status_message = 'Plone Google Sitemap updated.')
