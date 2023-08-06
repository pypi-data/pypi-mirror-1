from zope import interface

class IInPlaceTopicView(interface.Interface):
    """Inplacetopicview is a browserview helper"""
    
    def url(item):
        """Return the url in topic view of item"""
