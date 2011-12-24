import uuid

class BaseComponent(object):
    def __init__(self,parent = None):
        self._parent = parent
        self._id = uuid.uuid4()