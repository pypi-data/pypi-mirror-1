from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from Acquisition import aq_inner
from Products.Five.browser import BrowserView
from AccessControl import getSecurityManager
from Products.PloneGetPaid.interfaces import IGetPaidManagementOptions, INamedOrderUtility
from Products.PloneGetPaid.browser.checkout import CheckoutReviewAndPay
from zope.component import getUtility, getMultiAdapter
from getpaid.core.interfaces import IOrderManager, IShoppingCartUtility
from getpaid.verkkomaksut.interfaces import IVerkkomaksutOptions, IVerkkomaksutOrderInfo
import md5

class VerkkomaksutCheckoutReviewAndPay(CheckoutReviewAndPay):

    template = ZopeTwoPageTemplateFile("templates/checkout-verkkomaksut-pay.pt")
    _next_url = None

    def update( self ):
        siteroot = getToolByName(self.context, "portal_url").getPortalObject()
        manage_options = IGetPaidManagementOptions(siteroot)
        order_manager = getUtility(IOrderManager)
        order = self.createOrder()
        properties = getToolByName(siteroot, 'portal_properties')
        try:
            processors = properties.payment_processor_properties.enabled_processors
            processor = u'Verkkomaksut Processor'
            if processor in processors:
                order.processor_id = processor
        except AttributeError:
            processor_name = manage_options.payment_processor
            order.processor_id = processor_name
        order.finance_workflow.fireTransition( "create" )
        order_manager.store(order)
        super( CheckoutReviewAndPay, self).update()

    def is_verkkomaksut(self):
        """
        Returns true if payment processor is verkkomaksut.
        """
        siteroot = getToolByName(self.context, "portal_url").getPortalObject()
        manage_options = IGetPaidManagementOptions(siteroot)
        properties = getToolByName(siteroot, 'portal_properties')
        processor = u'Verkkomaksut Processor'
        try:
            processors = properties.payment_processor_properties.enabled_processors
            if processor in processors:
                return True
            else:
                return False
        except AttributeError:
            processor_name = manage_options.payment_processor
            if processor_name == processor:
                return True
            else:
                return False

    def verkkomaksut_options(self):
        context= aq_inner(self.context)
        return IVerkkomaksutOptions(context)

    def order_info(self):
        order = self.createOrder()
        return IVerkkomaksutOrderInfo(order)()

class VerkkomaksutThankYou(BrowserView):

    template = ZopeTwoPageTemplateFile("templates/checkout-thank-you.pt")

    def __call__(self):
        form = self.request.form
        return_authcode = form.get('RETURN_AUTHCODE') or ''
        order_number = form.get('ORDER_NUMBER') or ''
        timestamp = form.get('TIMESTAMP') or ''
        paid_transaction_id = form.get('PAID') or ''
        site = getToolByName(self.context, "portal_url").getPortalObject()
        options = IVerkkomaksutOptions(site)
        merchant_hash = options.merchant_authentication_code
        m = md5.new()
        m.update(order_number)
        m.update('&' + timestamp)
        m.update('&' + paid_transaction_id)
        m.update('&' + merchant_hash)
        auth_code = m.hexdigest()
        AUTH_CODE = auth_code.upper()
        if AUTH_CODE != return_authcode:
            base_url = site.absolute_url()
            return self.request.response.redirect('%s/@@verkkomaksut-cancelled-declined' % (base_url,))
        else:
            self.wizard = getMultiAdapter(
                        ( self.context, self.request ),
                        name="getpaid-checkout-wizard"
                        )
            order_manager = getUtility(IOrderManager)

            order = order_manager.get(order_number)
            self.finance_state = "CHARGED"
            if order.finance_workflow.state().getState() == "CHARGED":
                getUtility(IShoppingCartUtility).destroy( self.context )
                return self.template()
            else:
                order.finance_workflow.fireTransition("authorize")
                template_key = 'order_template_entry_name'
                order_template_entry = self.wizard.data_manager.get(template_key)
                del self.wizard.data_manager[template_key]
                # if the user submits a name, it means he wants this order named
                if order_template_entry:
                    uid = getSecurityManager().getUser().getId()
                    if uid != 'Anonymous':
                        named_orders_list = getUtility(INamedOrderUtility).get(uid)
                        if order_template_entry not in named_orders_list:
                            named_orders_list[order.order_id] = order_template_entry
                order.finance_workflow.fireTransition("charge-charging")
                getUtility(IShoppingCartUtility).destroy( self.context )
                return self.template()
