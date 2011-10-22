import uuid

class Component(object):
    def __init__(self,parent = None):
        self._parent = parent
        self._uid = uuid.uuid4()