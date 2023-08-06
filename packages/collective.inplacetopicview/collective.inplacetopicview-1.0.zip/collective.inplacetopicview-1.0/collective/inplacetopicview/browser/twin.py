from Acquisition import aq_inner
from Products.Five import BrowserView
from BeautifulSoup import BeautifulSoup
from zope.app.component.hooks import getSite
from zope.component import getMultiAdapter
from Products.CMFCore.utils import getToolByName
from zope import interface
from collective.inplacetopicview.browser.interfaces import IInPlaceTopicView

class Item(BrowserView):
    """Lets render the targeted content and the context and place target 
    under the rendered context"""

    def __call__(self, *args):
        """mytopic/@@inplacetopicview.html?path=relative/path
        """
        context = aq_inner(self.context)
        path = self.request.get('path',None)
        portal_url = getToolByName(context, 'portal_url')

        current_html = context()
        orig_soup = BeautifulSoup(current_html)
        orig_div = orig_soup.find('div', attrs={'id': 'content'})
        if orig_div is None:
            orig_div = orig_soup.find('div',
                                      attrs=dict({'id': 'region-content'}))


        if path is not None:
            content = None
            site = getSite()
            relative_path = '/'.join(self.getRelPath(path.split('/')))
            content = site.restrictedTraverse(relative_path)
            html = content() #TODO: get the current view (cf bda.proxy)
            soup = BeautifulSoup(html)
            div = soup.find('div', attrs={'id': 'content'})
            if div is None:
                div = soup.find('div', attrs=dict({'id': 'region-content'}))
            orig_div.replaceWith(div)

            return str(orig_soup)

        else:
            return current_html

    def getRelPath(self, ppath):
        """take something with context (self) and a physical path as a
        tuple, return the relative path for the portal"""
        urlTool = getToolByName(self.context, 'portal_url')
        portal_path = urlTool.getPortalObject().getPhysicalPath()
        ppath = ppath[len(portal_path):]
        return ppath

class Topic(BrowserView):
    
    interface.implements(IInPlaceTopicView)

    def url(self, item):
        item_path = item.getPath()
        return self.context.absolute_url()+'/@@inplace.twin.item?path='+item_path

    def test(self, a, b, c):
        if a:
            return b
        return c
