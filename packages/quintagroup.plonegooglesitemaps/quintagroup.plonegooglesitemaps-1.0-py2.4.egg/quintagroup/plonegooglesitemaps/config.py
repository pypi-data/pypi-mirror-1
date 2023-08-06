"""Common configuration constants
"""

PROJECTNAME = 'quintagroup.plonegooglesitemaps'

ADD_PERMISSIONS = {
    # -*- extra stuff goes here -*-
    'Sitemap': 'qPloneGoogleSitemaps: Add Sitemap',
}

SITEMAPS_VIEW_MAP = {
    'content'   : 'sitemap.xml',
    'mobile'    : 'mobile-sitemap.xml',
    'news'      : 'news-sitemap.xml'
}

ping_googlesitemap = 'pingGoogleSitemap'
testing = 0

AVAILABLE_WF_SCRIPTS = [ping_googlesitemap, '']

try:
    from Products.DCWorkflow.events import AfterTransitionEvent
except ImportError:
    IS_PLONE_3 = False
else:
    IS_PLONE_3 = True
