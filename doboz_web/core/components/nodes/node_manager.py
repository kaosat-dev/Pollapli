"""
.. py:module:: node_manager
   :synopsis: manager of nodes : handles global list of available node typesas well as the individual nodes it contains
"""
import logging
import uuid
from twisted.internet import reactor, defer
from twisted.enterprise import adbapi
from twistar.registry import Registry
from twistar.dbobject import DBObject
from twistar.dbconfig.base import InteractionBase
from twisted.python import log,failure
from twisted.python.log import PythonLoggingObserver


from doboz_web.core.components.nodes.node import Node
from doboz_web.core.tools.wrapper_list import WrapperList
from doboz_web.exceptions import UnknownNodeType,NodeNotFound

from doboz_web.core.components.nodes.hardware.reprap.reprap_capability import ReprapCapability
from doboz_web.core.components.nodes.hardware.dummy_capability import DummyCapability


class NodeManager(object):
    """
    Class for managing nodes: works as a container, a handler
    and a central managment point for the list of avalailable nodes
    (for future plugin based system)
    """
    nodeTypes={}
    nodeTypes["reprap"]=ReprapCapability
    nodeTypes["dummy"]=DummyCapability
    #nodeTypes["webcam"]=WebcamNode
   # nodeTypes["node"]=Node #this is just a dummy node as it is a base class
    
    
    def __init__(self,parentEnv):
        self.logger=log.PythonLoggingObserver("dobozweb.core.components.nodes.nodeManager")
        self.parentEnv=parentEnv
        self.nodes={}
        self.lastNodeId=0
        
     
    @defer.inlineCallbacks    
    def setup(self):
        
        @defer.inlineCallbacks
        def addNode(nodes,nodeTypes):
            for node in nodes:
                node.environment.set(self.parentEnv)
                self.nodes[node.id]=node
               
                yield node.setup()
                for capability in nodeTypes.values():   
                    def addCapabilities(caps,node):
                        if len(caps)>0:
                            node.capability=caps[0] 
                    capability.find(where=['node_id = ?', node.id]).addCallback(addCapabilities,node)
            
                
        yield Node.all().addCallback(addNode,self.nodeTypes)
        defer.returnValue(None)
        
    """
    ####################################################################################
    The following are the "CRUD" (Create, read, update,delete) methods for the general handling of nodes
    """
    @defer.inlineCallbacks
    def add_node(self,name="node",description="",type=None,connector=None,driver=None,*args,**kwargs):
        """
        Add a new node to the list of nodes of the current environment
        Params:
        name: the name of the node
        Desciption: short description of node
        type: the type of the node : very important , as it will be used to instanciate the correct class
        instance
        Connector:the connector to use for this node
        Driver: the driver to use for this node's connector
        """
            
        if type in self.nodeTypes.iterkeys():
            node= yield Node(name,description,type).save()
            node.environment.set(self.parentEnv)
            self.nodes[node.id]=node
            capability= yield NodeManager.nodeTypes[type](name,description).save()
            capability.node.set(node)
            node.capability=capability
            
            log.msg("Added  node ",name," of capability ",type," with id set to ",str(node.id), logLevel=logging.CRITICAL)
            defer.returnValue(node)
        else:
            log.msg("unknown node type",logLevel=logging.CRITICAL)
            raise(UnknownNodeType())
        defer.returnValue(None)
    
    def get_nodes(self,filter=None):
        """
        Returns the list of nodes, filtered by  the filter param
        the filter is a dictionary of list, with each key beeing an attribute
        to check, and the values in the list , values of that param to check against
        """
        d=defer.Deferred()
        
        def filter_check(node,filter):
            for key in filter.keys():
                if not getattr(node, key) in filter[key]:
                    return False
            return True
      
        def get(filter,nodesList):
            if filter:
                return WrapperList(data=[node for node in nodesList if filter_check(node,filter)],rootType="nodes")
            else:               
                return WrapperList(data=nodesList,rootType="nodes")
            
        d.addCallback(get,self.nodes.values())
        reactor.callLater(0.5,d.callback,filter)
        return d
    
    def get_node(self,id):
        if not id in self.nodes.keys():
            raise NodeNotFound()
        return self.nodes[id]
    
    def update_node(self,id,name,description):
        """Method for node update"""
        print("updating node")
        return self.nodes[id]
        #self.nodes[id].update()
    
    def delete_node(self,id):
        """
        Remove a node : this needs a whole set of checks, 
        as it would delete an node completely 
        Params:
        id: the id of the node
        """
        d=defer.Deferred()
        def remove(id,nodes):
            nodeName=nodes[id].name
            nodes[id].delete()
            del nodes[id]
            log.msg("Removed node ",nodeName,"with id ",id,logLevel=logging.CRITICAL)
        d.addCallback(remove,self.nodes)
        reactor.callLater(0,d.callback,id)
        return d
            
    @defer.inlineCallbacks
    def clear_nodes(self):
        """
        Removes & deletes ALL the nodes, should be used with care
        """
        for node in self.nodes.values():
            yield self.delete_node(node.id)        
        defer.returnValue(None)
   
    """
    ####################################################################################
    Helper Methods    
    """
        
    def set_driver(self,nodeId,**kwargs):
        """Method to set a nodes connector's driver 
        Params:
        nodeId: the id of the node
        WARNING: cheap hack for now, always defaults to serial
        connector
        """
        #real clumsy, will be switched with better dynamic driver instanciation
        driver=None
        if kwargs["type"]== "teacup":
            del kwargs["type"]
            driver=TeacupDriver(**kwargs)
        elif kwargs["type"]=="fived":
            del kwargs["type"]
            driver=FiveDDriver(**kwargs)
        if driver:
            self.nodes[nodeId].connector.set_driver(driver)  
            self.logger.critical("Set driver for connector of node %d with params %s",nodeId,str(kwargs))
        else:
            raise Exception("unknown driver ")
        
    def start_node(self,nodeId,**kwargs):
        self.nodes[nodeId].start(**kwargs)
        
    def stop_node(self,nodeId):
        self.nodes[nodeId].stop()
    
    