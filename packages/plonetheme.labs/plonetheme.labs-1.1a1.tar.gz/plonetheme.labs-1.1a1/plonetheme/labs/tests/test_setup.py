"""Unit tests for the installation and uninstallation"""

import os, sys
import unittest

from zope.interface import directlyProvides

from Products.PloneTestCase import PloneTestCase as ptc
from Products.CMFCore.utils import getToolByName

from plonetheme.labs.browser.interfaces import IThemeSpecific
from plonetheme.labs.tests.base import TestCase

ptc.setupPloneSite(products=['plonetheme.labs'])


class TestInstall(TestCase):
    """Test theme installation"""

    def afterSetUp(self):
        self.skins = getToolByName(self.portal, 'portal_skins')
        self.css = getToolByName(self.portal, 'portal_css')
        self.setup = getToolByName(self.portal, 'portal_setup')

        # Shouldn't this happen automatically?
        directlyProvides(self.portal.REQUEST, IThemeSpecific)

    def test_theme_css_added(self):
        """Test that the main CSS file is registered"""
        resources = self.css.getResources()
        resources = dict(zip([i.getId() for i in resources], resources))
        self.failUnless('main.css' in resources)
        self.failUnless(resources['main.css'].getEnabled())

    def test_skin_selection_added(self):
        """Check that 'Labs Theme' is in portal_skins"""
        self.failUnless('Labs Theme' in self.skins.getSkinSelections())

    def test_default_skin_selection(self):
        """Check that 'Labs Theme' is the default skin"""
        self.assertEqual(self.skins.getDefaultSkin(), 'Labs Theme')

    def test_site_actions_moved_to_footer(self):
        """Check that site actions are in the footer viewlet manager"""
        site_actions_in_footer = self.is_viewlet_in_viewlet_manager(
            'plone.site_actions',
            'plone.portalfooter')
        self.failUnless(site_actions_in_footer)

        site_actions_hidden_in_header = self.is_hidden_viewlet(
            'plone.site_actions',
            'plone.portalheader',
        )
        self.failIf(site_actions_hidden_in_header)

    def test_personal_bar_moved_to_footer(self):
        """Check that site actions are in the footer viewlet manager"""
        personal_bar_in_footer = self.is_viewlet_in_viewlet_manager(
            'plone.personal_bar',
            'plone.portalfooter')
        self.failUnless(personal_bar_in_footer)

        personal_bar_hidden_in_header = self.is_hidden_viewlet(
            'plone.personal_bar',
            'plone.portalheader',
        )
        self.failIf(personal_bar_hidden_in_header)

    def test_footer_viewlets_order(self):
        """Test order of viewlets in the footer viewlet manager"""
        viewlets = self.list_ordered_viewlets('plone.portalfooter')
        target_order = (
            u'plone.personal_bar',
            u'plone.site_actions',
            u'plone.footer',
            u'plone.colophon',
        )
        self.assertEquals(viewlets, target_order)

class TestUninstall(TestCase):
    """Test theme uninstalation"""

    def afterSetUp(self):
        self.skins = getToolByName(self.portal, 'portal_skins')
        self.css = getToolByName(self.portal, 'portal_css')
        self.setup = getToolByName(self.portal, 'portal_setup')

        uninstall_profile = 'profile-plonetheme.labs:uninstall'
        self.setup.runAllImportStepsFromProfile(uninstall_profile)

    def test_theme_css_removed(self):
        """Test that the main CSS file is not registered"""
        resources = self.css.getResources()
        resources = dict(zip([i.getId() for i in resources], resources))
        self.failIf('main.css' in resources)

    def test_skin_selection_removed(self):
        """Check that 'Labs Theme' is not in portal_skins"""
        self.failIf('Labs Theme' in self.skins.getSkinSelections())

    def test_default_skin_selection(self):
        """Check that 'Labs Theme' is not the default skin"""
        self.failIf(self.skins.getDefaultSkin() == 'Labs Theme')

    def test_site_actions_moved_to_header(self):
        """Check that site actions are in the header viewlet manager"""
        site_actions_in_footer = self.is_viewlet_in_viewlet_manager(
            'plone.site_actions',
            'plone.portalfooter')
        self.failIf(site_actions_in_footer)

        site_actions_in_header = self.is_viewlet_in_viewlet_manager(
            'plone.site_actions',
            'plone.portalheader')
        self.failUnless(site_actions_in_header)

    def test_personal_bar_moved_to_header(self):
        """Check that the personal bar are in the header viewlet
        manager
        """
        personal_bar_in_footer = self.is_viewlet_in_viewlet_manager(
            'plone.site_actions',
            'plone.portalfooter')
        self.failIf(personal_bar_in_footer)

        personal_bar_in_header = self.is_viewlet_in_viewlet_manager(
            'plone.site_actions',
            'plone.portalheader')
        self.failUnless(personal_bar_in_header)


    def test_footer_viewlets_order(self):
        """Test order of viewlets in the footer viewlet manager"""
        viewlets = self.list_ordered_viewlets('plone.portalfooter')
        target_order = (
            u'plone.footer',
            u'plone.colophon',
        )
        self.assertEquals(viewlets, target_order)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestInstall))
    suite.addTest(unittest.makeSuite(TestUninstall))
    return suite

