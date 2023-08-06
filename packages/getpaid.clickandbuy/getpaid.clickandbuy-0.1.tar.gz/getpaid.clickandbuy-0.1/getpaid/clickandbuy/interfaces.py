from getpaid.core import interfaces
from zope import schema

class IClickAndBuyStandardProcessor(interfaces.IPaymentProcessor):
    """
    Click and Buy Standard Processor
    """

class IClickAndBuyStandardOptions(interfaces.IPaymentProcessorOptions):
    """
    Click and Buy Standard Options
    """
    premium_url = schema.ASCIILine(title = u"premium URL")
    seller_id = schema.Int(title = u"SellerID")
    tm_password = schema.ASCIILine(title = u"TMI-Password")
