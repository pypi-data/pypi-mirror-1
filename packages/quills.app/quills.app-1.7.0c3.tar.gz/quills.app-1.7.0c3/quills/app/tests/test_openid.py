import unittest
from Testing import ZopeTestCase
from Products.PloneTestCase import PloneTestCase
from Products.PloneTestCase.layer import PloneSite

import plone.openid
from plone.openid.plugins.oid import OpenIdPlugin
from plone.openid.tests.consumer import PatchPlugin
from OFS.Application import install_package


PloneTestCase.setupPloneSite()

from Products.Five.testbrowser import Browser


class TestOpenId(PloneTestCase.FunctionalTestCase):

    def afterSetUp(self):
        # Since Zope 2.10.4 we need to install our package manually
        install_package(self.app, plone.openid, plone.openid.initialize)
        self.addProduct("plone.app.openid")
        PatchPlugin(OpenIdPlugin)

    def test_login(self):
        browser = Browser()
        browser.open("http://nohost/plone")
        login = browser.getControl(label="OpenID URL")
        login.value = "http://anyhost/none"
        browser.getControl(name="openid_submit").click()
        print browser.contents


      
def test_suite():
    suite = unittest.TestSuite( unittest.makeSuite(TestOpenId))
    suite.layer = PloneSite
    return suite
