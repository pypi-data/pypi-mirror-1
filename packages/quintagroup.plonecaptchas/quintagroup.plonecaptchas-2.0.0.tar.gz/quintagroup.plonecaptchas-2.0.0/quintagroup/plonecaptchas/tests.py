import unittest
import os
import sys
import re

from Products.Five import zcml
from Products.Five import fiveconfigure

from Testing import ZopeTestCase as ztc
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

from AccessControl.SecurityManagement import newSecurityManager
from Products.CMFCore.utils import getToolByName

from quintagroup.plonecaptchas.utils import getWord, decrypt, parseKey
from quintagroup.plonecaptchas.config import *

@onsetup
def setup_product():
    fiveconfigure.debug_mode = True
    import quintagroup.plonecaptchas
    zcml.load_config('configure.zcml', quintagroup.plonecaptchas)
    fiveconfigure.debug_mode = False
    ztc.installPackage('quintagroup.plonecaptchas')

setup_product()
ptc.setupPloneSite()

class TestCaptchaWidget(ptc.FunctionalTestCase):

    def afterSetUp(self):
        self.loginAsPortalOwner()
        self.addProduct(PRODUCT_NAME)
        self.portal.invokeFactory('Document', 'index_html')
        self.portal['index_html'].allowDiscussion(True)
        self.absolute_url = self.portal['index_html'].absolute_url_path()

        self.basic_auth = 'portal_manager:secret'
        uf = self.app.acl_users
        uf.userFolderAddUser('portal_manager', 'secret', ['Manager'], [])
        user = uf.getUserById('portal_manager')
        if not hasattr(user, 'aq_base'):
            user = user.__of__(uf)
        newSecurityManager(None, user)
        self.captcha_key = self.portal.captcha_key

    def testImage(self):
        path = '%s/discussion_reply_form' % self.absolute_url
        response = self.publish(path, self.basic_auth, request_method='GET').getBody()
        patt = re.compile('\s+src="%s(/getCaptchaImage/[0-9a-fA-F]+)"' % self.portal.absolute_url())
        match_obj = patt.search(response)
        img_url = match_obj.group(1)
        content_type = self.publish('/plone' + img_url, self.basic_auth).getHeader('content-type')
        self.assert_(content_type.startswith('image'))

    def testSubmitRightCaptcha(self):
        hashkey = self.portal.getCaptcha()
        key = getWord(int(parseKey(decrypt(self.captcha_key, hashkey))['key']))
        parameters = 'form.submitted=1&Creator=test_user&key=%s' % key
        path = '%s/discussion_reply_form?%s' % (self.absolute_url, parameters)
        extra = {'hashkey': hashkey,
                 'subject': 'testing',
                 'body_text': 'Text in Comment',
                 'discussion_reply:method': 'Save'}
        response = self.publish(path, self.basic_auth, extra=extra, request_method='GET').getBody()
        patt = re.compile("Please re\-enter validation code")
        match_obj = patt.match(response)
        self.assert_(not match_obj)

    def testSubmitWrongCaptcha(self):
        hashkey = self.portal.getCaptcha()
        parameters = 'form.submitted=1&Creator=test_user&key=fdfgh'
        path = '%s/discussion_reply_form?%s' % (self.absolute_url, parameters)
        extra = {'hashkey': hashkey,
                 'subject': 'testing',
                 'body_text': 'Text in Comment',
                 'discussion_reply:method': 'Save'}
        response = self.publish(path, self.basic_auth, extra=extra, request_method='GET').getBody()
        patt = re.compile("Please re\-enter validation code")
        match_obj = patt.search(response)
        self.assert_(match_obj)

    def testSubmitRightCaptchaTwice(self):
        hashkey = self.portal.getCaptcha()
        key = getWord(int(parseKey(decrypt(self.captcha_key, hashkey))['key']))
        parameters = 'form.submitted=1&Creator=test_user&key=%s'%key
        path = '%s/discussion_reply_form?%s'%(self.absolute_url, parameters)
        extra = {'hashkey': hashkey,
                 'subject': 'testing',
                 'body_text': 'Text in Comment',
                 'discussion_reply:method': 'Save'}
        self.publish(path, self.basic_auth, extra=extra, request_method='GET')
        response = self.publish(path, self.basic_auth, extra=extra, request_method='GET').getBody()
        patt = re.compile(".*?Comment\+added")
        match_obj = patt.match(response)
        self.assert_(not match_obj)

