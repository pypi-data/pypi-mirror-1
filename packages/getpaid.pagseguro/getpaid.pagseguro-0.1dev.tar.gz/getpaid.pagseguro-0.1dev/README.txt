GetPaid PagSeguro
=================

GetPaid `PagSeguro`_ is used to do payments using PagSeguro, a brazilian
PayPal like service.

  .. _`PagSeguro`: https://pagseguro.uol.com.br/

Introduction
-------------

1. Configure in the buildout ::

    [buildout]
    parts =
    ...
    getpaid
    
    eggs = 
    ...
    ${getpaid:eggs}
    getpaid.pagseguro
    
    zcml =
    ...
    getpaid.pagseguro
    getpaid.pagseguro-overrides

    [getpaid]
    recipe = getpaid.recipe.release
    addpackages=
    getpaid.pagseguro

2. Setup this as your payment processor in getpaid admin interface (Payment Options) :

3. Last step is to enter your pagseguro email info in Payment Processor
Settings. You may also want to add your generated TOKEN if return functionality 
is desired : 

Enjoy!
