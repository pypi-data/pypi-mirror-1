import Globals
import os.path

from lxml import etree

from unittest import defaultTestLoader
from urllib2 import HTTPError

from Products.Five import zcml
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

from Products.Five.testbrowser import Browser
from Products.CMFCore.Expression import Expression, getExprContext

from plone.registry.interfaces import IRegistry
from zope.component import getUtility

from collective.xdv.interfaces import ITransformSettings
from collective.xdv.transform import CACHE
from collective.xdv.utils import compile_theme

@onsetup
def setup_product():
    import collective.xdv
    zcml.load_config('configure.zcml', collective.xdv)

setup_product()
ptc.setupPloneSite(products=['collective.xdv'])

class TestCase(ptc.FunctionalTestCase):
    
    def afterSetUp(self):
        # Enable debug mode always to ensure cache is disabled by default
        Globals.DevelopmentMode = True
        
        self.settings = getUtility(IRegistry).forInterface(ITransformSettings)
        
        self.settings.enabled = False
        self.settings.domains = set([u'nohost:80', u'nohost'])
        self.settings.theme = unicode(os.path.join(os.path.split(__file__)[0], 'theme.html'))
        self.settings.rules = unicode(os.path.join(os.path.split(__file__)[0], 'rules.xml'))
        self.settings.notheme = set([u'^.*/emptypage$', 
                                     u'^.*/manage$', 
                                     u'^.*/manage_(?!translations_form)[^/]+$', 
                                     u'^.*/image_view_fullscreen$',
                                     u'^.*/referencebrowser_popup(\?.*)?$',
                                     u'^.*/error_log(/.*)?$',
                                     u'^.*/aq_parent(/.*)?$'])
        theme_other = unicode(os.path.join(os.path.split(__file__)[0], 'othertheme.html'))
        self.settings.alternate_themes = [u"^.*/news.*$|%s|%s" % (theme_other, self.settings.rules),]
        
    def evaluate(self, context, expression):
        ec = getExprContext(context, context)
        expr = Expression(expression)
        return expr(ec)
    
    def test_no_effect_if_not_enabled(self):
        browser = Browser()
        browser.open(self.portal.absolute_url())
        
        # Title - pulled in with rules.xml
        self.failUnless("Welcome to Plone" in browser.contents)
        
        # Elsewhere - not pulled in
        self.failUnless("Accessibility" in browser.contents)
        
        # The theme
        self.failIf("This is the theme" in browser.contents)
    
    def test_theme_enabled(self):
        self.settings.enabled = True
        browser = Browser()
        browser.open(self.portal.absolute_url())
        
        # Title - pulled in with rules.xml
        self.failUnless("Welcome to Plone" in browser.contents)
        
        # Elsewhere - not pulled in
        self.failIf("Accessibility" in browser.contents)
        
        # The theme
        self.failUnless("This is the theme" in browser.contents)
        
    def test_theme_installed_invalid_config(self):
        self.settings.enabled = True
        self.settings.theme = u"invalid"
        
        browser = Browser()
        browser.open(self.portal.absolute_url())
        
        # Title - pulled in with rules.xml
        self.failUnless("Welcome to Plone" in browser.contents)
        
        # Elsewhere - not pulled in
        self.failUnless("Accessibility" in browser.contents)
        
        # The theme
        self.failIf("This is the theme" in browser.contents)
        
    def test_notheme_path(self):
        self.settings.enabled = True
        self.settings.notheme = set([u'^.*/emptypage$', 
                                     u'^.*/manage$', 
                                     u'^.*/manage_(?!translations_form)[^/]+$', 
                                     u'^.*/image_view_fullscreen$',
                                     u'^.*/referencebrowser_popup(\?.*)?$',
                                     u'^.*/error_log(/.*)?$',
                                     u'^.*/aq_parent(/.*)?$'])
        
        browser = Browser()
        browser.open(self.portal.absolute_url() + '/emptypage')
        
        self.failUnless("Kupu" in browser.contents)
        self.failIf("This is the theme" in browser.contents)

    def test_non_html_content(self):
        
        self.settings.enabled = True
        self.settings.theme = u"invalid"
        
        browser = Browser()
        browser.open(self.portal.absolute_url() + '/document_icon.gif')
        # The theme
        self.failIf("This is the theme" in browser.contents)

    def test_outside_domain(self):
        
        self.settings.enabled = True
        self.settings.domains = set([u"www.example.org", u"www.example.org:80"])
        
        browser = Browser()
        browser.open(self.portal.absolute_url())
        
        # Title - pulled in with rules.xml
        self.failUnless("Welcome to Plone" in browser.contents)
        
        # Elsewhere - not pulled in
        self.failUnless("Accessibility" in browser.contents)
        
        # The theme
        self.failIf("This is the theme" in browser.contents)
        
    def test_non_debug_mode_cache(self):
        Globals.DevelopmentMode = False
        self.settings.enabled = True
        
        # Sneakily seed the cache with dodgy data
        
        theme = unicode(os.path.join(os.path.split(__file__)[0], 'othertheme.html'))
        rules = unicode(os.path.join(os.path.split(__file__)[0], 'rules.xml'))
        theme_id = u"default"
        compiled_theme = compile_theme(theme, rules)
        xslt_tree = etree.fromstring(compiled_theme)
        transform = etree.XSLT(xslt_tree)
            
        CACHE.update_transform(theme_id, transform)
        
        browser = Browser()
        browser.open(self.portal.absolute_url())
        
        # Title - pulled in with rules.xml
        self.failUnless("Welcome to Plone" in browser.contents)
        
        # Elsewhere - not pulled in
        self.failIf("Accessibility" in browser.contents)
        
        # The theme
        self.failUnless("This is the other theme" in browser.contents)
        
        # Now invalide the cache by touching the settings utility
        
        self.settings.enabled = False
        self.settings.enabled = True
        
        browser.open(self.portal.absolute_url())
        
        # Title - pulled in with rules.xml
        self.failUnless("Welcome to Plone" in browser.contents)
        
        # Elsewhere - not pulled in
        self.failIf("Accessibility" in browser.contents)
        
        # The theme
        self.failUnless("This is the theme" in browser.contents)
    
    def test_enabled_check(self):
        self.settings.enabled = False
        self.settings.domains = set([u'nohost', u'nohost:80'])
        
        value = self.portal.restrictedTraverse('@@xdv-check/enabled')()
        self.failIf(value)
        
        self.settings.enabled = True
        
        value = self.portal.restrictedTraverse('@@xdv-check/enabled')()
        self.failUnless(value)
        
        self.settings.domains = set([u'www.example.com', u'www.example.com:80'])
        value = self.portal.restrictedTraverse('@@xdv-check/enabled')()
        self.failIf(value)
        
        
    def test_enabled_domain_check(self):
        self.settings.enabled = False
        self.settings.domains = set([u'nohost', u'nohost:80'])
        
        value = self.portal.restrictedTraverse('@@xdv-check/domain_enabled')()
        self.failUnless(value)
        
        self.settings.enabled = True
        value = self.portal.restrictedTraverse('@@xdv-check/domain_enabled')()
        self.failUnless(value)
        
        self.settings.domains = set([u'www.example.com', u'www.example.com:80'])
        value = self.portal.restrictedTraverse('@@xdv-check/domain_enabled')()
        self.failIf(value)
    
    def test_theme_different_path(self):
        self.settings.enabled = True
        browser = Browser()
        browser.open(self.portal.absolute_url())
        
        # Title - pulled in with rules.xml
        self.failUnless("Welcome to Plone" in browser.contents)
        
        # Elsewhere - not pulled in
        self.failIf("Accessibility" in browser.contents)
        
        # The theme
        self.failUnless("This is the theme" in browser.contents)
        
        browser.open(self.portal.news.absolute_url())
        
        # Title - pulled in with rules.xml
        self.failUnless("News" in browser.contents)
        
        # Elsewhere - not pulled in
        self.failIf("Accessibility" in browser.contents)
        
        # The theme
        self.failUnless("This is the other theme" in browser.contents)
    
    def test_theme_for_404(self):
        self.settings.enabled = True
        browser = Browser()
        try:
            browser.open('%s/404_page' % self.portal.absolute_url())
        except HTTPError, error:
            pass
        self.assertEquals(error.code, 404)
        
        # The theme
        self.failUnless("This is the theme" in browser.contents)
    
def test_suite():
    return defaultTestLoader.loadTestsFromName(__name__)
