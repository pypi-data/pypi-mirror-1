""" Payment processor configuration ZCML directives

"""

__author__ = "Mikko Ohtamaa <mikko.ohtamaa@twinapex.com> http://www.twinapex.com"
__docformat__ = "epytext"
__license__ = "GPL"
__copyright__ = "2009 Twinapex Research"


import os
from inspect import ismethod

from zope import component
from zope.interface import Interface
from zope.component.zcml import handler
from zope.component.interface import provideInterface
from zope.configuration.exceptions import ConfigurationError
from zope.publisher.interfaces.browser import IBrowserRequest, \
     IDefaultBrowserLayer

from zope.app.publisher.browser.viewmeta import pages as zope_app_pages
from zope.app.publisher.browser.viewmeta import view as zope_app_view
from zope.app.publisher.browser.viewmeta import providesCallable, \
     _handle_menu, _handle_for

from Globals import InitializeClass as initializeClass

from zope.configuration.fields import GlobalObject, GlobalInterface
from zope.configuration.fields import MessageID
from zope.configuration.fields import Path
from zope.configuration.fields import PythonIdentifier
from zope.interface import Interface

import getpaid.core

from registry import paymentProcessorRegistry, Entry

class IRegisterPaymentProcessorDirective(Interface):
    """ Register payment processor with the global registry.
    """

    name = PythonIdentifier(
        title=u'Name',
        description=u"Unique identifier for the payment processor. The same name as getpaid.core.interfaces.IPaymentProcessor adapter name has.",
        required=True)
    
    i18n_name = MessageID(
        title=u'International name',
        description=u"User visible name of the payment processor (can be localized)",
        required=True)

    selection_view = PythonIdentifier(
        title=u'Selection view',
        description=u"browser:page name which is used to render the payment processor checkout button",
        required=True)

    review_pay_view = PythonIdentifier(
        title=u'Payment view',
        description=u"browser:page which is used to render the page which redirects to payment processor or renders the payment form",
        required=True)

    settings_view = PythonIdentifier(
        title=u'Settings view',
        description=u"browser:page name which is used to render the payment processor admin screen",
        default=None,
        required=False)

    thank_you_view = PythonIdentifier(
        title=u'Thank you view',
        description=u"browser:page name which is used to render the thank you page when the payment is complete",
        required=False)

def registerProcessor(_context, name=None, i18n_name=None, selection_view=None, review_pay_view=None, settings_view=None, thank_you_view=None):
    """
    Configure a payment processor.
    """
    entry = Entry(name=name, 
                  i18n_name=i18n_name,
                  selection_view=selection_view, 
                  thank_you_view=thank_you_view, 
                  settings_view=settings_view, 
                  review_pay_view=review_pay_view)

    paymentProcessorRegistry.register(entry)

