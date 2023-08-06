from plone.app.iterate.browser.checkout import Checkout as BaseCheckout
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class Checkout(BaseCheckout):
    """ This seems to be the only way to override the template 
        because its set in the base class and so the zcml template directive
        is unusable
    """
    template = ViewPageTemplateFile('checkout.pt')


