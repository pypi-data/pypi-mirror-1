from Acquisition import aq_inner
from Products.Five import BrowserView
from zope.app.component.hooks import getSite
from zope.component import getMultiAdapter
from Products.CMFCore.utils import getToolByName


class Topic(BrowserView):
    """Lets render the target throw aquisition"""

    def url(self, item):
        """take something with context (self) and a physical path as a
        tuple, return the relative path for the portal"""
        context_url = ""
        putils = getToolByName(self.context, 'plone_utils')
        if putils.isDefaultPage(self.context):
            context_url = self.context.aq_inner.aq_parent.absolute_url()
        else:
            context_url = self.context.absolute_url()
        item_url = item.getURL()
        portal_url = getToolByName(self.context, 'portal_url')()
        result_url = context_url + item_url[len(portal_url):]
        return result_url

    def test(self, a, b , c):
        if a:
            return b
        return c

#Page already exists in Plone