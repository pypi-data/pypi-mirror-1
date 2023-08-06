import urllib, urllib2
import socket
import logging
import re
import pdb

from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from zope.component import getUtility

from getpaid.core.interfaces import IOrderManager

from getpaid.pagseguro.interfaces import IPagseguroStandardOptions
from getpaid.pagseguro.pagseguro import _sites

from notification import Notification

logger = logging.getLogger("Plone")

class IPNListener(BrowserView):
    """Listener for Pagseguro IPN notifications - registered as a page view
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.portal = getToolByName(self.context, 'portal_url').getPortalObject()
        
   
    def process(self):
        this_notification = Notification(self.request)
        is_valid_IPN = self.verify()
        order_manager = getUtility(IOrderManager)
        if this_notification.Referencia in order_manager:
            if not(is_valid_IPN):
		logger.info('getpaid.pagseguro: POST não vem do pagseguro')
                return		
            order = order_manager.get(this_notification.Referencia)
            if not self.compare_cart(this_notification, order):
                logger.info('getpaid.pgseguro: received IPN that does match order number %s' % this_notification.Referencia)
                # bad IPN - do not apply to transaction
                return
            if this_notification.StatusTransacao == 'Completo':
                self.fill_in_order_data(this_notification, order)
                order.finance_workflow.fireTransition('charge-charging')
                logger.info('getpaid.pagseguro: received successful IPN payment notification for order %s' % this_notification.Referencia)
                return
            if this_notification.StatusTransacao == 'Cancelado':
                order.finance_workflow.fireTransition('decline-charging')
                logger.info('getpaid.pagseguro: received unsuccessful IPN payment notification for order %s  - txn_type "%s"' % this_notification.Referencia,this_notification.TipoPagamento)
                return
            # IPN not of interest to us right now
            logger.info('getpaid.pagseguro: received IPN for order %s that is not of interest - txn_type "%s", payment_status "%s"' % (this_notification.Referencia, this_notification.TipoPagamento, this_notification.StatusTransacao))
            return
        # invoice not in cart
        #logger.info('getpaid.pagseguro: received IPN that does not apply to any order number - invoice "%s"' % (this_notification.Referencia))
        siteroot = getToolByName(self.context, "portal_url").getPortalObject()
        siteURL = siteroot.absolute_url()
        return self.request.RESPONSE.redirect("%s/@@getpaid-thank-you" % siteURL)
       
    def compare_cart(self, notification, order):
        for ref in order.shopping_cart.keys():
            cart_item = order.shopping_cart[ref]
            if notification.shopping_cart.has_key(cart_item.product_code):
                notification_item = notification.shopping_cart[cart_item.product_code]
                if int(cart_item.quantity) != int(notification_item.ProdQuantidade_):
                    return False
            else:
                # item not in returned cart - invalid IPN response
                return False
        # everything checks out
        return True
    
    


    def verify(self):
        options = IPagseguroStandardOptions( self.portal)
        # get ready to POST back form variables
       
        form = self.request.form
        params =[(key, form[key]) for key in form.keys() if key != 'cmd']
        params = [('Comando', 'validar')] + params
        params = [('Token', options.merchant_token)] + params
        paramData = urllib.urlencode(params)
        url = "https://%s/Security/NPI/Default.aspx" % _sites[options.server_url]
        req = urllib2.Request(url, paramData)
        f = urllib2.urlopen(req)
        pagseg_ret = f.read()
        f.close()        
        
        if pagseg_ret.lower() == 'verificado':
            return True
        else:
            pass


    def fill_in_order_data(self, notification, order):

        if notification.CliNome is not None:
            order.contact_information.name = notification.CliNome
       
        if notification.CliEmail is not None:
            order.contact_information.email = notification.CliEmail
       
        if notification.CliTelefone is not None:
            order.contact_information.phone_number = re.sub('[^\d]+', '', notification.CliTelefone)
        
        
        if notification.CliEndereco is not None:
            endereco = notification.CliEndereco 
            if notification.CliNumero is not None:
                endereco = endereco + ' , ' + notification.CliNumero
            if notification.CliComplemento is not None:
                endereco = endereco + ' ' + notification.CliComplemento
            order.billing_address.bill_first_line = endereco
       
        if notification.CliCidade is not None:
            order.billing_address.bill_city = notification.CliCidade
       
        if notification.CliEstado is not None:
            order.billing_address.bill_state = notification.CliEstado

        if notification.CliCEP is not None:
            order.billing_address.bill_postal_code = notification.CliCEP

        order.billing_address.bill_country = "Brasil"

        # mark address as same - Pagseguro does not provide seperate shipping address
        order.shipping_address.ship_same_billing = True
        
    
