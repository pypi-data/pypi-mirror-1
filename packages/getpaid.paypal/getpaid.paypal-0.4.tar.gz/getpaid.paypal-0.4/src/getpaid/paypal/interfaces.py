"""
"""

from getpaid.core import interfaces
from zope import schema

from zope.i18nmessageid import MessageFactory
_ = MessageFactory('getpaid.paypal')

class IPaypalStandardProcessor( interfaces.IPaymentProcessor ):
    """
    Paypal Standard Processor
    """

class IPaypalStandardOptions( interfaces.IPaymentProcessorOptions ):
    """
    Paypal Standard Options
    """
    server_url = schema.Choice(
        title = _(u"Paypal Website Payments Server"),
        values = ( "Sandbox", "Production" ),
        )

    merchant_id = schema.ASCIILine( title = _(u"Paypal Id"))
