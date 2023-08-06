from cubicweb.selectors import implements
from cubicweb.sobjects.notification import ContentAddedView

class TaskAddedView(ContentAddedView):
    """get notified from new tasks"""
    __select__ = implements('Task')
    content_attr = 'description'
