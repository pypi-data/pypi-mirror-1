from Products.PloneGetPaid.browser.cart import ShoppingCartActions
from Products.PloneGetPaid.interfaces import IGetPaidManagementOptions
from getpaid.core.interfaces import IPaymentProcessor, IShoppingCartUtility
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from Products.CMFCore.utils import getToolByName
from zope.component import getAdapter, getUtility

class Actions(ShoppingCartActions):

    template = ZopeTwoPageTemplateFile('templates/cart-actions.pt')
    
    def render(self):
        cart_utility = getUtility(IShoppingCartUtility)
        html = self.template()
        cart_utility.destroy(self.context)
        return html

    def actionsOtherThanCheckout(self):
        return [action for action in self.availableActions()
                if action.label != 'Checkout']

    def doesHaveActions(self):
        return len(self.availableActions()) > 0
    
    def buyNowButton(self):
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        cart = getUtility(IShoppingCartUtility).get(self.context, create=True)
        manage_options = IGetPaidManagementOptions(portal)
        processor_name = manage_options.payment_processor
        processor = getAdapter(portal, IPaymentProcessor, processor_name)
        return processor.cart_post_button(cart)
