from zope import interface

from getpaid.core import options

from interfaces import IPaymentMethodInformation

class PaymentMethodInformation(options.PersistentBag):
    """ Store checkout information about chosen payment method.

    This is a persistent storage which checkout wizard step
    accesses through getSchemaAdapters().

    Later this will be stored in order.payment_method when the order is saved.

    This is referred by Products.PloneGetPaid.preferences
    """

    interface.implements(IPaymentMethodInformation)

    title = "Payment Method Information"

    # TODO: No idea what lines below do or why they are needed
    # blindly copied Products.PlonmeGetPaid.member -mikko
    __parent__ = None
    __name__ = None


# Boostrap the PersistentBag to contain fields from the schema
PaymentMethodInformation.initclass(IPaymentMethodInformation)
