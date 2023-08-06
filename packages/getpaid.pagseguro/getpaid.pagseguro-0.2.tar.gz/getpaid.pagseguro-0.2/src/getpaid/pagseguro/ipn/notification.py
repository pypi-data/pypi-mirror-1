from UserDict import DictMixin

main_mapping = { 'VendedorEmail':'VendedorEmail',
                 'TransacaoID':'TransacaoID',
                 'Referencia':'Referencia',
                 'TipoFrete':'TipoFrete',
                 'ValorFrete':'ValorFrete',
                 'Anotacao':'Anotacao',
                 'DataTransacaot':'DataTransacao',
                 'TipoPagamento':'TipoPagamento',
                 'StatusTransacao':'StatusTransacao',
                 'CliNome':'CliNome',
                 'CliEmail':'CliEmail',
                 'CliEndereco':'CliEndereco',
                 'CliNumero':'CliNumero',
                 'CliComplemento':'CliComplemento',
                 'CliBairro':'CliBairro',
                 'CliCidade':'CliCidade',
                 'CliEstado':'CliEstado',
                 'CliCEP':'CliCEP',
                 'CliTelefone':'CliTelefone',
                 'NumItens':'NumItens',
                 
                 }


cart_item_mapping = {'ProdDescricao_%s':'ProdDescricao_',
                     'ProdId_%s':'ProdId_',
                     'ProdQuantidade_%s':'ProdQuantidade_',
                     'ProdValor_%s':'ProdValor_',
                     'ProdFrete_%s':'ProdFrete_',
                     'ProdExtras_%s':'ProdExtras_',
                     
                    
                     }

payment_txn_types = ['Pagamento', 'Cartão de Crédito', 'Boleto', 'Pagamento online']

subscription_txn_types = ['subscr-failed', 'subscr-cancel', 'subscr-payment', 
                          'subscr-signup', 'subscr-eot', 'subscr-modify']

dispute_txn_types = ['new_case', 'adjustment']

class CartItem(object):

    ProdDescricao_ = None
    ProdId_ = None
    ProdQuantidade_ = None
    ProdValor_ = None
    ProdFrete_ = None
    ProdExtras_ = None
    
class Notification(DictMixin):
    
    shopping_cart = {}
    mass_payments = {}
    _form_variables = []

    def __init__(self, request = None):
        if request == None:
            return
        self.parse(request)
    
    def __repr__(self):
        return "<Notification at %s>" % id(self)

    # define a read-only dict interface to make it easier to work with upstream
    def __getitem__(self, item):
        return getattr(self, item)
    
    def __setitem__(self, item, value):
        return None
    
    def __delitem__(self, item):
        return None

    def keys(self):
        return self._form_variables
    # end of DictMixin classes

    def _do_parse(self, request, mapping):
        for item in mapping.keys():
            if request.has_key(item):
                self._form_variables.append(mapping[item])
                setattr(self, mapping[item], request[item])
            else:
                setattr(self, mapping[item], None)

    def parse(self, request):
        self._do_parse(request, main_mapping)
        self._parse_cart(request)
        return
        
       
        
     
        
    def _parse_cart(self, request):
        self._form_variables.append('shopping_cart')
        if self.NumItens is not None:
            cartitems = range(1, int(self.NumItens)+1)
        else:
            cartitems = [1,]
        for i in cartitems:
            if request.has_key('ProdId_%s' % i):
                cartkey = request['ProdId_%s' % i]
            else:
                cartkey = "%s" % i
            self.shopping_cart[cartkey] = CartItem()
            for item in cart_item_mapping.keys():
                if request.has_key(item % i):
                    # parse out the shopping cart into each variable
                    setattr(self.shopping_cart[cartkey], cart_item_mapping[item], request[item % i])


 
