import urllib, urllib2
import socket
import transaction

from AccessControl import ClassSecurityInfo
from DateTime.DateTime import DateTime

from persistent.dict import PersistentDict
from persistent.wref import WeakRef

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import ModifyPortalContent

from Products.Archetypes.public import registerType, Schema, BaseBTreeFolder, \
    ComputedField, StringField, \
    ComputedWidget, StringWidget



responderSchema = Schema((
    
    StringField(
        'baseUrl',
        read_permission=ModifyPortalContent,
        language_independent=True,
        widget=StringWidget(
            label='Portal URL',
            description = 'The portal URL used to construct the URL ' \
                'that PayPal IPN should send messages to. This is used ' \
                'to calculate the response URL. If omitted, the current ' \
                'user\'s portal URL will be used.',
        ),
    ),
    
    StringField(
        'adminEmail',
        read_permission=ModifyPortalContent,
        required=True,
        language_independent=True,
        validators=('isEmail',),
        widget=StringWidget(
            label='Shop Administrator\'s Email Address',
            description = 'Shop notification will go to this address.',
        ),
    ),
    
    StringField(
        'responseAction',
        read_permission=ModifyPortalContent,
        language_independent=True,
        default='PayPalIpnListener',
        widget=StringWidget(
            label='Response Action',
            description = 'This provides the suffix of the response URL to '\
                'allow a flexible response action to be defined.',
        ),
    ),
    
    ComputedField(
        'responseUrl',
        read_permission=ModifyPortalContent,
        expression='context.generateResponseUrl()',
        widget=ComputedWidget(
            label='Responder URL',
            description='This is where PayPal IPN will send payment approval ' \
                'messages to. It should point this responder.'
        ),
    ),
    
))


