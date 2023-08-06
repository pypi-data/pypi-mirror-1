from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from Acquisition import aq_inner
from Products.Five.browser import BrowserView
from AccessControl import getSecurityManager

from Products.PloneGetPaid.interfaces import IGetPaidManagementOptions, INamedOrderUtility
from getpaid.core import interfaces
from Products.PloneGetPaid.browser.checkout import CheckoutReviewAndPay
from getpaid.verkkomaksut import VerkkomaksutMessageFactory as _

from zope.interface import implements
from zope.component import adapts, getUtility, getMultiAdapter
from Products.CMFCore.interfaces import ISiteRoot
from getpaid.core.interfaces import IOrderManager, IShoppingCartUtility
from getpaid.verkkomaksut.interfaces import (
                                            IVerkkomaksutProcessor,
                                            IVerkkomaksutOptions,
                                            IVerkkomaksutOrderInfo
                                            )

class VerkkomaksutCheckoutReviewAndPay(CheckoutReviewAndPay):

    template = ZopeTwoPageTemplateFile("templates/checkout-verkkomaksut-pay.pt")
    _next_url = None

    def update( self ):
        siteroot = getToolByName(self.context, "portal_url").getPortalObject()
        manage_options = IGetPaidManagementOptions(siteroot)
        processor_name = manage_options.payment_processor
        order_manager = getUtility(IOrderManager)
        order = self.createOrder()
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
        processor_name = manage_options.payment_processor
        if processor_name == u'Verkkomaksut payment interface':
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
        self.wizard = getMultiAdapter(
                    ( self.context, self.request ),
                    name="getpaid-checkout-wizard"
                    )
        order_manager = getUtility(IOrderManager)
        form = self.request.form
        order_id = form.get('order_id')
        order = order_manager.get(order_id)
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
