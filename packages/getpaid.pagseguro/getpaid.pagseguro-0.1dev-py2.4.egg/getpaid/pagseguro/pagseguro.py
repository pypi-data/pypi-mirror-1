"""
"""
import urllib



from Products.CMFCore.utils import getToolByName
from zope import component
from zope import interface

from interfaces import IPagseguroStandardOptions, IPagseguroStandardProcessor

from Products.PloneGetPaid.interfaces import IGetPaidManagementOptions
from getpaid.core import interfaces as GetPaidInterfaces

_sites = {
    "real": "pagseguro.uol.com.br",
    "teste":  "pagseguro.uol.com.br"
    }

class PagseguroStandardProcessor( object ):
   
    interface.implements( IPagseguroStandardProcessor )

    options_interface = IPagseguroStandardOptions

    def __init__( self, context ):
        self.context = context

    def cart_post_button( self, order ):
        options = IPagseguroStandardOptions( self.context )
        siteroot = getToolByName(self.context, "portal_url").getPortalObject()
        manage_options = IGetPaidManagementOptions( siteroot )        
        cartitems = []
        idx = 1
        _button_form = """<form target="pagseguro" method="post"
action="https://pagseguro.uol.com.br/security/webpagamentos/webpagto.aspx">
<input type="hidden" name="email_cobranca" value="%(merchant_id)s">
<input type="hidden" name="encoding" value="utf-8">
<input type="hidden" name="tipo" value="CP">
<input type="hidden" name="moeda" value="BRL">
<input type="hidden" name="ref_transacao" value="%(order_id)s"/>
%(cart)s

<input type="image" 
src="https://pagseguro.uol.com.br/Security/Imagens/btnfinalizaBR.jpg" 
name="submit" alt="Pague com PagSeguro - e rapido, gratis e seguro!">
</form>

"""
        _button_cart = """<input type="hidden" name="item_descr_%(idx)s" value="%(item_name)s" />
<input type="hidden" name="item_id_%(idx)s" value="%(item_number)s" />
<input type="hidden" name="item_quant_%(idx)s" value="%(quantity)s" />
<input type="hidden" name="item_valor_%(idx)s" value="%(amount)s" />
<input type="hidden" name="item_peso_%(idx)s" value="%(weight)s" />

"""
        
        for item in order.shopping_cart.values():
            weight = getattr(item, 'weight', 0)	    
            v = _button_cart % {"idx": idx,
                                "item_name": item.name,
                                "item_number" : item.product_code,
                                "quantity": item.quantity,
                                 "amount": int(item.cost*100),
                                 "weight": int(weight*1000),
                                 }
            cartitems.append(v)
            idx += 1
        siteURL = siteroot.absolute_url()
        # having to do some magic with the URL passed to Paypal so their system replaies properly
        # returnURL = "%s/@@getpaid-thank-you" % siteURL
        # IPNURL = "%s/%s" % (siteURL, urllib.quote_plus("@@getpaid-pagseguro-ipnreactor"))
        formvals = {
           # "site": _sites[options.server_url],
            "merchant_id": options.merchant_id,
            "cart": ''.join(cartitems),
            "order_id" : order.order_id,
            "store_name": manage_options.store_name,
            }
        return _button_form % formvals
    
    def capture(self, order, price):
        # always returns async - just here to make the processor happy
        return GetPaidInterfaces.keys.results_async

    def authorize( self, order, payment ):
        pass
