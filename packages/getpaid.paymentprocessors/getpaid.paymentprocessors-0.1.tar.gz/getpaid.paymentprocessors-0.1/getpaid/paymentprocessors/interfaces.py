from zope.interface import Interface
from zope import schema

from zope.i18nmessageid import MessageFactory
_ = MessageFactory('getpaid.paymentprocessors')

__author__ = "Mikko Ohtamaa <mikko.ohtamaa@twinapex.com> http://www.twinapex.com"
__docformat__ = "epytext"
__license__ = "GPL"
__copyright__ = "2009 Twinapex Research"


class IPaymentMethodInformation(Interface):
    """ Store information which payment method user selects on the checkout wizard.


    """

    payment_processor = schema.Choice( title = _(u"Payment method"),
                                    source = u"getpaid.paymentprocessors.payment_processors",)


