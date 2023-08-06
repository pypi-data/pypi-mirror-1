#
# Tests for quintagroup.plonegooglesitemaps
#

import re, sys
from urllib import urlencode
from StringIO import StringIO
import unittest

from zope.testing import doctestunit
from zope.component import testing
from Testing import ZopeTestCase as ztc

from Products.Five import zcml
from Products.Five import fiveconfigure

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite
from Products.CMFPlone.utils import _createObjectByType

from XMLParser import parse, hasURL

import quintagroup.plonegooglesitemaps
from quintagroup.plonegooglesitemaps.config import ping_googlesitemap

quintagroup.plonegooglesitemaps.config.testing = 1

class MixinTestCase:
    """ Define layer and common afterSetup method with package installation.
        Package installation on plone site setup impossible because of
        five's registerPackage directive not recognized on module initializing.
    """
    layer = PloneSite

    def afterSetUp(self):
        self.loginAsPortalOwner()


class TestCase(MixinTestCase, ptc.PloneTestCase):
    """ For unit tests """

class FunctionalTestCase(MixinTestCase, ptc.FunctionalTestCase):
    """ For functional tests """

# Initialize all needed zcml directives
fiveconfigure.debug_mode = True
from Products import Five, CMFCore, GenericSetup
zcml.load_config('meta.zcml', Five)
zcml.load_config('meta.zcml', CMFCore)
zcml.load_config('meta.zcml', GenericSetup)
zcml.load_config('permissions.zcml', Five)

# Force quintagroup.plonegooglesitemaps zcml initialization
zcml.load_config('configure.zcml', quintagroup.plonegooglesitemaps)
fiveconfigure.debug_mode = False

# Install quintagroup.plonegooglesitemaps package and Plone site
# with the default profile for the package
PRODUCT = 'quintagroup.plonegooglesitemaps'
ptc.installPackage(PRODUCT)
ptc.setupPloneSite( extension_profiles=("%s:default" % PRODUCT,))


class TestGoogleSitemapsInstallation(TestCase):

    def testType(self):
        pt = self.portal.portal_types
        self.assert_('Sitemap' in pt.objectIds(), 
            'No "Sitemap" type after installation')
        #Test views
        views = pt.getTypeInfo('Sitemap').view_methods
        self.assert_('sitemap.xml' in views, 
            'No "sitemap.xml" view for Sitemap type')
        self.assert_('mobile-sitemap.xml' in views, 
            'No "mobile-sitemap.xml" view for Sitemap type')
        self.assert_('news-sitemap.xml' in views, 
            'No "news-sitemap.xml" view for Sitemap type')

    def testGSMProperties(self):
        pp = self.portal.portal_properties

        # Test types_not_searched
        self.assert_("Sitemap" in pp['site_properties'].getProperty('types_not_searched'), 
            'No "Sitemap" added to types not searched on installation')
        # Test metaTypesNotToList
        self.assert_("Sitemap" in pp['navtree_properties'].getProperty('metaTypesNotToList'), 
            'No "Sitemap" added to types not to list on installation')

        # Test 'googlesitemap_properties'
        self.assert_('googlesitemap_properties' in pp.objectIds(), 
            'No "googlesitemap_properties" after installation')
        qsmprops = pp['googlesitemap_properties']
        self.assert_(qsmprops.hasProperty('verification_filenames'),
            'No "verification_filenames" property added on installation')

    def testSkins(self):
        ps = self.portal.portal_skins
        self.assert_('plonegooglesitemaps' in ps.objectIds(), 
            'No "plonegooglesitemaps" skin layer in portal_skins')
        self.assert_('plonegooglesitemaps' in ps.getSkinPath(ps.getDefaultSkin()),
            'No "plonegooglesitemaps" skin layer in default skin')

    def testConfiglet(self):
        cp = self.portal.portal_controlpanel
        self.assert_([1 for ai in cp.listActionInfos() if ai['id']=='GoogleSitemaps'], 
            'No "GoogleSitemaps" configlet added to plone control panel')


