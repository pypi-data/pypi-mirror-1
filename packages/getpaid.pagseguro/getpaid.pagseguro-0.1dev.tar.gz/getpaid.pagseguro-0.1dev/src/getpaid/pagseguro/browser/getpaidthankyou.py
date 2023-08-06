from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

class GetpaidPagseguroThankyouView(BrowserView):
    """Class for overriding getpaid-thank-you view for pagseguro purchases
    """
    
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def getInvoice(self):
        if self.request.has_key('Referencia'):
            return self.request['Referencia']
        else:
            return None

    def getURL(self):
        portalurl = getToolByName(self.context, "portal_url").getPortalObject().absolute_url()
        if self.getInvoice() is not None:
            return "%s/@@getpaid-order/%s" % ( portalurl, self.getInvoice())
        else:
            return ''
