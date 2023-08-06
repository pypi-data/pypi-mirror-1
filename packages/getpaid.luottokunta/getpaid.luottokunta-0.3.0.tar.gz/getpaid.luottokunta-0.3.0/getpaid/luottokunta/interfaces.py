from zope import schema
from zope.interface import Interface
from getpaid.core.interfaces import IPaymentProcessor,IPaymentProcessorOptions
from getpaid.luottokunta import LuottokuntaMessageFactory as _

class ILuottokuntaProcessor(IPaymentProcessor):
    """
    Luottokunta Processor
    """

class ILuottokuntaOptions(IPaymentProcessorOptions):
    """
    Luottokunta Options
    """

    merchant_number = schema.ASCIILine( 
                        title = _(u"Merchant Number"),
                        description = _("Input merchant ID provided by Luottokunta."),
                        required=True,
                        )

    card_details_transmit = schema.Bool(
                        title = _(u"Card Details Transmit"),
                        description = _("If card details are entered at this plone site, check this option. If at Luottokunta's page, leave this blank."),
                        required=False,
                        )

    transaction_type = schema.Bool(
                        title = _(u"Transaction Type"),
                        description = _(u"If money receiver pays the provision to Luottokunta, check this option. If payer pays it, leave this blank."),
                        required=False,
                        )

    use_dossier_id = schema.Bool(
                        title = _(u"Use Dossier ID"),
                        description = _(u"Dossier ID is only for travel agencies and airlines. Check this option if Dossier ID is used to the card transactions, else leave this blank."),
                        required=False,
                        )

    dossier_id = schema.ASCIILine(
                        title = _(u"Use Dossier ID"),
                        description = _(u""),
                        required=False,
                        )

    use_authentication_mac = schema.Bool(
                        title = _(u"Use Authentication MAC"),
                        description = _(u"If authentication MAC is used to the card transactions, check this option, else leave this blank."),
                        required=False,
                        )

    authentication_mac = schema.ASCIILine( 
                        title = _(u"Authentication MAC"),
                        description = _("Input merchant's authentication MAC provided by Luottokunta. Remember to allow MAC authentication at Luottokunta's administration page!!"),
                        required=False,
                        )

#    allow_amex = schema.Bool(
#                        title = _(u"American Express"),
#                        description = _(u"If you allow AMEX as an payment method, check this option. Remember to read usage of AMEX located in Luottokunta's administaration page."),
#                        required=False,
#                        )

    use_incremental_order_id = schema.Bool(
                        title = _(u"Use Incremenatal Order Number"),
                        description = _(u"Check this option to use incremental order ID for Luottokunta interface. Remember to input numeric order ID to the next order ID field."),
                        required=False,
                        )

    next_order_id = schema.Int( 
                        title = _(u"Next Order ID"),
                        description = _("Input order ID for the next order. This order ID will be used only for Luottokunta interface. You see getpaid order ID in the customer ID column in Luottokunta interface."),
                        required=False,
                        default=1,
                        )

### Adapters
class ILuottokuntaOrderInfo(Interface):
    def __call__():
        """Returns information of order."""

### Utilities
class ILuottokuntaLanguage(Interface):
    def __call__():
        """Returns Language variable."""

class IDecimalPrice(Interface):
    def __call__():
        """Returns decimal price."""
