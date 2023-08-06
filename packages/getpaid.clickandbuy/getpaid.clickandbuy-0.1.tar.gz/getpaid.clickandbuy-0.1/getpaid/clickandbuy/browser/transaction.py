from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from zope.component import getUtility
from getpaid.core.interfaces import IOrderManager
from persistent.dict import PersistentDict

class Transaction(BrowserView):
    def transaction(self):
        """ click and buy transaction """
        request = self.request
        environ = request.environ
        order_manager = getUtility(IOrderManager)

        cb_linknr = environ.get("HTTP_X_CONTENTID", "") # ClickandBuy Link Number
        cb_price = environ.get("HTTP_X_PRICE", "") # ClickandBuy Price recorded in Millicents !
        if cb_price.isdigit():
            cb_price = str(int(cb_price) / 1000) # Convert Millicent to Cent
        else:
            cb_price = 'nan'
        cb_uid = environ.get("HTTP_X_USERID", "") # ClickandBuy Customer Reference Number
        cb_transaction_id = environ.get("HTTP_X_TRANSACTION", "") # ClickandBuy unique Transaction Reference Number
        cb_currency = environ.get("HTTP_X_CURRENCY", "") # ClickandBuy recorded transaction currency
        cb_ip = environ.get("REMOTE_ADDR", "") # IP Address of the ClickandBuy Web Proxy

        portal_url = getToolByName(self.context, "portal_url").getPortalObject().absolute_url()
        thank_you_page = "%s/@@getpaid-thank-you" % portal_url

        result = True
        reason = ''

        # Defined variables captured via GET
        ext_bdr_id = request.get("externalBDRID")
        if not ext_bdr_id:
            result = False
            reason += "invalid_order_id&"
            order = None
            myprice = None
        else:
            # Get the corresponding order
            order = order_manager.get(ext_bdr_id)

            # Get my price back from the zodb
            myprice = str(int(order.getTotalPrice() * 100))
            myprice = '100'

        # Check ClickandBuy UserID is returned
        if cb_uid in ('', 'nan'):
            result = False
            reason += "cb_uid&"

        # Check communication is from ClickandBuy Web Proxy
        if cb_ip[0: 11] != "217.22.128.":
            result = False
            reason += "cb_ip&"

        # Check ClickandBuy Transaction ID if cb_transaction_id=0 then is it a test purchase made by a user in the free group
        if cb_transaction_id == '0':
            result = False
            reason += "cb_transaction_id&"

        # Check ClickandBuy Price is returned
        if cb_price in ('', 'nan'):
            result = False
            reason += "cb_price1&%s#" % cb_price

        # Check your Price matches ClickandBuy price !!!
        if cb_price != myprice:
            result = False
            reason += "cb_price2=%s#" % cb_price

        # Check that the order has the good workflow in the database and move this workflow one more step
        if result:
            if order.finance_state != 'REVIEWING':
                result = False
                reason += "wrong_workflow_state&" % cb_price
            else:
                # move forward in the workflow
                order.finance_workflow.fireTransition('authorize')

                # save those informations on the order object in the zodb
                order.clickandbuy_data = data =  PersistentDict()
                data['cb_linknr'] = cb_linknr
                data['cb_price'] = cb_price
                data['cb_uid'] = cb_uid
                data['cb_transaction_id'] = cb_transaction_id
                data['cb_currency'] = cb_currency
                data['cb_ip'] = cb_ip

        # Redirect customer to landing page on your website with success or error
        response = request.response
        if result:
            response.redirect(thank_you_page + '?result=success&externalBDRID=%s' % ext_bdr_id)
        else:
            response.redirect(thank_you_page + '?result=error&reason=%s' % reason)
