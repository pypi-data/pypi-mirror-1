from cubicweb.selectors import implements
from cubicweb.sobjects.notification import ContentAddedView

class EventAddedView(ContentAddedView):
    """get notified from new events"""
    __select__ = implements('Event')
    content_attr = 'description'
