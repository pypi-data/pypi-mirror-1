import Products.PloneGetPaid.browser.portlets.cart
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from getpaid.googlecheckout.browser.button import checkout_button_url
from Products.CMFCore.utils import getToolByName


class Renderer(Products.PloneGetPaid.browser.portlets.cart.Renderer):
    render = ViewPageTemplateFile('../templates/portlet-cart.pt')

    def googleCheckoutButtonUrl(self):
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        return checkout_button_url(portal)