class TestSitemapType(FunctionalTestCase):

    def afterSetUp(self):
        super(TestSitemapType, self).afterSetUp()
        self.auth = 'admin:admin'
        self.contentSM = _createObjectByType('Sitemap', self.portal, id='google-sitemaps')
        self.portal.portal_membership.addMember('admin', 'admin', ('Manager',), [])

    def testFields(self):
        field_ids = map(lambda x:x.getName(), self.contentSM.Schema().fields())
        # test old Sitemap settings fields
        self.assert_('id' in field_ids)
        self.assert_('portalTypes' in field_ids)
        self.assert_('states' in field_ids)
        self.assert_('blackout_list' in field_ids)
        self.assert_('urls' in field_ids)
        self.assert_('pingTransitions' in field_ids)
        # test new sitemap type field
        self.assert_('sitemapType' in field_ids)

    def testSitemapTypes(self):
        sitemap_types = self.contentSM.getField('sitemapType').Vocabulary().keys()
        self.assert_('content' in sitemap_types)
        self.assert_('mobile' in sitemap_types)
        self.assert_('news' in sitemap_types)

    def testAutoSetLayout(self):
        response = self.publish('/%s/createObject?type_name=Sitemap' % \
                                self.portal.absolute_url(1), basic=self.auth)
        location = response.getHeader('location')
        newurl = location[location.find('/'+self.portal.absolute_url(1)):]

        msm_id = 'mobile_sitemap'
        form = {'id': msm_id,
                'sitemapType':'mobile',
                'portalTypes':['Document',],
                'states':['published'],
                'form_submit':'Save',
                'form.submitted':1,
                }
        post_data = StringIO(urlencode(form))
        response = self.publish(newurl, request_method='POST', stdin=post_data, basic=self.auth)
        msitemap = getattr(self.portal, msm_id)

        self.assertEqual(msitemap.defaultView(), 'mobile-sitemap.xml')

    def txestPingSetting(self):
        pwf = self.portal.portal_workflow['plone_workflow']
        self.assertEqual(self.contentSM.getPingTransitions(), ())

        self.contentSM.setPingTransitions(('plone_workflow#publish',))
        self.assertEqual(self.contentSM.getPingTransitions(), ('plone_workflow#publish',))
        self.assert_(ping_googlesitemap in pwf.scripts.keys(),"Not add wf script")


class TestGoogleSitemaps(FunctionalTestCase):

    def afterSetUp(self):
        super(TestGoogleSitemaps, self).afterSetUp()

        self.workflow = self.portal.portal_workflow
        self.auth = 'admin:admin'
        _createObjectByType('Sitemap', self.portal, id='google-sitemaps')
        self.sitemapUrl = '/'+self.portal.absolute_url(1) + '/google-sitemaps'
        self.portal.portal_membership.addMember('admin', 'admin', ('Manager',), [])
        self.gsm_props = self.portal.portal_properties['googlesitemap_properties']

        # Add testing document to portal
        my_doc = self.portal.invokeFactory('Document', id='my_doc')
        self.my_doc = self.portal['my_doc']
        self.my_doc.edit(text_format='plain', text='hello world')


    def testSitemap(self):
        sitemap = self.publish(self.sitemapUrl, self.auth).getBody()
        parsed_sitemap = parse(sitemap)
        start = parsed_sitemap['start']
        data = parsed_sitemap['data']
        self.assert_('urlset' in start.keys())
        self.assertFalse(self.my_doc.absolute_url(0) in data,
                         'Wrong content present in the sitemap')

        self.workflow.doActionFor(self.my_doc, 'publish')

        sitemap = self.publish(self.sitemapUrl, self.auth).getBody()
        parsed_sitemap = parse(sitemap)
        start = parsed_sitemap['start']
        data = parsed_sitemap['data']
        self.assertEqual(len(start.keys()), 4)
        self.assert_('urlset' in start.keys())
        self.assert_('url' in start.keys())
        self.assert_('loc' in start.keys())
        self.assert_('lastmod' in start.keys())

        self.assertTrue(self.my_doc.absolute_url(0) in data, 'Incorect url')

    def testVerificationFileCreation(self):
        self.portal.gsm_create_verify_file('verif_file')

        vf_created = hasattr(self.portal, 'verif_file')
        self.assert_(vf_created, 'Verification file not created')

    def testVerificationForm(self):
        verifyConfigUrl = '/'+self.portal.absolute_url(1) + '/prefs_gsm_verification'
        verif_config = self.publish(verifyConfigUrl, self.auth).getBody()
        rexp_input_acitve = re.compile('<input\s+name="verify_filename"\s+([^>]*)>', re.I|re.S)
        rexp_button_acitve = re.compile('<input\s+name="form.button.CreateFile"\s+([^>]*)>', re.I|re.S)
        rexp_delete_button = re.compile('<input\s+name="form.button.DeleteFile"\s+[^>]*>', re.I|re.S)

        input_acitve = rexp_input_acitve.search(verif_config)
        button_acitve = rexp_button_acitve.search(verif_config)
        delete_button = rexp_delete_button.match(verif_config)

        self.assert_(input_acitve and not 'disabled' in input_acitve.groups(1))
        self.assert_(button_acitve and not 'disabled' in button_acitve.groups(1))
        self.assert_(not delete_button)

        self.portal.gsm_create_verify_file('verif_file')

        input_acitve = rexp_input_acitve.search(verif_config)
        button_acitve = rexp_button_acitve.search(verif_config)
        delete_button = rexp_delete_button.match(verif_config)

        verif_config = self.publish(verifyConfigUrl, self.auth).getBody()
        self.assert_(input_acitve and not 'disabled' in input_acitve.groups(1))
        self.assert_(not delete_button)

    def testMultiplyVerificationFiles(self):
        verifyConfigUrl = '/'+self.portal.absolute_url(1) + '/prefs_gsm_verification'

        form = {'verify_filename':'verif_file_1',
                'form.button.CreateFile': 'Create verification file',
                'form.submitted':1}
        post_data = StringIO(urlencode(form))
        response = self.publish(verifyConfigUrl, request_method='POST',
                                stdin=post_data, basic=self.auth)
        self.assertEqual(response.getStatus(), 200)
        self.assert_('verif_file_1' in self.gsm_props.getProperty('verification_filenames',[]),
                     self.gsm_props.getProperty('verification_filenames',[]))

        form = {'verify_filename':'verif_file_2',
                'form.button.CreateFile': 'Create verification file',
                'form.submitted':1}
        post_data = StringIO(urlencode(form))
        response = self.publish(verifyConfigUrl, request_method='POST',
                                stdin=post_data, basic=self.auth)
        self.assertEqual(response.getStatus(), 200)
        self.assert_([1 for vf in ['verif_file','verif_file_2'] \
                      if vf in self.gsm_props.getProperty('verification_filenames',[])],
                     self.gsm_props.getProperty('verification_filenames',[]))


