from zope import schema
from zope.interface import Interface
from getpaid.core.interfaces import IPaymentProcessor,IPaymentProcessorOptions
from getpaid.wizard.interfaces import IWizardController
from getpaid.verkkomaksut import VerkkomaksutMessageFactory as _

class IVerkkomaksutProcessor(IPaymentProcessor):
    """
    Verkkomaksut Processor
    """

class IVerkkomaksutOptions(IPaymentProcessorOptions):
    """
    Verkkomaksut Options
    """

    merchant_id = schema.ASCIILine( 
                        title = _(u"Merchant ID"),
                        description = _("Input merchant ID provided by Verkkomaksut."),
                        required=True,
                        )

    merchant_authentication_code = schema.ASCIILine( 
                        title = _(u"Merchant Authentication Code"),
                        description = _("Input marchant authentication code provided by Verkkomaksut."),
                        required=True,
                        )

#class IVerkkomaksutWizardController(IWizardController):
#    """
#    """

### Adapters
class IVerkkomaksutOrderInfo(Interface):
    def __call__():
        """Returns information of order."""

### Utilities
class ILanguageCulture(Interface):
    def __call__(language_bindings):
        """Returns verkkomaksut culture."""
