# Copyright (c) 2007 ifPeople, Kapil Thangavelu, and Contributors
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

"""
"""
from zope.interface import implements
from zope.component import getUtility

from gchecky import model as gmodel
from gchecky import gxml

from getpaid.core.interfaces  import IShoppingCartUtility
from getpaid.googlecheckout.interfaces import IGoogleCheckoutOptions
from getpaid.googlecheckout.interfaces import IGoogleCheckoutProcessor
from getpaid.googlecheckout.interfaces import IGoogleCheckoutController
from getpaid.googlecheckout.interfaces import IGoogleCheckoutShipping

from cgi import escape


def gcart_item(entry, options):
    return gmodel.item_t(
        name = entry.name,
        description = entry.description,
        unit_price = gmodel.price_t(
            value = entry.cost,
            currency = options.currency,
            ),
        quantity = entry.quantity,
        merchant_item_id = entry.product_code,
        )


class GoogleCheckoutProcessor(object):

    implements(IGoogleCheckoutProcessor)

    options_interface = IGoogleCheckoutOptions

    def __init__( self, context ):
        self.context = context
        self._controller = None

    def getController( self ):
        if self._controller is None:
            self._controller = IGoogleCheckoutController(self.context)
        return self._controller

    controller = property(getController)

    def checkout_shopping_cart(self, cart, analytics_data=None):
        options = IGoogleCheckoutOptions(self.context)
        cart_key = getUtility(IShoppingCartUtility).getKey(self.context)
        edit_cart_url = '%s/getpaid-cart' % self.context.absolute_url()
        continue_shopping_url = self.context.absolute_url()
        return gmodel.checkout_shopping_cart_t(
            shopping_cart = gmodel.shopping_cart_t(
                items = [gcart_item(entry, options) for entry in cart.values()],
                merchant_private_data={'cart-key': cart_key},
                ),
            checkout_flow_support = gmodel.checkout_flow_support_t(
                shipping_methods = IGoogleCheckoutShipping(self.context)(cart),
                analytics_data = analytics_data,
                edit_cart_url = edit_cart_url,
                continue_shopping_url = continue_shopping_url,
                ),
            )

    def checkout(self, cart, analytics_data=None):
        checkout_shopping_cart = self.checkout_shopping_cart(cart,
                                                             analytics_data)
        request = checkout_shopping_cart.toxml()
        response = self.controller.send_xml(request)
        __traceback_supplement__ = (TracebackSupplement, request, response)
        return gxml.Document.fromxml(response).redirect_url

    def notify(self, xml):
        __traceback_supplement__ = (NotifyTracebackSupplement, xml)
        return self.controller.receive_xml(xml)




class TracebackSupplement:

    def __init__(self, request, response):
        self.request = request
        self.response = response

    def format_text(self, name):
        value = getattr(self, name)
        return '   - %s:\n      %s' % (name, value.replace('\n', '\n      '))

    def format_html(self, name):
        value = getattr(self, name)
        return '<dt>%s:</dt><dd><pre>%s</pre></dd>' % (name, escape(value))

    def getInfo(self, as_html=0):
        if not as_html:
            return '%s\n%s' % (self.format_text('request'),
                               self.format_text('response'))
        else:
            return '<dl>%s%s</dl>' % (self.format_html('request'),
                                      self.format_html('response'))


class NotifyTracebackSupplement(TracebackSupplement):

    def __init__(self, xml):
        self.xml = xml

    def getInfo(self, as_html=0):
        if not as_html:
            return '%s' % self.format_text('xml')
        else:
            return '<dl>%s</dl>' % self.format_html('xml')