class TestSettings(FunctionalTestCase):

    def afterSetUp(self):
        super(TestSettings, self).afterSetUp()

        self.workflow = self.portal.portal_workflow
        self.gsm_props = self.portal.portal_properties['googlesitemap_properties']
        self.auth = 'admin:admin'
        self.contentSM = _createObjectByType('Sitemap', self.portal, id='google-sitemaps')

        self.sitemapUrl = '/'+self.portal.absolute_url(1) + '/google-sitemaps'

        self.portal.portal_membership.addMember('admin', 'admin', ('Manager',), [])

        # Add testing document to portal
        my_doc = self.portal.invokeFactory('Document', id='my_doc')
        self.my_doc = self.portal['my_doc']
        self.my_doc.edit(text_format='plain', text='hello world')
        self.my_doc_url = self.my_doc.absolute_url()

    def testMetaTypeToDig(self):
        self.workflow.doActionFor(self.my_doc, 'publish')
        sitemap = self.publish(self.sitemapUrl, self.auth).getBody()
        self.assert_(hasURL(sitemap, self.my_doc_url))

        self.contentSM.setPortalTypes([])

        sitemap = self.publish(self.sitemapUrl, self.auth).getBody()
        self.assert_(not hasURL(sitemap, self.my_doc_url))

        self.contentSM.setPortalTypes(['Document'])

        sitemap = self.publish(self.sitemapUrl, self.auth).getBody()
        self.assert_(hasURL(sitemap, self.my_doc_url))

    def testStates(self):
        self.workflow.doActionFor(self.my_doc, 'publish')
        self.contentSM.setStates(['visible'])

        sitemap = self.publish(self.sitemapUrl, self.auth).getBody()
        self.assert_(not hasURL(sitemap, self.my_doc_url))

        self.contentSM.setStates(['published'])

        sitemap = self.publish(self.sitemapUrl, self.auth).getBody()
        self.assert_(hasURL(sitemap, self.my_doc_url))

    def test_blackout_entries(self):
        self.workflow.doActionFor(self.my_doc, 'publish')
        self.contentSM.setBlackout_list((self.my_doc.getId(),))

        sitemap = self.publish(self.sitemapUrl, self.auth).getBody()
        self.assert_(not hasURL(sitemap, self.my_doc_url))

        self.contentSM.setBlackout_list([])
        sitemap = self.publish(self.sitemapUrl, self.auth).getBody()
        self.assert_(hasURL(sitemap, self.my_doc_url))

    def test_regexp(self):
        self.workflow.doActionFor(self.my_doc, 'publish')
        sitemap = self.publish(self.sitemapUrl, self.auth).getBody()
        self.assert_(not hasURL(sitemap, self.portal.absolute_url()))

        regexp = "s/\/%s//"%self.my_doc.getId()
        self.contentSM.setReg_exp([regexp])

        sitemap = self.publish(self.sitemapUrl, self.auth).getBody()
        self.assert_(hasURL(sitemap, self.portal.absolute_url()))

    def test_add_urls(self):
        self.contentSM.setUrls(['http://w1', 'w2', '/w3'])
        w1_url = 'http://w1'
        w2_url = self.portal.absolute_url() + '/w2'
        w3_url = self.portal.getPhysicalRoot().absolute_url() + '/w3'
        sitemap = self.publish(self.sitemapUrl, self.auth).getBody()

        self.assert_(hasURL(sitemap, w1_url))
        self.assert_(hasURL(sitemap, w2_url))
        self.assert_(hasURL(sitemap, w3_url))


