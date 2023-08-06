import unittest

import dummies
from base import PaymentProcessorTestCase

from Products.Five import zcml
from zope.configuration.exceptions import ConfigurationError

from getpaid.paymentprocessors.registry import BadViewConfigurationException, paymentProcessorUIRegistry

class TestViews(PaymentProcessorTestCase):
    """ Test ZCML directives """

    def render_admin(self):
        """ Test rendering admin interface views with the current paymentprocessor configuration. """

        # Render the page where you can choose which payment processor settings are managed

        self.loginAsPortalOwner()
        view = self.portal.restrictedTraverse("@@manage-getpaid-payment-processor")
        view()
        self.logout()

    def test_selection_screen_no_processor(self):
        """ Test different count of site payment processors """

        view = self.portal.restrictedTraverse("@@getpaid-checkout-wizard")
        processors = view.getProcessors()
        self.assertEqual(len(processors), 0)

        # Render payment method selection HTML
        view()

        # Test rendering related admin interface pages and hope to catch all raised exceptions
        self.render_admin()

    def test_selection_screen_one_processor(self):
        """ Test different count of site payment processors """
        self.loadDummyZCML(dummies.configure_zcml)

        view = self.portal.restrictedTraverse("@@getpaid-checkout-wizard")
        processors = view.getProcessors()
        self.assertEqual(len(processors), 1)

        # Render payment method selection HTML
        view()

        # Test rendering related admin interface pages and hope to catch all raised exceptions
        self.render_admin()


    def test_selection_screen_n_processors(self):
        """ Test different count of site payment processors """
        self.loadDummyZCML(dummies.configure_zcml)
        self.loadDummyZCML(dummies.configure_zcml_2)

        view = self.portal.restrictedTraverse("@@getpaid-checkout-wizard")
        processors = view.getProcessors()
        self.assertEqual(len(processors), 2)

        # Render payment method selection HTML
        view()

        # Test rendering related admin interface pages and hope to catch all raised exceptions
        self.render_admin()

    def test_bad_view_definition(self):
        """ Try render non-existing browser:page """
        bad_button_configure_zcml = '''
        <configure
            xmlns="http://namespaces.zope.org/zope"
            xmlns:five="http://namespaces.zope.org/five"
            xmlns:paymentprocessors="http://namespaces.plonegetpaid.com/paymentprocessors"
            xmlns:browser="http://namespaces.zope.org/browser"
            i18n_domain="foo">

            <paymentprocessors:registerProcessor
               name="dummy"
               processor="getpaid.paymentprocessors.tests.dummies.DummyProcessor"
               selection_view="BAD_ENTRY_HERE"
               thank_you_view="dummy_payment_processor_thank_you_page"
               />

        </configure>'''
        zcml.load_string(bad_button_configure_zcml)
        view = self.portal.restrictedTraverse("@@getpaid-checkout-wizard")
        try:
            view()
            raise AssertionError("Should not be never reached")
        except BadViewConfigurationException:
            pass

    def test_choose_available_payment_processors(self):
        """ Test page where you can enabled different payment processors on the site """
        self.loadDummyZCML(dummies.configure_zcml)
        self.loginAsPortalOwner()

        # Do fake POST
        request = self.portal.REQUEST
        request["REQUEST_METHOD"] = "POST"
        request["active-payment-processors"] =["dummy"]

        view = self.portal.restrictedTraverse("@@manage-getpaid-payment-processor")
        view()
        self.assertEqual(self.portal.portal_properties.payment_processor_properties.enabled_processors, ["dummy"])

    def test_settings_view(self):
        """ Render settings view for an payment processor. """
        self.loadDummyZCML(dummies.configure_zcml)
        self.loginAsPortalOwner()
        self.portal.restrictedTraverse("@@dummy_payment_processor_settings")

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestViews))
    return suite
