"""
"""

from getpaid.core import interfaces
from zope import schema
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from zope.i18nmessageid import MessageFactory
_ = MessageFactory('getpaid.pagseguro')

# generate a Zope 3 vocabulary from a sequence of tuples, suitable for use in a drop-down menu
def _vocabulary(*terms):
    return SimpleVocabulary([SimpleTerm(token, token, title)
                             for token, title in terms])


class IPagseguroStandardProcessor( interfaces.IPaymentProcessor ):
    """
    Pagseguro Processor
    """

class IPagseguroStandardOptions( interfaces.IPaymentProcessorOptions ):
    """
    Pagseguro Standard Options
    """
    server_url = schema.Choice(
        title = _(u"Pagseguro Processador de Pagamentos"),
        values = ( "real", "teste"),
        )

    merchant_id = schema.ASCIILine( title = _(u"ID Pagseguro"))
    merchant_token = schema.ASCIILine( title = _(u"Token Pagseguro"))

   
