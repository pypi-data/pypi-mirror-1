from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getUtility

from Products.PloneGetPaid.interfaces import IGetPaidManagementOptions
from getpaid.core.interfaces import IShoppingCartUtility, IOrderManager
from getpaid.core.order import Order
from getpaid.core import payment

from cPickle import loads, dumps
from AccessControl import getSecurityManager

from getpaid.clickandbuy.clickandbuy import ClickAndBuyStandardProcessor

class ClickAndBuyButtonView(BrowserView):
    """page for click and buy button
    """
    def getButton(self):
        button = ClickAndBuyStandardProcessor(self.context)
        cart_util = getUtility(IShoppingCartUtility)
        cart = cart_util.get(self.context, create=True)
        manage_options = IGetPaidManagementOptions(self.context)

        # we'll get the order_manager, create the new order, and store it.
        order_manager = getUtility(IOrderManager)
        new_order_id = order_manager.newOrderId()
        order = Order()

        order.finance_workflow.fireTransition('create')

        # register the payment processor name to make the workflow handlers happy
        order.processor_id = manage_options.payment_processor

        # registering an empty contact information list
        order.contact_information = payment.ContactInformation()
        order.billing_address = payment.BillingAddress()
        order.shipping_address = payment.ShippingAddress()
        order.order_id = new_order_id

        # make cart safe for persistence by using pickling
        order.shopping_cart = loads(dumps(cart))
        order.user_id = getSecurityManager().getUser().getId()
        order_manager.store(order)

        import ipdb; ipdb.set_trace()

        return button.cart_post_button(order)