class PayPalIpnResponder(BaseBTreeFolder):
    
    """Listens to messages from PayPal IPN and responds accordingly."""
    
    security = ClassSecurityInfo()
    
    schema = BaseBTreeFolder.schema.copy() + responderSchema.copy()
    
    portal_type = 'PayPalIpnResponder'
    meta_type = 'PayPalIpnResponder'
    archetype_name = 'PayPal IPN Responder'
    
    content_icon = 'undo_icon.gif'
    
    
    def _getPortalUrl(self):
        return (getToolByName(self, 'portal_url'))()
    
    
    def generateResponseUrl(self):
        baseUrl = self.getBaseUrl() or self._getPortalUrl()
        path = self.getPhysicalPath()
        url = baseUrl + '/'.join(path)
        action = self.getResponseAction()
        if action:
            url += '/' + action
        return url
    
    
    security.declareProtected(perms.MANAGE, 'getOrders')
    def getOrders(self):
        
        if hasattr(self, 'ordersRef'):
            ordersRef = getattr(self, 'ordersRef')
        else:
            orders = PersistentDict()
            ordersRef = WeakRef(orders)
            self.ordersRef = ordersRef
        
        return ordersRef()
    
    
    def createOrder(self, cart):
        """Create a new order from a shopping cart. Returns a unique (to this
        responder) random order ID. This ID is used to track the order."""
        
        if hasattr(self, 'ordersRef'):
            ordersRef = getattr(self, 'ordersRef')
        else:
            orders = PersistentDict()
            ordersRef = WeakRef(orders)
            self.ordersRef = ordersRef
        
        orders = self.getOrders()
        
        # keep trying until a order ID is found that doesn't already exist
        while True:
            orderId = generateRandomCode(16)
            if not orders.has_key(orderId):
                break
        
        # store the cart against the order ID
        order = PersistentDict()
        order['id'] = orderId
        now = DateTime()
        order['created'] = now
        order['state'] = 'CREATED'
        # expire this in 7 days
        order['expires'] = now + 7
        order['cart'] = cart.copy()
        
        orders[orderId] = order
        self._p_changed = 1
        
        self.plone_log('new order CREATED; order ID: ' + str(orderId) \
            + '; expires: ' + str(order['expires']))
        self.plone_log('all order IDs: ' + repr(orders.keys()))
        
        return orderId
    
    
    security.declareProtected(perms.MANAGE, 'retrieveOrder')
    def retrieveOrder(self, orderId):
        order = None
        orders = self.getOrders()
        if orders != None:
            if orders.has_key(orderId):
                order = orders[orderId]
        return order
    
    
    security.declareProtected(perms.MANAGE, 'listOrderIds')
    def listOrderIds(self):
        ids = []
        orders = self.getOrders()
        if orders != None:
            ids = orders.keys()
        return ids
    
    
    security.declareProtected(perms.MANAGE, 'purgeOrder')
    def purgeOrder(self, orderId):
        deleted = False
        orders = self.getOrders()
        if orders != None:
            if orders.has_key(orderId):
                del(orders[orderId])
                deleted = True
        return deleted
    
    
    security.declareProtected(perms.MANAGE, 'purgeOrders')
    def purgeOrders(self):
        n = 0
        orders = self.getOrders()
        if orders != None:
            n = len(orders)
            for key in orders.key():
                del(orders[key])
        return n
    
    
    def processPayPalRequest(self, request):
        
        self.plone_log('PayPalIpnResonder:: processing incoming PayPal request')
        
        # get ready to POST back form variables
        
        form = request.form
        params =[(key, form[key]) for key in form.keys() if key != 'cmd']
        params = [('cmd', '_notify-validate')] + params
        paramData = urllib.urlencode(params)
        url = self.GetPaypalUrl()
        
        self.plone_log(
            'PayPalIpnResponder::   Opening URL: ' + repr(url) + ' ... ')
        # TODO: is this dangerous for other products?
        socket.setdefaulttimeout(120)
        try:
            connection = urllib2.urlopen(url, paramData)
        except URLError:
            raise IOError, 'IPN post-back failed'
        self.plone_log('PayPalIpnResponder::   Reading response ... ')
        response = connection.read()
        self.plone_log('PayPalIpnResponder::   Response: ' + repr(response))
        connection.close()
        
        # convert params into an easy to use dictionary:
        newParams = {}
        for (key, value) in params:
            newParams[key] = value
        params = newParams
        
        if response == 'VERIFIED':
            self._handleVerifiedPayPayRequest(response, params)
        elif response == 'INVALID':
            self._handleInvalidPayPayRequest(response, params)
        else:
            self._handleUnknownPayPayRequest(response, params)
            
        self.previousPayPalTransactionId = params['txn_id']
    
    
    def _handleVerifiedPayPayRequest(self, response, params):
        
        txnId = params['txn_id']
        self.plone_log('PayPalIpnResonder:: request VERIFIED; txn_id=' + txnId)
        
        
        # 1. VERIFY THE PAYMENT DETAILS, AS PER PAYPAL'S "ORDER MANAGEMENT
        # INTEGRATION GUIDE" CHAPTER 3, SECTION "IPN NOTIFICATION
        # VALIDATION: PREVENTING FRUAD"
        
        
        # 1 (a) "Check that the payment_status is Completed." ...
        
        status = params['payment_status']
        if status != 'Completed':
            # payment not confirmed yet - nothing to do
            self.plone_log('valid IPN response "' + status \
                + '" - ignoring; txn_id=' + txnId)
            return
        
        # 1 (b) "check the txn_id against the previous PayPal transaction 
        # you have processed to ensure it is not a duplicate" ...
        
        previousTxnId = \
            getattr(self, 'previousPayPalTransactionId', None)
        if txnId == previousTxnId:
            # duplicate - nothing to do
            self.plone_log(
                'valid IPN response duplicate txn_id - ignoring; txn_id=' \
                    + txnId)
            return
        
        # 1 (c) "make sure the receiver_email is an email address registered 
        # in your PayPal account" ...
        
        ourAccount = self.GetPayPalUserName()
        if ourAccount != params['receiver_email']:
            self._handleSuspiciousPayPayRequest(
                response, params, 'invalid seller PayPal email address')
            return
        
        # 1 (d) Check that the price, mc_gross, and currency, mc_currency, 
        # are correct for the item, item_name or item_number" ...
        
        orderId = params['invoice']
        order = self.retrieveOrder(orderId)
        if order == None:
            self._handleSuspiciousPayPayRequest(
                response, params, 'no such order; order ID: ' + orderId)
            return
        if params['mc_currency'] != 'GBP':
            self._handleSuspiciousPayPayRequest(
                response, params, 'currency mismatch: ' + params['mc_currency'])
            return
        cart = order['cart']
        ourPrice = cart.getSalesPriceTotal()
        reportedPrice = params['mc_gross']
        salesPriceDifference = float(ourPrice) - float(reportedPrice)
        # tolerate one cent of difference to alow for any rounding errors
        if abs(salesPriceDifference) > 0.01:
            self._handleSuspiciousPayPayRequest(
                response, params,'price mismatch: ours=' + str(ourPrice) + \
                    ' vrs. theirs=' + str(reportedPrice))
            return
        
        # 1 (e) "Check the the shared secret returned to you is correct." - we
        # use post-back, so there is no shared secret .. nothing to do
        
        
        # 2. CREATE PROTECTED BUNDLE OF DOWNLOADABLES
        
        
        if order['state'] != 'CREATED':
            # already processed - nothing to do
            self.plone_log('order already in state "' + order['state'] \
                + '" - ignoring; txn_id=' + txnId)
            return
        
        order['state'] = 'PAID'
        self.plone_log('order PAID; order ID: ' + str(orderId) \
            + '; expires: ' + str(order['expires']))
        
        # expire this in 30 days
        self.plone_log(
            'validation PASSED - proceeding with packaging; txn_id=' + txnId)
        order['expiry'] = DateTime() + 30
        
        cart.setCartContext(self)
        contentUids = set([])
        for item in cart.getProductItems():
            product = item.getCommodity()
            # TODO: what do we do if this product has disappeared?
            if isinstance(product, DownloadableProduct):
                moreContent = set(product.getRawVirtualContent())
                contentUids = contentUids.union(moreContent)
        
        addMethod = self.manage_addProduct['paypalIPN']
        bundleId = self.generateUniqueId(type_name='bundle')
        addMethod.addProtectedContent(bundleId)
        bundle = self[bundleId]
        self.plone_log('bundle ID: ' + str(bundleId))
        bundle.setContent(tuple(contentUids))
        bundle.setExpirationDate(DateTime() + 4)
        
        order['state'] = 'PACKAGED'
        self.plone_log('order PAID; order ID: ' + str(orderId) \
            + '; expires: ' + str(order['expires']))
        
        # commit the transaction before moving on the the notification
        # phase
        
        transaction.commit()
        
        
        # 3. EMAIL ACCESS DETAILS TO CUSTOMER
        
        
        bundleUrl = bundle.absolute_url() + '?code=' + bundle.getAccessCode()
        
        subject = 'online order PAID (order ID: ' + str(orderId) + ')'
        message = """
            An order of online items has been paid for: 
            %s
        """ % bundleUrl
        self._sendEmail(message, None, subject)
        
        customerAddress = params['payer_email']
        subject = 'online order ready (order ID: ' + str(orderId) + ')'
        message = """
            Your order of online items is ready to be picked
            up from our website. Please use this link to collect
            your items: 
            %s
        """ % bundleUrl
        self._sendEmail(message, customerAddress, subject)
        
        order['state'] = 'DELIVERED'
    
    
    def _handleInvalidPayPayRequest(self, response, params):
        # TODO: treat as suspicious .. this should haver no effect
        # on the order
        self._handleSuspiciousPayPayRequest(
            params, 'PayPal response returned "INVALID"')
    
    
    def _handleUnknownPayPayRequest(self, response, params):
        # TODO: treat as suspicious .. this should haver no effect
        # on the order
        self._handleSuspiciousPayPayRequest(
            params, 'unknown PayPal response: "' + response + '"')
    
    
    def _handleSuspiciousPayPayRequest(self, params, reason):
        
        # TODO: treat as suspicious .. this should haver no effect
        # on the order though
        
        txnId = params['txn_id']
        message = 'WARNING!!! A suscipicous PayPal IPN response was ' \
            'received; This might be a hacker trying to steal goods or ' \
            'money. txn_id=' + txnId + '; reason: ' + reason
        self.plone_log(message)
        
        message += "\NRESPONSE PARAMETERS:\n"
        for (key, param) in params:
            message += str(key) + ' -> ' + str(param) + "\n"
            
        self._sendEmail(message, None, 'WARNING!!! Suscpicous PayPal activity')
    
    
    def _sendEmail(self, message, recipientAddress, subject):
        
        if recipientAddress == None:
            recipientAddress = self.getAdminEmail()
        
        portal_url = getToolByName(self, 'portal_url') 
        portal = portal_url.getPortalObject() 
        sender = portal.getProperty('email_from_name')
        senderAddress = portal.getProperty('email_from_address')
        senderAddress = sender + '<' + senderAddress + '>'
        
        mailHost = getToolByName(self, 'MailHost')
        self.plone_log('sending email to: ' + recipientAddress + ' ...')
        mailHost.secureSend(message, recipientAddress, senderAddress, subject)
        self.plone_log('    .... sent.')


registerType(PayPalIpnResponder)
