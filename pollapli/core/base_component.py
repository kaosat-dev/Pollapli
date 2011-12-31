import uuid


class BaseComponent(object):
    """Basic component, usually 'oldest' ancestor of most classes"""
    def __init__(self, parent=None):
        self._parent = parent
        self.cid = uuid.uuid4()
