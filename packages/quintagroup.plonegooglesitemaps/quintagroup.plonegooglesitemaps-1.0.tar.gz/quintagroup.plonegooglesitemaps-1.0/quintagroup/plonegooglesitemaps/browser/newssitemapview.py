from DateTime import DateTime
from commonview import *

class NewsSitemapView(CommonSitemapView):
    """
    Mobile Sitemap browser view
    """
    implements(ISitemapView)

    additional_maps = (
        ('publication_date', lambda x:DateTime(x.EffectiveDate).HTML4()),
        ('keywords', lambda x:', '.join(x.Subject))
    )

    def getFilteredObjects(self):
        path = self.portal.getPhysicalPath()
        portal_types = self.context.getPortalTypes()
        review_states = self.context.getStates()
        min_date = DateTime() - 3
        res = self.portal_catalog(path = path,
                portal_type = portal_types,
                review_state = review_states,
                effective = {"query": min_date,
                             "range": "min" })
        return res