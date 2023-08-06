from zope.interface import implements
from zope.component import adapts
from Products.CMFCore.interfaces import ISiteRoot
from getpaid.core.interfaces import keys
from getpaid.verkkomaksut.interfaces import IVerkkomaksutProcessor, IVerkkomaksutOptions, IVerkkomaksutOrderInfo

from urllib import urlencode#, urlopen
from urllib2 import urlopen, HTTPSHandler, Request
import md5

class VerkkomaksutProcessor( object ):

    implements(IVerkkomaksutProcessor)
    adapts(ISiteRoot)

    options_interface = IVerkkomaksutOptions

    def __init__( self, context ):
        self.context = context

    def capture(self, order, price):
        # always returns async - just here to make the processor happy
        return keys.results_async

    def authorize( self, order, payment ):
        action_url = "https://ssl.verkkomaksut.fi/payment.svm"
        order_info = IVerkkomaksutOrderInfo(order)()
        data = urlencode(order_info)
        request = Request(action_url, data)
#        HTTPSHandler().https_open(request)
#        return keys.results_async
        f = urlopen(request)
        return self.request.response.redirect(f.geturl())
