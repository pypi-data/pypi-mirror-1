import unittest
from collective.inplacetopicview.tests import base

from Products.CMFCore.utils import getToolByName
from collective.inplacetopicview.browser.twin import Topic

class TestAcquisition(base.TestCase):
    """Test if classic cms is well setup"""

    def afterSetUp(self):
        self.setRoles(['Manager', 'Member'])
        self.folder.invokeFactory("News Item", "mynews", title="My news")
        mynews = self.folder.mynews
        wftool = self.portal.portal_workflow
        wftool.doActionFor(mynews, 'publish')
        self.topic = self.portal.news.aggregator

    def test_url(self):
        view = Topic(self.topic, {})
        news = self.topic.queryCatalog()
        self.assertEqual(len(news),1)
        url = view.url(news[0])
        turl = 'http://nohost/plone/news/aggregator/@@inplace.twin.item?path=/plone/Members/test_user_1_/mynews'
        self.assertEqual(url, turl)

def test_suite():
    """This sets up a test suite that actually runs the tests in the class
    above
    """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestAcquisition))
    return suite
