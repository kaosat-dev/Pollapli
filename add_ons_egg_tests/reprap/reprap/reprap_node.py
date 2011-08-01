from zope.interface import implements
from twisted.plugin import IPlugin
from doboz_web import idoboz_web 
from zope.interface import classProvides
from twisted.python import log,failure
from doboz_web.core.components.nodes.node import Node


class ReprapNode(Node):
    """Class defining the components of the driver for a basic arduino,using attached firmware """
    classProvides(IPlugin, idoboz_web.INode) 
    TABLENAME="nodes"   
    def __init__(self,type="ArduinoExample",name="ReprapNode",description="a reprap node",options={},*args,**kwargs):
        """
        very important : the first two args should ALWAYS be the CLASSES of the hardware handler and logic handler,
        and not instances of those classes
        """
        Node.__init__(self,type,name,description,options,*args,**kwargs)
        