
"""

    Zope vocabularies used by payment processors.


    E.g. used in the checkout schema.

"""

__author__ = "Mikko Ohtamaa <mikko.ohtamaa@twinapex.com> http://www.twinapex.com"
__docformat__ = "epytext"
__license__ = "GPL"
__copyright__ = "2009 Twinapex Research"

from zope import component
from zope.interface import implements
from zope.schema import vocabulary
import interfaces

from registry import paymentProcessorRegistry

def PaymentProcessors(context):
    """ List all registered payment processors.

    Mostly useful for validating form input.

    Vocabulary contains all payment processors, not just active ones.
    
    @return: zope.vocabulary.SimpleVocabulary
    """
    processors = paymentProcessorRegistry.getProcessors() 
    # TODO: Localize here
    terms = [ vocabulary.SimpleTerm(token=p.name, value=p.i18n_name) for p in processors ] 
    return vocabulary.SimpleVocabulary(terms)


