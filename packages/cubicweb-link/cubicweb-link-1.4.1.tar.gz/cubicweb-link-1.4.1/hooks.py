from cubicweb.selectors import implements
from cubicweb.sobjects.notification import ContentAddedView

class LinkAddedView(ContentAddedView):
    """get notified from new links"""
    __select__ = implements('Link')
    content_attr = 'description'
