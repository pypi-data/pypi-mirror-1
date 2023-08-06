import unittest

from base import PaymentProcessorTestCase

from Products.Five import zcml
from zope.configuration.exceptions import ConfigurationError

from getpaid.paymentprocessors.registry import paymentProcessorRegistry
configure_zcml = '''
<configure
    xmlns="http://namespaces.zope.org/zope"
    xmlns:five="http://namespaces.zope.org/five"
    xmlns:paymentprocessors="http://namespaces.plonegetpaid.com/paymentprocessors"
    i18n_domain="foo">

    <paymentprocessors:registerProcessor
       name="dummy"
       processor="getpaid.paymentprocessors.tests.dummies.DummyProcessor"
       selection_view="getpaid.paymentprocessors.tests.dummies.DummyButton"
       thank_you_view="getpaid.paymentprocessors.tests.dummies.DummyThankYou"
       />


</configure>'''

bad_processor_zcml = '''
<configure
    xmlns="http://namespaces.zope.org/zope"
    xmlns:five="http://namespaces.zope.org/five"
    xmlns:paymentprocessors="http://namespaces.plonegetpaid.com/paymentprocessors"
    i18n_domain="foo">

    <paymentprocessors:registerProcessor
       name="dummy"
       selection_view="getpaid.paymentprocessors.tests.dummies.DummyButton"
       thank_you_view="getpaid.paymentprocessors.tests.dummies.DummyThankYou"
       />

</configure>'''


class TestZCML(PaymentProcessorTestCase):
    """ Test ZCML directives """


    def test_register(self):
        """ Check that ZCML entry gets added to our processor registry """
        zcml.load_string(configure_zcml)

        # See that our processor got registered
        self.assertEqual(len(papaymentProcessorRegistryistry.items()), 1)

    def test_bad_processor(self):
        """ Check that ZCML entry which has bad processor declaration is caught """

        try:
            zcml.load_string(bad_processor_zcml)
            raise AssertionError("Should not be never reached")
        except ConfigurationError, e:
            pass

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestZCML))
    return suite
