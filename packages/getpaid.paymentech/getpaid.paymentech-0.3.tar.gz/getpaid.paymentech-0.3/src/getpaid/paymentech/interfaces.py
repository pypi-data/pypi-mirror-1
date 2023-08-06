from getpaid.core import interfaces

from zope import schema

class IPaymentechOptions(interfaces.IPaymentProcessorOptions):
    """
    Paymentech options
    """
    server_url = schema.Choice(
        title=u"Paymentech Server URL",        
        values=("Production1",
                "Production2",
                "Test1",
                "Test2",)
        )
    
    merchant_id = schema.ASCIILine( title=u"Merchant Id" )
    #merchant_key = schema.ASCIILine( title=u"Transaction Key" )
    terminal_id = schema.ASCIILine( title=u"Terminal Id" )
    check_cvv2 = schema.Bool( title=u"Double Check the Card Verification Number", default=True)
