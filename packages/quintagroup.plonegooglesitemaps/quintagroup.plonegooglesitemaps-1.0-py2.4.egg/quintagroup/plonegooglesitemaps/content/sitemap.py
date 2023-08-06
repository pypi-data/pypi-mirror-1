"""Definition of the Sitemap content type
"""

from zope.interface import implements, directlyProvides

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata
from Products.CMFCore.utils import getToolByName

from quintagroup.plonegooglesitemaps import qPloneGoogleSitemapsMessageFactory as _
from quintagroup.plonegooglesitemaps.interfaces import ISitemap
from quintagroup.plonegooglesitemaps.config import * 

SitemapSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-
    atapi.StringField(
        name='sitemapType',
        storage = atapi.AnnotationStorage(),
        required=True,
        default='content',
        vocabulary=SITEMAPS_VIEW_MAP.keys(),
        widget=atapi.SelectionWidget(
            label=_(u"Sitemap type"),
            visible = {'edit':'invisible', 'view':'invisible'},
            description=_(u"Select Type of the sitemap."),
        ),
    ),
    atapi.LinesField(
        name='portalTypes',
        storage = atapi.AnnotationStorage(),
        required=True,
        default=['Document',],
        vocabulary="availablePortalTypes",
        #schemata ='default',
        widget=atapi.MultiSelectionWidget(
            label=_(u"Define the types"),
            description=_(u"Define the types to be included in sitemap."),
        ),
    ),
    atapi.LinesField(
        name='states',
        storage = atapi.AnnotationStorage(),
        required=True,
        default=['published',],
        vocabulary="getWorkflowStates",
        #schemata ='default',
        widget=atapi.MultiSelectionWidget(
            label=_(u"Review status"),
            description=_(u"You may include items in sitemap depend of their " \
                          u"review state."),
        ),
    ),
    atapi.LinesField(
        name='blackout_list',
        storage = atapi.AnnotationStorage(),
        required=False,
        #default='',
        #schemata ='default',
        widget=atapi.LinesWidget(
            label=_(u"Blackout entries"),
            description=_(u"The objects with the given ids will not be " \
                          u"included in sitemap."),
        ),
    ),
    atapi.LinesField(
        name='reg_exp',
        storage = atapi.AnnotationStorage(),
        required=False,
        #default='',
        #schemata ='default',
        widget=atapi.LinesWidget(
            label=_(u"URL processing Regular Expressions"),
            description=_(u"Provide regular expressions (in Perl syntax), " \
                          u"one per line to be applied to URLs before " \
                          u"including them into Sitemap. For instance, " \
                          u"\"s/\/index_html//\" will remove /index_html " \
                          u"from URLs representing default documents."),
        ),
    ),
    atapi.LinesField(
        name='urls',
        storage = atapi.AnnotationStorage(),
        required=False,
        #default='',
        #schemata ='default',
        widget=atapi.LinesWidget(
            label=_(u"Additional URLs"),
            description=_(u"Define additional URLs that are not objects and " \
                          u"that should be included in sitemap."),
        ),
    ),
    atapi.LinesField(
        name='pingTransitions',
        storage = atapi.AnnotationStorage(),
        required=False,
        vocabulary='getWorkflowTransitions',
        #schemata="default",
        widget=atapi.MultiSelectionWidget(
            label=_(u"Pinging workflow transitions"),
            description=_(u"Select workflow transitions for pinging google on."),
        ),
    ),

))

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

SitemapSchema['id'].widget.ignore_visible_ids = True
SitemapSchema['title'].storage = atapi.AnnotationStorage()
SitemapSchema['title'].required=False
SitemapSchema['title'].widget.visible = {'edit':'invisible', 'view':'invisible'}
SitemapSchema['description'].storage = atapi.AnnotationStorage()
SitemapSchema['description'].widget.visible = {'edit':'invisible', 'view':'invisible'}

schemata.finalizeATCTSchema(SitemapSchema, moveDiscussion=False)
SitemapSchema['relatedItems'].schemata='metadata'
SitemapSchema['relatedItems'].widget.visible = {'edit':'invisible', 'view':'invisible'}

class Sitemap(base.ATCTContent):
    """Search engine Sitemap content type"""
    implements(ISitemap)

    portal_type = "Sitemap"
    schema = SitemapSchema

    #title = atapi.ATFieldProperty('title')
    #description = atapi.ATFieldProperty('description')

    def at_post_create_script(self):
        # Set default layout on creation
        default_layout = SITEMAPS_VIEW_MAP[self.getSitemapType()]
        self._setProperty('layout', default_layout)

    def availablePortalTypes(self):
        pt = getToolByName(self, 'portal_types')
        types = pt.listContentTypes()
        return atapi.DisplayList(zip(types,types))

    def getWorkflowStates(self):
        pw = getToolByName(self,'portal_workflow')
        states = list(set([v for k,v in pw.listWFStatesByTitle()]))
        states.sort()
        return atapi.DisplayList(zip(states, states))

    def getWorkflowTransitions(self):
        wf_trans = []
        pw = getToolByName(self,'portal_workflow')
        for wf_id in pw.getWorkflowIds():
            wf = pw.getWorkflowById(wf_id)
            if not wf:
                continue
            for wf_tr in wf.transitions.values():
                if wf_tr.after_script_name in AVAILABLE_WF_SCRIPTS:
                    wf_trans.append(("%s#%s" % (wf_id,wf_tr.id),
                        "%s : %s (%s)" % (wf_id,wf_tr.id,wf_tr.title_or_id())))
        return atapi.DisplayList(wf_trans)

    def setPingTransitions(self, value, **kw):
        """Add 'Ping sitemap' afterscript for selected workflow transitions.
        """
        self.getField('pingTransitions').set(self, value)
        if not IS_PLONE_3:
            # Update Workflow if needed
            pw = getToolByName(self, 'portal_workflow')
            #ping_googlesitemap = PING_EMETHODS_MAP[self.getSitemapType()]
            transmap = {}
            for key in value:
                if key.find('#')>0:
                    ids = key.split('#')
                    wfid = ids[0]
                    if not wfid in transmap.keys():
                        transmap[wfid]=[]
                    transmap[wfid].append(ids[1])
            for wfid in transmap.keys():
                workflow = pw.getWorkflowById(wfid)
                if ping_googlesitemap not in workflow.scripts.objectIds():
                    workflow.scripts.manage_addProduct['ExternalMethod'].manage_addExternalMethod(
                        ping_googlesitemap,
                        'Ping sitemap',
                        'quintagroup.plonegooglesitemaps.ping_googlesitemap',
                        ping_googlesitemap)
                transitions_set = transmap[wfid]
                for transition in workflow.transitions.values():
                    trid = transition.id
                    tras = transition.after_script_name
                    if (tras == '') and (trid in transitions_set):
                        #set
                        after_script = ping_googlesitemap
                    elif (tras == ping_googlesitemap) and not (trid in transitions_set):
                        #reset
                        after_script = ''
                    else:
                        #avoid properties set
                        continue
                    transition.setProperties(title=transition.title,
                        new_state_id=transition.new_state_id,
                        after_script_name=after_script,
                        actbox_name=transition.actbox_name)

atapi.registerType(Sitemap, PROJECTNAME)
