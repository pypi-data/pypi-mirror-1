from Products.CMFCore.utils import getToolByName

PROFILE = "profile-quintagroup.plonegooglesitemaps:default"

def install(self, reinstall=False):
    """ Install skin with GenericSetup install profile
    """
    ps = getToolByName(self, 'portal_setup')
    mtool = getToolByName(self, 'portal_migration')
    plone_version = mtool.getFileSystemVersion()

    if plone_version.startswith('3'):
        # if this is plone 3.x
        (ps.aq_base).__of__(self).runAllImportStepsFromProfile(PROFILE)
    else:
        active_context_id = ps.getImportContextID()
        ps.setImportContext(PROFILE)
        ps.runAllImportSteps()
        ps.setImportContext(active_context_id)
