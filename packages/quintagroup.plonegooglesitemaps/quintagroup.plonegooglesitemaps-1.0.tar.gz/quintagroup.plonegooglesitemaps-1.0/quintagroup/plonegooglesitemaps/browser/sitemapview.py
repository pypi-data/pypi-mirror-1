from DateTime import DateTime
from commonview import *


class SitemapView(CommonSitemapView):
    """
    Sitemap browser view
    """
    implements(ISitemapView)

    additional_maps = (
        ('modification_date', lambda x:DateTime(x.ModificationDate).HTML4()),
    )

    def getFilteredObjects(self):
        path = self.portal.getPhysicalPath()
        portal_types = self.context.getPortalTypes()
        review_states = self.context.getStates()
        return self.portal_catalog(path = path,
                portal_type = portal_types,
                review_state = review_states)
