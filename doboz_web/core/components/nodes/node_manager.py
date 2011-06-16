"""
.. py:module:: node_manager
   :synopsis: manager of nodes : handles global list of available node types
   as well as the individual nodes it contains
"""
import logging
import uuid

from doboz_web.core.components.nodes.hardware.reprap.reprap_node import ReprapNode
from doboz_web.core.components.nodes.hardware.webcam.webcam_node import WebcamNode
from doboz_web.core.components.connectors.hardware.serial.serial_plus import SerialPlus
from doboz_web.core.components.drivers.reprap.Teacup.teacup_driver import TeacupDriver
from doboz_web.core.components.drivers.reprap.FiveD.fived_driver import FiveDDriver


class NodeManager(object):
    """
    Class for managing nodes: works as a container, a handler
    and a central managment point for the list of avalailable nodes
    (for future plugin based system)
    """
    nodeTypes={}
    nodeTypes["reprap"]=ReprapNode
    nodeTypes["webcam"]=WebcamNode
    
    
    def __init__(self):
        self.logger=logging.getLogger("dobozweb.core.components.nodes.nodeManager")
        #self.nodes={}#dictionary of list of nodes, by nodeType
        self.nodes=[]
        self.lastNodeId=0
    
    def add_node(self,name,type,connector=None,driver=None,*args,**kwargs):
        """each nodeType should have an id, just defaulting to 0 (reprap)
        for now"""
        
        #nodeTypeId=self.nodeTypes[type]
        #self.nodes[nodeTypeId]=[]
        
        node=None
        if type in NodeManager.nodeTypes.iterkeys():
            node=NodeManager.nodeTypes[type](name)
            self.nodes.append(node)
            id=self.nodes.index(node)
            self.nodes[id].id=id
            node.id=id
            self.logger.critical("Added  node %s of type %s with id set to %s",name,type,str(node.id))
            
        else:
            self.logger.critical("unknown node type")
       # node=ReprapNode()
        
       # self.nodes[nodeTypeId].append(node) 
       
    
    def delete_node(self,id):
        """
        Delete a specific node
        """
        nodeId=int(id)
        #self.nodesById[nodeId].stop()
        try:
            del self.nodes[id] 
            self.logger.critical("Removed node with id %d",id)
        except Exception as inst:
            self.logger.error("Error in node deletion: %s ",str(inst))
    
    def clear_nodes(self):
        self.nodesById.clear()
    
    def get_node(self,id):
        return self.nodes[id]
    
    def get_nodes(self):
        """
        Return full list of nodes
        """
        return self.nodes
    
    def set_connector(self,nodeId,*args,**kwargs):
        """Method to set a nodes connector 
        Params:
        nodeId: the id of the node
        WARNING: cheap hack for now, always defaults to serial
        connector
        """
        self.nodes[nodeId].set_connector(SerialPlus())
        self.logger.critical("Set connector of node %d",nodeId)
        print("in connector for node",str(self.nodes[nodeId].connector))
        
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
    
    