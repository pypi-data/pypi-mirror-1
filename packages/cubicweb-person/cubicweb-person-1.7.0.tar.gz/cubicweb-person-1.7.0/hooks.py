from cubicweb.selectors import implements
from cubicweb.sobjects.notification import ContentAddedView

class PersonAddedView(ContentAddedView):
    """get notified from new persons"""
    __select__ = implements('Person')
    content_attr = 'description'
