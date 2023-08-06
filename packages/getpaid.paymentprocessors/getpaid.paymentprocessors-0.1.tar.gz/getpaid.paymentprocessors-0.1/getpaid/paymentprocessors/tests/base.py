"""

    Setup unit test suite for getpaid.paymentprocessors package.

"""
import sys, os

__author__ = "Mikko Ohtamaa <mikko.ohtamaa@twinapex.com> http://www.twinapex.com"
__docformat__ = "epytext"
__license__ = "GPL"
__copyright__ = "2009 Twinapex Research"

from Testing import ZopeTestCase as ztc
from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase.layer import onsetup
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneGetPaid.tests.base import PloneGetPaidTestCase

from getpaid.paymentprocessors.registry import paymentProcessorRegistry@onsetup
def setup_package():
    fiveconfigure.debug_mode = True
    import getpaid.paymentprocessors
    zcml.load_config('configure.zcml', getpaid.paymentprocessors)
    fiveconfigure.debug_mode = False

    ztc.installPackage('getpaid.paymentprocessors')

setup_package()
ptc.setupPloneSite(products=['Products.GetPaid', 'getpaid.paymentprocessors'])

class PaymentProcessorTestCase(PloneGetPaidTestCase):
    """ Base class for getpaid.paymentprocessors unit tests """

    def afterSetUp( self ):
        """ Since ZCML loads happen process life cycle, we need to unload ZCML on every step """
        PloneGetPaidTestCase.afterSetUp(self)
        papaymentProcessorRegistryar()


    def loadDummyZCML(self, string):
        """ Load ZCML as a string and set the folder so that template references are related correctly. """
        module = sys.modules[__name__]
        dir = os.path.dirname(module.__file__)
        os.chdir(dir)
        zcml.load_string(string)

