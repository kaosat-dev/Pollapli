from twisted.internet import reactor, defer
from twisted.enterprise import adbapi
from twistar.registry import Registry
from twistar.dbobject import DBObject
from twistar.dbconfig.base import InteractionBase
from twisted.python import log,failure
from twisted.python.log import PythonLoggingObserver
from doboz_web.core.components.nodes.node import Node


#class ReprapNode(DBObject):
#    BELONGSTO  = ['node']
#    BELONGSTO  = ['environment']
#    def __init__(self,name="node",description="reprap node",type="reprap",*args,**kwargs):
#        DBObject.__init__(self,**kwargs)
#       
#       
#Registry.register(Node, ReprapNode)


class ReprapCapability(DBObject):
    BELONGSTO   = ['node','environment']
    def __init__(self,info="reprapInfo",*args,**kwargs):
        DBObject.__init__(self,**kwargs)
        self.info=info
            
Registry.register(Node, ReprapCapability)