"""

    Payment processor registry.

    Register user interface related payment processor settings.

"""

__author__ = "Mikko Ohtamaa <mikko.ohtamaa@twinapex.com> http://www.twinapex.com"
__docformat__ = "epytext"
__license__ = "GPL"
__copyright__ = "2009 Twinapex Research"


from zope.component import queryMultiAdapter

class BadViewConfigurationException(Exception):
    """ Thrown when defined view look up fails """

class Entry:
    """ Hold information about payment processor user interface registrations.

    Instance variables correspond ones defined in IRegisterPaymentProcessorDirective.
    """
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def _getViewByName(self, context, request, name):
         view = queryMultiAdapter((context, request), name=name)
         if view == None:
             # Do graceful error handling
             raise BadViewConfigurationException("No browser:page implemented for payment processor %s view %s" % (self.name, name))

         view = view.__of__(context) # Link acquisition chain
         return view

    def getButtonView(self, context, request):
        """ Get payment method selection button renderer.

        @param context: Any site object
        @param request: HTTPRequest
        @return: BrowserView instance
        """
        view = self._getViewByName(context, request, self.selection_view)
        return view

    def getThankYouView(self, context, request):
        """ Get payment complete page renderer.

        @param context: Any site object
        @param request: HTTPRequest
        @return: BrowserView instance
        """
        view = self._getViewByName(context, request, self.thank_you_view)
        return view

    def getSettingsView(self, context, request):
        """ Get settings page view class name for the admin screen.

        @param context: Any site object
        @param request: HTTPRequest
        @return: BrowserView instance
        """
        view = self._getViewByName(context, request, self.settings_view)
        return view

class PaymentProcessorRegistry:
    """ Payment processor configuration data holder.

    For possible parameters, see directives.IRegisterPaymentProcessorDirective
    """

    def __init__(self):
        self.clear()
        
    def register(self, processor):
        """ Put a new payment processor to the global registry """
        self.registry[processor.name] = processor

    def clear(self):
        """ Delete all registry entries """
        self.registry = {}

    def getProcessors(self):
        """ Return list of Entry objects. """
        return self.registry.values()

    def getNames(self):
        """ Return list of payment processor names """
        return self.registry.keys()

    def get(self, name):
        """ Return payment processor registry entry by its name. 
        
        @param name: Payment processor adapter name
        @raise: KeyError if the payment processor with name does not exist
        """
        return self.registry[name]

paymentProcessorRegistry = PaymentProcessorRegistry()


