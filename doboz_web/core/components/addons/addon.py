from twisted.internet import reactor, defer
from twisted.python import log,failure
from twisted.python.log import PythonLoggingObserver

class AddOn(object):
    def __init__(self,name="addOn",description="add on",path="",*args,**kwargs):
        #DBObject.__init__(self,**kwargs)
        self.enabled=True
        self.name=name
        self.description=description
        self.path=path
        
    def _toDict(self):
        return {"AddOn":{"name":self.name,"description":"","active":self.enabled,"path":self.path}}