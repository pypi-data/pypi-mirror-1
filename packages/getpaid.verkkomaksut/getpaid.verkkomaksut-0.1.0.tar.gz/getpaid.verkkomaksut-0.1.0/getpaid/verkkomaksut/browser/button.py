from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from Products.PloneGetPaid.browser.checkout import BasePaymentMethodButton

class VerkkomaksutPaymentButton(BasePaymentMethodButton):
    __call__ = ZopeTwoPageTemplateFile("templates/button.pt")
