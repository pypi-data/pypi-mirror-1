from Products.CMFCore.utils import getToolByName
from zope import interface

from interfaces import IClickAndBuyStandardOptions, IClickAndBuyStandardProcessor

from Products.PloneGetPaid.interfaces import IGetPaidManagementOptions
from getpaid.core import interfaces as GetPaidInterfaces


class ClickAndBuyStandardProcessor(object):

    options_interface = IClickAndBuyStandardOptions
    interface.implements(IClickAndBuyStandardProcessor)

    def __init__(self, context):
        self.context = context

    def cart_post_button(self, order):
        price = int(order.getTotalPrice() * 100) # price in Cents
        price = 100
        order_id = order.order_id

        options = IClickAndBuyStandardOptions(self.context)
        siteroot = getToolByName(self.context, "portal_url").getPortalObject()
        manage_options = IGetPaidManagementOptions(siteroot)

        premium_url = options.premium_url

        transaction_url = "https://eu.clickandbuy.com/newauth/%s/@@transaction?price=%s&externalBDRID=%s"
        transaction_url = transaction_url % (premium_url, price, order_id)
        img_url = "https://eu.clickandbuy.com/images/all/logos/powredby_logo_en.gif"
        alt = "Pay with Click and Buy"
        return "<a href='%s'><img src='%s' alt='%s'></a>" % (transaction_url, img_url, alt)

    def capture(self, order, price):
        # always returns async - just here to make the processor happy
        return GetPaidInterfaces.keys.results_async

    def authorize(self, order, payment):
        pass
