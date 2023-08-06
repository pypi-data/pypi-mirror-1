from zope.interface import implements
from zope.component import adapts
from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
import md5
from zope.app.component.hooks import getSite
from zope.component import getUtility
from getpaid.core.order import Order

### For implements.
from getpaid.verkkomaksut.interfaces import IVerkkomaksutOrderInfo

### For call.
from getpaid.verkkomaksut.interfaces import IVerkkomaksutOptions, ILanguageCulture

class VerkkomaksutOrderInfo(object):

    implements(IVerkkomaksutOrderInfo)
    adapts(Order)

    def __init__(self, context):
        self.context = context

    def __call__(self):
        """Returns information of order."""
        site = getSite()
        context = aq_inner(self.context)
        membership = getToolByName(site, 'portal_membership')
        member_id = membership.getAuthenticatedMember().getId()
        order_id = context.order_id
        if member_id:
            customer_id = member_id
        else:
            customer_id = 'anonymous'
        verkkomaksut_price = '%.2f' %(context.getTotalPrice())
        options = IVerkkomaksutOptions(site)
        merchant_id = options.merchant_id
        base_url = site.absolute_url()
#        context.finance_workflow.fireTransition( "create" )
#        state = context.finance_state
        success_url = base_url + '/@@verkkomaksut-thank-you?order_id=%s' %(order_id)
        cancel_url = base_url + '/@@verkkomaksut-cancelled-declined'

        language_tool = getToolByName(site, "portal_languages")
        language_bindings = language_tool.getLanguageBindings()
        language_culture = getUtility(ILanguageCulture)
        culture = language_culture(language_bindings)

        m = md5.new()
        m.update(options.merchant_authentication_code)
        m.update('&' + merchant_id)
        m.update('&' + verkkomaksut_price)
        m.update('&' + order_id)
        m.update('&&' + customer_id)
        m.update('&EUR')
        m.update('&' + success_url)
        m.update('&' + cancel_url)
        m.update('&&4')
        m.update('&' + culture)
        auth_code = m.hexdigest()
        AUTH_CODE = auth_code.upper()
        order_info = {
                        "MERCHANT_ID" : merchant_id,
                        "AMOUNT" : verkkomaksut_price,
                        "ORDER_NUMBER" : order_id,
                        "ORDER_DESCRIPTION" : customer_id,
                        "CURRENCY" : "EUR",
                        "RETURN_ADDRESS" : success_url,
                        "CANCEL_ADDRESS" : cancel_url,
#                        "NOTIFY_ADDRESS" : "http://www.esimerkki.fi/notify",
                        "TYPE" : "4",
                        "CULTURE" : culture,
                        "AUTHCODE" : AUTH_CODE,
                        }
        return order_info