class TestPinging(FunctionalTestCase):

    def afterSetUp(self):
        super(TestPinging, self).afterSetUp()

        self.workflow = self.portal.portal_workflow
        self.workflow.setChainForPortalTypes(pt_names=('News Item','Document'),
                                             chain="simple_publication_workflow")
        self.gsm_props = self.portal.portal_properties['googlesitemap_properties']
        self.auth = 'admin:admin'
        self.portal.portal_membership.addMember('admin', 'admin', ('Manager',), [])
        # Add sitemaps
        self.contentSM = _createObjectByType('Sitemap', self.portal, id='google-sitemaps')
        self.contentSM.setPingTransitions(('simple_publication_workflow#publish',))
        self.newsSM = _createObjectByType('Sitemap', self.portal, id='news-sitemaps')
        self.newsSM.setPortalTypes(('News Item','Document'))
        self.newsSM.setPingTransitions(('simple_publication_workflow#publish',))
        self.sitemapUrl = '/'+self.portal.absolute_url(1) + '/google-sitemaps'
        # Add testing document to portal
        my_doc = self.portal.invokeFactory('Document', id='my_doc')
        self.my_doc = self.portal['my_doc']
        my_news = self.portal.invokeFactory('News Item', id='my_news')
        self.my_news = self.portal['my_news']

    def testAutomatePinging(self):
        # 1. Check for pinging both sitemaps
        back_out, myout = sys.stdout, StringIO()
        sys.stdout = myout
        try:
            self.workflow.doActionFor(self.my_doc, 'publish')
            myout.seek(0)
            data = myout.read()
        finally:
            sys.stdout = back_out

        self.assert_('Pinged %s sitemap to Google' % self.contentSM.absolute_url() in data,
                     "Not pinged %s: '%s'" % (self.contentSM.id, data))
        self.assert_('Pinged %s sitemap to Google' % self.newsSM.absolute_url() in data,
                     "Not pinged %s: '%s'" % (self.newsSM.id, data))

        # 2. Check for pinging only news-sitemap sitemaps
        back_out, myout = sys.stdout, StringIO()
        sys.stdout = myout
        try:
            self.workflow.doActionFor(self.my_news, 'publish')
            myout.seek(0)
            data = myout.read()
        finally:
            sys.stdout = back_out

        self.assert_('Pinged %s sitemap to Google' % self.newsSM.absolute_url() in data,
                     "Not pinged %s: '%s'" % (self.newsSM.id, data))
        self.assert_(not 'Pinged %s sitemap to Google' % self.contentSM.absolute_url() in data,
                     "Pinged %s on news: '%s'" % (self.contentSM.id, data))

    def testPingingWithSetupForm(self):
        # Ping news and content sitemaps
        formUrl = '/'+self.portal.absolute_url(1) + '/prefs_gsm_settings'
        qs = 'smselected:list=%s&smselected:list=%s&form.button.Ping=1&form.submitted=1' % \
             (self.contentSM.id, self.newsSM.id)

        back_out, myout = sys.stdout, StringIO()
        sys.stdout = myout
        try:
            response = self.publish("%s?%s" % (formUrl, qs), basic=self.auth)
            myout.seek(0)
            data = myout.read()
        finally:
            sys.stdout = back_out

        self.assert_('Pinged %s sitemap to Google' % self.contentSM.absolute_url() in data,
                     "Not pinged %s: '%s'" % (self.contentSM.id, data))
        self.assert_('Pinged %s sitemap to Google' % self.newsSM.absolute_url() in data,
                     "Not pinged %s: '%s'" % (self.newsSM.id, data))



def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestGoogleSitemapsInstallation))
    suite.addTest(makeSuite(TestSitemapType))
    suite.addTest(makeSuite(TestGoogleSitemaps))
    suite.addTest(makeSuite(TestSettings))
    suite.addTest(makeSuite(TestPinging))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
#    framework()