class TestInstallation(ptc.FunctionalTestCase):

    def afterSetUp(self):
        self.loginAsPortalOwner()
        self.qi = getToolByName(self.portal, 'portal_quickinstaller', None)
        self.cp = getToolByName(self.portal, 'portal_controlpanel', None)
        self.st = getToolByName(self.portal, 'portal_skins', None)
        self.qi.installProduct(PRODUCT_NAME)

    def getLayers(self):
        return LAYERS + [LAYER_STATIC_CAPTCHAS]

    def testPropertysheetInstall(self):
        pp = getToolByName(self.portal, 'portal_properties')
        self.assert_(PROPERTY_SHEET in pp.objectIds(), 'Property sheet isn\'t found')

    def testPropertysheetUninstall(self):
        self.qi.uninstallProducts([PRODUCT_NAME])
        pp = getToolByName(self.portal, 'portal_properties')
        self.assert_(not PROPERTY_SHEET in pp.objectIds(),
            'Property sheet found after uninstallation')

    def testConfigletInstall(self):
        self.assert_(CONFIGLET_ID in [a.getId() for a in self.cp.listActions()], 'Configlet not found')

    def testConfigletUninstall(self):
        self.qi.uninstallProducts([PRODUCT_NAME])
        self.assertNotEqual(self.qi.isProductInstalled(PRODUCT_NAME), True,'%s is already installed' % PRODUCT_NAME)
        self.assert_(not CONFIGLET_ID in [a.getId() for a in self.cp.listActions()], 'Configlet found after uninstallation')

    def testSkinsInstall(self):
        skinstool = self.st
        layers = self.getLayers()
        for skin in skinstool.getSkinSelections():
            path = skinstool.getSkinPath(skin)
            path = map(str.strip, path.split(','))
            for layer in layers:
                self.assert_(layer.split('/')[0] in skinstool.objectIds(), '%s directory view not found in portal_skins after installation' % layer)
                self.assert_(layer in path, '%s layer not found in %s' % (PRODUCT_NAME, skin))

    def testSkinsUninstall(self):
        self.qi.uninstallProducts([PRODUCT_NAME])
        self.assertNotEqual(self.qi.isProductInstalled(PRODUCT_NAME), True,'%s is already installed' % PRODUCT_NAME)
        skinstool = self.st
        layers = self.getLayers()
        for skin in skinstool.getSkinSelections():
            path = skinstool.getSkinPath(skin)
            path = map(str.strip, path.split(','))
            for layer in layers:
                self.assert_(not layer.split('/')[0] in skinstool.objectIds(), '%s directory view found in portal_skins after uninstallation' % layer)
                self.assert_(not layer in path, '%s layer found in %s after uninstallation' % (layer, skin))

    def testToolInstall(self):
        self.assert_(TOOL_ID in self.portal.objectIds())

    def testToolUninstall(self):
        self.qi.uninstallProducts([PRODUCT_NAME])
        self.assertNotEqual(self.qi.isProductInstalled(PRODUCT_NAME), True, 
            '%s is already installed' % PRODUCT_NAME)
        self.assert_(not TOOL_ID in self.portal.objectIds())

    def testCaptchaKey(self):
        ck = getattr(self.portal, CAPTCHA_KEY)
        self.assert_(ck)
        self.assertEqual(len(ck), 8)
        self.qi.uninstallProducts([PRODUCT_NAME])
        self.assert_(not self.portal.hasProperty(CAPTCHA_KEY))

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestCaptchaWidget))
    suite.addTest(unittest.makeSuite(TestInstallation))
    return suite
