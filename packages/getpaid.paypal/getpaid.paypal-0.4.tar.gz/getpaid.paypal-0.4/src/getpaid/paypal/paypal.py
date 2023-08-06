"""
"""
from zope import component
from zope import interface

from interfaces import IPaypalStandardOptions
from interfaces import IPaypalStandardProcessor

from config import SITEURL, MERCHANTID

_sites = {
    "Sandbox": "www.sandbox.paypal.com",
    "Production": "www.paypal.com",
    }

class PaypalStandardProcessor( object ):
   
    interface.implements( IPaypalStandardProcessor )

    options_interface = IPaypalStandardOptions

    def __init__( self, context ):
        self.context = context

    def cart_post_button( self, cart ):
        #import pdb;pdb.set_trace()
        options = IPaypalStandardOptions( self.context )
        cartitems = []
        idx = 1
        _button_form = """\
        <form style="display:inline;" action="https://%(site)s/cgi-bin/webscr" method="post">
        <input type="hidden" name="cmd" value="_cart"/>
        <input type="hidden" name="upload" value="1">
        <input type="hidden" name="business" value="%(merchant_id)s"/>
        <input type="hidden" name="currency_code" value="USD"/>
        %(cart)s
        <input type="image" src="http://%(site)s/en_US/i/btn/x-click-but01.gif"
               name="submit"
               alt="Make payments with PayPal - it's fast, free and secure!"/>
        </form>"""
        _button_cart = """
        <input type="hidden" name="item_name_%(idx)s" value="%(itemname)s"/>
        <input type="hidden" name="amount_%(idx)s" value="%(amount)s"/>
        <input type="hidden" name="quantity_%(idx)s" value="%(quantity)s"/>
        """
        
        for item in cart.values():
            v = _button_cart % {"idx": idx,
                                "itemname": item.name,
                                "amount": item.cost,
                                "quantity": item.quantity,}
            cartitems.append(v)
        formvals = {
            "site": SITEURL,
            "merchant_id": MERCHANTID,
            "cart": ''.join(cartitems),
            }
        return _button_form % formvals

    def authorize( self, order, payment ):
        pass