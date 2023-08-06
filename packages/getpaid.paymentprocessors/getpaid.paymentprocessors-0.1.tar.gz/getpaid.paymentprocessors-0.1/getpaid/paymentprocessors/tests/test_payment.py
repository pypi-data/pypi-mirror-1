import unittest

import dummies
from base import PaymentProcessorTestCase

from Products.Five import zcml
from zope.configuration.exceptions import ConfigurationError

from getpaid.paymentprocessors.registry import BadViewConfigurationException, paymentProcessorUIRegistry

class TestPayment(PaymentProcessorTestCase):
    """ Test that payment is completed using the chosen processor"""

    def test_payment(self):

        self.loadDummyZCML(dummies.configure_zcml)

        # Go to checkout screen
        view = self.portal.restrictedTraverse("@@getpaid-checkout-wizard")
        processors = view.getProcessors()
        self.assertEqual(len(processors), 1)

        # Choose processor
        # Do fake POST
        request = self.portal.REQUEST
        request["REQUEST_METHOD"] = "POST"
        request["nullpayment"] = "" # Simulate <button> press outcome

        view = self.portal.restrictedTraverse("@@getpaid-checkout-wizard")


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPayment))
    return suite
